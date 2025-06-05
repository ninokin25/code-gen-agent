import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from gen_code.code_gen_agent.common.constants import AGENT_STATE_KEYS, ROOT_DIR

def generate_test_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Callback function for unit test generation.
    Receives LLM output and saves it as a test file.
    """
    agent_name = callback_context.agent_name
    llm_output_str: Optional[str] = None

    # 1. state から出力を取得試行
    agent_output_key = AGENT_STATE_KEYS.get(agent_name)
    if agent_output_key:
        current_state: Dict[str, Any] = callback_context.state.to_dict()
        if agent_output_key in current_state:
            output_from_state = current_state.get(agent_output_key)
            if isinstance(output_from_state, str) and output_from_state.strip():
                llm_output_str = output_from_state
                print(f"[Callback TestWriter] Retrieved '{agent_output_key}' from state for agent '{agent_name}'.")

    # 2. state にない場合、latest_output から取得試行
    if not llm_output_str:
        print(f"[Callback TestWriter] Output not found or empty in state for agent '{agent_name}'. Trying latest_output.")
        agent_latest_output_content = callback_context.latest_output
        if agent_latest_output_content and agent_latest_output_content.parts:
            # 通常、最初の part にテキスト出力が含まれる
            if hasattr(agent_latest_output_content.parts[0], 'text'):
                text_output = agent_latest_output_content.parts[0].text
                if isinstance(text_output, str) and text_output.strip():
                    llm_output_str = text_output
                    print(f"[Callback TestWriter] Retrieved code from latest_output for agent '{agent_name}'.")
                else:
                    print(f"[Callback TestWriter] latest_output part text is empty or not a string for agent '{agent_name}'.")
            else:
                print(f"[Callback TestWriter] Error: latest_output part does not have 'text' attribute for agent '{agent_name}'.")
        else:
            print(f"[Callback TestWriter] Error: No valid latest_output found for agent '{agent_name}'.")

    if not llm_output_str:
        print(f"[Callback TestWriter] No LLM output found for agent '{agent_name}'. Cannot write test file.")
        return None

    # llm_output_str を使ってコードをパース
    code: Optional[str] = None
    # TestWriterAgent のプロンプトはコードブロックを要求しているので、主に文字列処理
    if isinstance(llm_output_str, str):
        stripped_output = llm_output_str.strip()
        # Markdown形式のコードブロック (例: ```cpp ... ```) を処理
        if stripped_output.startswith("```") and stripped_output.endswith("```"):
            code_lines = stripped_output.split('\n')
            if len(code_lines) > 1 and code_lines[0].startswith("```"): # ```cpp や ```c など言語指定子があっても対応
                code = '\n'.join(code_lines[1:-1]).strip()
            else: # ```code``` のような1行または ```\ncode\n``` の形式
                code = stripped_output[3:-3].strip()
        else:
            # マークダウン形式でない場合、JSONとしてパースを試みる (フォールバック)
            # TestWriterAgentのプロンプトは直接コードを要求しているため、通常はJSONではない想定
            try:
                parsed_json = json.loads(llm_output_str)
                if isinstance(parsed_json, dict):
                    code = parsed_json.get("test_code") or parsed_json.get("source_code") or parsed_json.get("content")
                else: # JSONだが辞書でない場合、元の文字列をコードとして扱う
                    code = llm_output_str
            except json.JSONDecodeError:
                # JSONでもない場合、そのままコードとして扱う
                code = llm_output_str
    # isinstance(llm_output_str, dict) のケースは、stateやlatest_outputから文字列として取得する前提では通常発生しない
    # もし発生する場合は、そのデータ構造に応じた処理が必要

    if not code or not code.strip():
        print(f"[Callback TestWriter] Extracted code is empty for agent '{agent_name}'. Test file not written.")
        return None

    # ファイル書き出し処理 (既存のロジックを流用)
    try:
        test_dir = ROOT_DIR / "examples" / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        # ファイル名はエージェント名や入力に基づいて動的に変更することも検討可能
        test_file = test_dir / f"test_{agent_name.lower().replace('agent', '').replace('writer', '')}.cpp"
        if agent_name == "TestWriterAgent": # より具体的なファイル名
             test_file = test_dir / "test_doorlock_control.cpp"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[Callback TestWriter] Successfully wrote test code from agent '{agent_name}' to {test_file}")

        return types.Content(
            # ADKの慣習に従い、Contentオブジェクトで返す場合はファイルパスやMIMEタイプを指定
            # name=str(test_file), # nameはツール呼び出しの識別子等に使われることがある
            parts=[types.Part(text=f"Test file generated: {test_file}")] # 簡潔なテキストメッセージ
        )
    except IOError as e:
        print(f"[Callback TestWriter] IOError writing test file for agent '{agent_name}': {e}")
        return None
    except Exception as e:
        print(f"[Callback TestWriter] An unexpected error occurred writing test file for agent '{agent_name}': {e}")
        return None
