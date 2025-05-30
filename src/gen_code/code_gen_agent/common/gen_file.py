import os
import re
from typing import Optional, Dict, Any
from functools import partial # functools.partial をインポート

from google.adk.agents.callback_context import CallbackContext
from google.genai import types # Optional: types.Content を返す場合に必要

from gen_code.common.constants import ROOT_DIR
from gen_code.code_gen_agent.common.constants import AGENT_STATE_KEYS

# ヘルパー関数: MarkdownコードブロックからPythonコードを抽出
def _extract_python_code_from_markdown(markdown_code: str) -> str:
    """
    Markdown形式のコードブロックからPythonコードを抽出します。
    "```python\nCODE\n```" または "```\nCODE\n```" という形式を期待します。
    """
    if not isinstance(markdown_code, str):
        return ""

    match_python = re.search(r"^```python\s*(.*?)\s*```$", markdown_code, re.DOTALL | re.IGNORECASE)
    if match_python:
        return match_python.group(1).strip()

    match_generic = re.search(r"^```\s*(.*?)\s*```$", markdown_code, re.DOTALL)
    if match_generic:
        # print("[Callback] Info: Code block extracted without 'python' specifier.")
        return match_generic.group(1).strip()

    # print(f"[Callback] Warning: Could not extract Python code using markdown block syntax from: {markdown_code[:100]}...")
    return ""

def generate_file_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Agent実行後に呼び出されるコールバック関数。
    Agentの出力からPythonコードを抽出し、指定されたファイルパスに書き込みます。
    Agentの出力は state['generated_code'] (Agentのoutput_keyによる) または
    callback_context.latest_output から取得することを試みます。
    Agentの元の出力は変更せず、Noneを返します。
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    current_state: Dict[str, Any] = callback_context.state.to_dict()
    output_filepath = ROOT_DIR / "dist" / f"file_{agent_name.lower()}.py"

    print(f"\n[Callback] In 'generate_file_callback' for agent: {agent_name} (Inv: {invocation_id})")
    print(f"[Callback] Attempting to write generated code to: {output_filepath}")
    print(f"State: {current_state}")

    markdown_code: Optional[str] = None
    agent_output_key = AGENT_STATE_KEYS.get(agent_name)
    # agent_output_key = "generated_code" # デフォルトのoutput_key、必要に応じて変更または動的に取得

    # Agentのoutput_keyに基づいてstateから生成されたコードを取得
    # (Agentごとにoutput_keyが異なる場合は、それを考慮するロジックが必要になるかもしれません)
    if agent_output_key in current_state:
        markdown_code = current_state.get(agent_output_key)
        if markdown_code and isinstance(markdown_code, str):
            print(f"[Callback] Retrieved '{agent_output_key}' from state for agent '{agent_name}'.")
        else:
            markdown_code = None # 無効な場合はリセット

    # stateから取得できなかった場合、または空だった場合は latest_output を試す
    if not markdown_code:
        print(f"[Callback] '{agent_output_key}' not found or empty in state for agent '{agent_name}'. Trying latest_output.")
        agent_latest_output_content = callback_context.latest_output
        if agent_latest_output_content and agent_latest_output_content.parts:
            # 最初のパートにテキストが含まれていると仮定
            markdown_code = agent_latest_output_content.parts[0].text
            if markdown_code and isinstance(markdown_code, str):
                print(f"[Callback] Retrieved code from latest_output for agent '{agent_name}'.")
            else:
                markdown_code = None # 無効な場合はリセット
        else:
            print(f"[Callback] Error: No '{agent_output_key}' in state and no valid latest_output found for agent '{agent_name}'. Cannot write file.")
            return None

    if not markdown_code or not markdown_code.strip():
        print(f"[Callback] Error: Agent '{agent_name}' produced no text content to write. File not written.")
        return None

    python_code = _extract_python_code_from_markdown(markdown_code)

    if not python_code:
        print(f"[Callback] Warning: Could not extract Python code from agent '{agent_name}' output. File will not be written to {output_filepath}.")
        return None

    try:
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"[Callback] Created directory: {output_dir}")

        # 抽出したコードをファイルに書き込み
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(python_code)

        print(f"[Callback] Successfully wrote extracted Python code from agent '{agent_name}' to {output_filepath}")

    except IOError as e:
        print(f"[Callback] IOError writing agent '{agent_name}' output to file {output_filepath}: {e}")
    except Exception as e:
        print(f"[Callback] An unexpected error occurred in 'generate_file_callback' for agent '{agent_name}': {e}")

    # Agentの元の出力は変更しないため、Noneを返す
    return None
