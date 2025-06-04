# /home/user/workspace/code-gen-agent/src/gen_code/code_gen_agent/common/gen_file.py
import os
import re
import json
from typing import Optional, Dict, Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from gen_code.code_gen_agent.common.constants import ROOT_DIR
from gen_code.code_gen_agent.common.constants import AGENT_STATE_KEYS

def _extract_c_code_from_markdown(markdown_code: str) -> str:
    if not isinstance(markdown_code, str):
        return ""
    match_c = re.search(r"^```c\s*(.*?)\s*```$", markdown_code, re.DOTALL | re.IGNORECASE)
    if match_c:
        return match_c.group(1).strip()
    match_generic = re.search(r"^```\s*(.*?)\s*```$", markdown_code, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    return ""

def _extract_specific_codes_from_json_output(json_string: str, header_key: str, source_key: str) -> Dict[str, str]:
    """
    LLMからのJSON形式の出力から指定されたキーでヘッダーとソースコードを抽出します。
    """
    try:
        cleaned_json_string = json_string.strip()
        if cleaned_json_string.startswith("```json"):
            cleaned_json_string = re.sub(r"^```json\s*", "", cleaned_json_string, count=1)
            cleaned_json_string = re.sub(r"\s*```$", "", cleaned_json_string, count=1)
        elif cleaned_json_string.startswith("```"):
            cleaned_json_string = re.sub(r"^```\s*", "", cleaned_json_string, count=1)
            cleaned_json_string = re.sub(r"\s*```$", "", cleaned_json_string, count=1)

        data = json.loads(cleaned_json_string)
        header_content = data.get(header_key, "")
        source_content = data.get(source_key, "")

        if not isinstance(header_content, str) or not isinstance(source_content, str):
            print(f"[Callback] Warning: JSON content for '{header_key}' or '{source_key}' is not a string.")
            return {}
        return {"header": header_content, "source": source_content}
    except json.JSONDecodeError as e:
        print(f"[Callback] Error: Failed to parse JSON output: {e}")
        print(f"[Callback] JSON string (first 200 chars): {json_string[:200]}...")
        return {}
    except Exception as e:
        print(f"[Callback] Error: Unexpected error during JSON parsing: {e}")
        return {}

def _write_code_to_file(filepath: str, code: str, agent_name: str, file_type: str):
    """指定されたパスにコードを書き込むヘルパー関数"""
    try:
        output_dir = os.path.dirname(filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"[Callback] Created directory: {output_dir}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[Callback] Successfully wrote {file_type} from agent '{agent_name}' to {filepath}")
    except IOError as e:
        print(f"[Callback] IOError writing {file_type} from agent '{agent_name}' to {filepath}: {e}")
    except Exception as e:
        print(f"[Callback] An unexpected error occurred writing {file_type} for agent '{agent_name}': {e}")

def generate_file_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state: Dict[str, Any] = callback_context.state.to_dict()

    print(f"\n[Callback] In 'generate_file_callback' for agent: {agent_name} (Inv: {invocation_id})")

    llm_output_str: Optional[str] = None
    agent_output_key = AGENT_STATE_KEYS.get(agent_name)

    if not agent_output_key:
        print(f"[Callback] Error: No output key configured for agent '{agent_name}' in AGENT_STATE_KEYS. Cannot write file.")
        return None

    if agent_output_key in current_state:
        llm_output_str = current_state.get(agent_output_key)
        if isinstance(llm_output_str, str) and llm_output_str.strip():
            print(f"[Callback] Retrieved '{agent_output_key}' from state for agent '{agent_name}'.")
        else:
            llm_output_str = None

    if not llm_output_str:
        print(f"[Callback] '{agent_output_key}' not found or empty in state for agent '{agent_name}'. Trying latest_output.")
        agent_latest_output_content = callback_context.latest_output
        if agent_latest_output_content and agent_latest_output_content.parts:
            if hasattr(agent_latest_output_content.parts[0], 'text'):
                 llm_output_str = agent_latest_output_content.parts[0].text
                 if isinstance(llm_output_str, str) and llm_output_str.strip():
                     print(f"[Callback] Retrieved code from latest_output for agent '{agent_name}'.")
                 else:
                     llm_output_str = None
            else:
                print(f"[Callback] Error: latest_output part does not have text for agent '{agent_name}'.")
                llm_output_str = None
        else:
            print(f"[Callback] Error: No '{agent_output_key}' in state and no valid latest_output found for agent '{agent_name}'. Cannot write file.")
            return None

    if not llm_output_str or not llm_output_str.strip():
        print(f"[Callback] Error: Agent '{agent_name}' produced no text content to write. File not written.")
        return None

    output_base_filename = f"file_{agent_name.lower().replace('agent', '')}"
    output_dir_path = ROOT_DIR / "examples" / "src" / "body_app"

    extracted_codes: Dict[str, str] = {}
    header_key = ""
    source_key = ""
    output_filename_suffix_h = ".h"
    output_filename_suffix_c = ".c"

    if agent_name == "CodeWriterAgent":
        header_key = "header_file_content"
        source_key = "source_file_content"
        extracted_codes = _extract_specific_codes_from_json_output(llm_output_str, header_key, source_key)
    elif agent_name == "CodeRefactorerAgent":
        header_key = "refactored_header_file_content"
        source_key = "refactored_source_file_content"
        output_base_filename = "doorlock_control"
        # output_filename_suffix_h = "_refactored.h"
        # output_filename_suffix_c = "_refactored.c"
        extracted_codes = _extract_specific_codes_from_json_output(llm_output_str, header_key, source_key)
    else:
        print(f"[Callback] Info: Agent '{agent_name}' does not have specific multi-file JSON generation logic in callback. Trying single file markdown extraction.")
        c_code = _extract_c_code_from_markdown(llm_output_str)
        if c_code:
            single_output_filepath = output_dir_path / f"{output_base_filename}.c"
            _write_code_to_file(str(single_output_filepath), c_code, agent_name, "C code file (fallback)")
        else:
            print(f"[Callback] Warning: Could not extract C code using markdown from '{agent_name}' output. File not written.")
        return None

    if not extracted_codes or not extracted_codes.get("source") or not extracted_codes.get("header"):
        print(f"[Callback] Warning: Could not extract header/source code from '{agent_name}' JSON output (keys: '{header_key}', '{source_key}'). Files will not be written.")
        return None

    header_code = extracted_codes["header"]
    source_code = extracted_codes["source"]

    header_filepath = output_dir_path / f"{output_base_filename}{output_filename_suffix_h}"
    source_filepath = output_dir_path / f"{output_base_filename}{output_filename_suffix_c}"

    _write_code_to_file(str(header_filepath), header_code, agent_name, f"{agent_name} header file")
    _write_code_to_file(str(source_filepath), source_code, agent_name, f"{agent_name} source file")

    return None
