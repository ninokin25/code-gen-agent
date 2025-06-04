from typing import Optional, Dict, Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def generate_test_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Callback function for unit test generation.
    Receives LLM output (JSON or code block) and saves it as a test file.
    """
    import os
    import json
    from pathlib import Path

    # Get LLM output
    output = callback_context.llm_output
    if not output:
        return None

    # Parse as code block or JSON
    code = None
    if isinstance(output, dict):
        code = output.get("test_code") or output.get("source_code") or output.get("content")
    elif isinstance(output, str):
        # Remove code block markers
        stripped_output = output.strip()
        if stripped_output.startswith("```") and stripped_output.endswith("```"):
            # Remove the triple backticks and optional language specifier
            code_lines = stripped_output.split('\n')
            if len(code_lines) > 1 and code_lines[0].startswith("```"):
                code = '\n'.join(code_lines[1:-1])
            else:
                code = stripped_output[3:-3].strip()
        else:
            try:
                parsed = json.loads(output)
                code = parsed.get("test_code") or parsed.get("source_code") or parsed.get("content")
            except Exception:
                code = output

    if not code:
        return None

    test_dir = Path("examples/tests")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test_doorlock_control.cpp"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(code)

    # Return as Content type (according to ADK conventions)
    return types.Content(
        name=str(test_file),
        data=code,
        mime_type="text/x-c++src"
    )
