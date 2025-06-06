"""
Common utility functions for agent callbacks in the code generation framework.

This module provides helper functions for:
- Retrieving LLM output from the agent callback context.
- Extracting code from LLM responses (handling markdown and JSON formats).
- Writing extracted code to files.
- A standardized callback for generating test files.

These utilities aim to reduce boilerplate and ensure consistent handling of
common tasks within different agent callback implementations.
"""
import os
import re
import json
from typing import Optional, Dict, Any
from pathlib import Path

# Assuming google.adk.services.action_handler.CallbackContext is the correct path.
# If ADK provides its own CallbackContext in a different module, adjust accordingly.
from google.adk.services.action_handler import CallbackContext
from google.genai import types as genai_types # For callback return type hints

from gen_code.code_gen_agent.common.constants import ROOT_DIR, AGENT_STATE_KEYS

# --- Output Retrieval ---
def get_llm_output_from_context(
    callback_context: CallbackContext,
    agent_output_key: Optional[str] = None
) -> Optional[str]:
    """
    Retrieves the LLM output string from the callback_context.

    It first tries to get the output from `callback_context.state` using the
    provided `agent_output_key`. If `agent_output_key` is not provided,
    or if the key is not found in the state, or if the value in state is not
    a non-empty string, it falls back to `callback_context.latest_output`.

    If `callback_context.latest_output` itself is a string, it's returned.
    If it's a `google.genai.types.Content` object (or similar with 'parts'),
    it attempts to extract text from the first part.

    Args:
        callback_context: The context object provided to the callback by the ADK.
        agent_output_key: The specific key to look for in `callback_context.state`
                          where the agent's output might be stored.

    Returns:
        The LLM output as a string if found and non-empty, otherwise None.
        Prints warnings if retrieval encounters issues.
    """
    if agent_output_key:
        output_from_state = callback_context.state.get(agent_output_key)
        if isinstance(output_from_state, str) and output_from_state.strip():
            print(f"[Callback] Retrieved '{agent_output_key}' from state.")
            return output_from_state
        # Note: The ADK might store complex objects in state. If the raw Content object
        # is stored in state, further checks could be added here, similar to latest_output handling.
        # For now, it assumes state[agent_output_key] is expected to be a string if set.

    latest_output = callback_context.latest_output
    if isinstance(latest_output, str) and latest_output.strip():
        print("[Callback] Retrieved output from latest_output (it was a string).")
        return latest_output

    # Handle cases where latest_output might be a Content object (e.g., from google.genai)
    if hasattr(latest_output, 'parts') and latest_output.parts:
        # Typically, text output is in the first part.
        part = latest_output.parts[0]
        if hasattr(part, 'text'):
            text_output = part.text
            if isinstance(text_output, str) and text_output.strip():
                print("[Callback] Retrieved text from latest_output.parts[0].text.")
                return text_output
            else:
                print("[Callback] Warning: latest_output.parts[0].text is empty or not a string.")
        else:
            print("[Callback] Warning: latest_output.parts[0] does not have a 'text' attribute.")
    else:
        # This case handles if latest_output is None, or not a string, or has no 'parts'.
        print(f"[Callback] Warning: latest_output is not a string and has no processable parts for key '{agent_output_key}'.")

    print(f"[Callback] Warning: Could not retrieve a valid string output for key '{agent_output_key}'.")
    return None

# --- Code Extraction ---
def extract_code_from_markdown(text: str, language: str = "c") -> str:
    """
    Extracts code from a markdown code block.

    It first attempts to find a code block explicitly tagged with the specified
    `language` (e.g., ```c ... ```). If not found, it searches for a generic
    code block (``` ... ```). If no markdown code block is detected (i.e.,
    the text doesn't contain "```"), it returns the original text, stripped.
    This handles cases where the LLM might return raw code without markdown fences.

    Args:
        text: The string potentially containing markdown-formatted code.
        language: The language identifier for the code block (e.g., "c", "cpp", "python").
                  Used to search for language-specific blocks like ```c ... ```.

    Returns:
        The extracted code content as a string. If multiple blocks exist,
        only the first one matching is returned. Returns an empty string if
        a markdown block is found but is empty. Returns the original stripped
        text if no markdown block syntax ("```") is present at all.
    """
    if not isinstance(text, str):
        return "" # Or raise TypeError, but returning "" is safer for callbacks

    # Pattern for specific language (e.g., ```c ... ``` or ```C ... ```)
    # Case-insensitive matching for the language identifier itself.
    lang_pattern = re.compile(r"^```" + re.escape(language) + r"\s*(.*?)```$", re.DOTALL | re.IGNORECASE)
    match_lang = lang_pattern.search(text.strip())
    if match_lang:
        return match_lang.group(1).strip()

    # Generic pattern (e.g., ``` ... ```) if specific language not found or specified differently
    # This is useful if the LLM uses ``` with no lang identifier, or a different one.
    generic_pattern = re.compile(r"^```\s*(.*?)```$", re.DOTALL)
    match_generic = generic_pattern.search(text.strip())
    if match_generic:
        return match_generic.group(1).strip()

    # If no markdown block fences ("```") are found at the start/end of the stripped text,
    # assume the text itself might be raw code.
    # This behavior is chosen to be more robust to LLMs that sometimes forget fences.
    stripped_text = text.strip()
    if not (stripped_text.startswith("```") and stripped_text.endswith("```")):
        # Check if it's not just an empty string or whitespace before returning.
        if stripped_text:
            # print("[Callback] No markdown fences detected, returning original stripped text as code.")
            return stripped_text

    return "" # Return empty if markdown was detected but not parsed (e.g., empty block or only ```)


def extract_json_data(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts data from a JSON string, attempting to clean potential markdown fences.

    The LLM might wrap JSON output in markdown fences (e.g., ```json ... ``` or ``` ... ```).
    This function tries to remove these fences before parsing the JSON.

    Args:
        text: The string potentially containing JSON data, possibly wrapped in
              markdown code fences.

    Returns:
        A dictionary if JSON parsing is successful and the result is a dict.
        None if the input is not a string, if JSON parsing fails, or if the
        parsed JSON is not a dictionary.
        Prints warnings/errors for parsing issues.
    """
    if not isinstance(text, str):
        return None

    cleaned_json_string = text.strip()
    # Remove ```json ... ``` fences
    if cleaned_json_string.startswith("```json"):
        # Remove the opening ```json and any leading whitespace after it
        cleaned_json_string = re.sub(r"^```json\s*", "", cleaned_json_string, count=1)
        # Remove the closing ``` and any trailing whitespace before it
        cleaned_json_string = re.sub(r"\s*```$", "", cleaned_json_string, count=1)
    # Remove generic ``` ... ``` fences if ```json was not present
    elif cleaned_json_string.startswith("```") and cleaned_json_string.endswith("```"):
        # Handles cases like ``` \n { ... } \n ``` by removing first and last ```
        cleaned_json_string = re.sub(r"^```\s*", "", cleaned_json_string, count=1, flags=re.DOTALL)
        cleaned_json_string = re.sub(r"\s*```$", "", cleaned_json_string, count=1, flags=re.DOTALL)

    cleaned_json_string = cleaned_json_string.strip() # Ensure no leading/trailing whitespace after fence removal

    if not cleaned_json_string: # If string becomes empty after stripping fences
        print("[Callback] Warning: JSON string is empty after attempting to remove markdown fences.")
        return None

    try:
        data = json.loads(cleaned_json_string)
        if isinstance(data, dict):
            return data
        else:
            # The LLM might return a JSON list or other primitive type.
            # For code generation contexts, a dictionary is usually expected.
            print(f"[Callback] Warning: JSON data parsed but is not a dictionary. Type: {type(data)}. Content: {str(data)[:100]}")
            return None
    except json.JSONDecodeError as e:
        print(f"[Callback] Error: Failed to parse JSON output: {e}.")
        # Log part of the problematic string for debugging, but be mindful of length.
        # print(f"[Callback] JSON string (approx first/last 100 chars if long): '{cleaned_json_string[:100]}...{cleaned_json_string[-100:]}'")
        return None
    except Exception as e: # Catch any other unexpected errors during parsing
        print(f"[Callback] Error: Unexpected error during JSON parsing: {e}")
        return None

def extract_code_from_llm_output(text: str, language_hint: str = "cpp") -> Optional[str]:
    """
    Extracts code from a potentially complex LLM text output.

    This function employs a multi-step strategy:
    1.  Tries `extract_code_from_markdown` using `language_hint`. If this returns
        a non-empty string that is different from the original input (meaning
        it successfully stripped markdown), that code is returned.
    2.  If markdown extraction doesn't yield a clear result (e.g., returns the
        original text or an empty string when the original was not empty),
        it tries `extract_json_data`.
    3.  If JSON parsing is successful and returns a dictionary, it searches for
        code content under common keys (e.g., "code", "source_code", `language_hint`).
    4.  If neither markdown nor JSON extraction yields code, and the original text
        was not identified as a markdown block by `extract_code_from_markdown`
        (i.e., `extract_code_from_markdown` returned the original text),
        this function returns the original text stripped of whitespace. This
        handles cases where the LLM returns raw code.

    Args:
        text: The LLM output string.
        language_hint: The programming language expected (e.g., "c", "cpp", "python").
                       Used by markdown extraction and as a potential key in JSON.

    Returns:
        The extracted code as a string if found, otherwise None.
        Prints warnings if extraction is ambiguous or fails.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    # 1. Try Markdown extraction with the specific language hint.
    # `extract_code_from_markdown` will return the original text if no fences are found.
    code_from_markdown = extract_code_from_markdown(text, language_hint)

    # If markdown extraction returned something, and it's different from the original text
    # (meaning it actually processed some markdown), or if the original text itself was just a markdown block.
    # Also check if the extracted code is not empty.
    if code_from_markdown.strip():
        # This condition checks if markdown processing actually happened.
        # If text was "```c int main(){} ```", code_from_markdown is "int main(){}".
        # If text was "int main(){}", code_from_markdown is "int main(){}".
        # We want to return early if markdown processing successfully extracted from fences.
        if code_from_markdown != text.strip() or \
           (text.strip().startswith("```") and text.strip().endswith("```")):
            print(f"[Callback] Extracted code via markdown ({language_hint}).")
            return code_from_markdown

    # 2. If markdown didn't yield a distinct result (e.g., raw code was passed through, or it was empty)
    #    try JSON extraction. This is particularly useful if the LLM was asked for JSON.
    json_data = extract_json_data(text)
    if json_data:
        # Common keys for code content in JSON, prioritizing specific ones.
        # Using language_hint as a key can be useful if the prompt asks for e.g. {"cpp": "code..."}
        common_code_keys = ["source_code", "test_code", "generated_code", "code", "content", language_hint]
        for key in common_code_keys:
            content = json_data.get(key)
            if isinstance(content, str) and content.strip():
                print(f"[Callback] Extracted code from JSON via key '{key}'.")
                return content.strip()
        print("[Callback] Warning: Parsed JSON but did not find a known code key with non-empty string content.")

    # 3. Fallback: If the original text was returned by `extract_code_from_markdown`
    #    (meaning no markdown fences were effectively processed) and JSON parsing failed or yielded no code,
    #    it implies the input might be raw code. Return `code_from_markdown` which holds the stripped original text.
    if code_from_markdown.strip(): # This is the (potentially) raw code if markdown/JSON failed
        print("[Callback] No distinct markdown or JSON code extracted, returning original text as code.")
        return code_from_markdown # Which is text.strip() if no markdown fences were found by extract_code_from_markdown

    print("[Callback] Warning: Could not extract usable code using markdown, JSON, or direct text interpretation.")
    return None


# --- File Writing ---
def write_code_to_file(filepath: Path, code: str, agent_name: str, file_type: str):
    """
    Writes the provided code string to the specified filepath.

    It creates the necessary parent directories if they don't exist.
    Handles potential IOErrors during file operations.

    Args:
        filepath: A `pathlib.Path` object representing the full path to the
                  file where the code should be written.
        code: The string containing the code to write.
        agent_name: The name of the agent generating the file (for logging).
        file_type: A descriptive type of the file being written (e.g.,
                   "C header file", "C++ test file") (for logging).
    """
    if not isinstance(filepath, Path):
        print(f"[Callback] Error: filepath must be a Path object. Got: {type(filepath)}")
        # Or raise TypeError
        return
    if not isinstance(code, str):
        print(f"[Callback] Error: code must be a string. Got: {type(code)} for {filepath}")
        # Or raise TypeError
        return

    try:
        output_dir = filepath.parent
        # Create parent directories if they don't exist.
        output_dir.mkdir(parents=True, exist_ok=True)
        # if not output_dir.exists(): # mkdir with exist_ok=True handles this.
        #     print(f"[Callback] Created directory: {output_dir}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[Callback] Successfully wrote {file_type} from agent '{agent_name}' to '{filepath}'")
    except IOError as e:
        print(f"[Callback] IOError writing {file_type} from agent '{agent_name}' to '{filepath}': {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"[Callback] An unexpected error occurred writing {file_type} for agent '{agent_name}' to '{filepath}': {e}")


# --- Test Generation Callback (Moved and Refactored) ---
def generate_test_callback(
    callback_context: CallbackContext
) -> Optional[genai_types.Content]:
    """
    Callback function specifically for generating and writing unit test files.

    This function orchestrates the process:
    1.  Retrieves the LLM's output using `get_llm_output_from_context`.
    2.  Extracts the code (expected to be C++ for tests) using `extract_code_from_llm_output`.
    3.  Constructs a filepath for the test file (e.g., in `examples/tests/`).
    4.  Writes the extracted code to the file using `write_code_to_file`.
    5.  Returns a `google.genai.types.Content` object with a success message,
        as expected by the ADK for callbacks.

    Args:
        callback_context: The context object provided by the ADK.

    Returns:
        A `google.genai.types.Content` object containing a text part with a
        message about the generated file, or None if a critical error occurs
        (e.g., no output key, no LLM output).
    """
    agent_name = callback_context.agent_name
    print(f"\n[Callback TestWriter] In 'generate_test_callback' for agent: {agent_name}")

    agent_output_key = AGENT_STATE_KEYS.get(agent_name)
    if not agent_output_key:
        print(f"[Callback TestWriter] Error: No output key configured for agent '{agent_name}' in AGENT_STATE_KEYS.")
        return None # Critical error, cannot proceed

    llm_output_str = get_llm_output_from_context(callback_context, agent_output_key)

    if not llm_output_str:
        print(f"[Callback TestWriter] No LLM output found for agent '{agent_name}' via key '{agent_output_key}' or latest_output. Cannot write test file.")
        # Return a Content object with error? Or None? ADK behavior might dictate.
        # For now, returning None as the operation essentially failed.
        return None

    # Test writer prompts usually ask for C++ code.
    code = extract_code_from_llm_output(llm_output_str, language_hint="cpp")

    if not code or not code.strip(): # Check if extracted code is non-empty
        print(f"[Callback TestWriter] Extracted code is empty or None for agent '{agent_name}'. Test file not written.")
        # Optionally, save the raw output for debugging if code extraction fails.
        # debug_dir = ROOT_DIR / "examples" / "tests" / "debug"
        # raw_output_path = debug_dir / f"test_{agent_name.lower().replace('agent', '')}_raw_output.txt"
        # write_code_to_file(raw_output_path, llm_output_str, agent_name, "raw LLM output for test debug")
        return genai_types.Content(parts=[genai_types.Part(text="Failed to extract valid test code.")])


    # --- File path configuration for tests ---
    # TODO: Make the output directory and filename generation more configurable.
    # This could involve agent-specific configurations or deriving paths from input state.
    test_dir = ROOT_DIR / "examples" / "tests"
    # Default filename pattern
    test_filename_default = f"test_{agent_name.lower().replace('agent', '').replace('writer', '')}.cpp"

    # Agent-specific filename overrides
    if agent_name == "TestWriterAgent": # Example: specific name for this primary test writer
         test_filename_default = "test_doorlock_control.cpp"
    # Add other agent-specific filenames here if needed
    # elif agent_name == "AnotherTestAgent":
    #     test_filename_default = "another_specific_test.cpp"

    test_filepath = test_dir / test_filename_default

    write_code_to_file(test_filepath, code, agent_name, "C++ test file")

    # ADK callbacks often expect a Content object as a return, even for side effects.
    # This can be used to pass simple status messages back to the ADK framework or logs.
    return genai_types.Content(parts=[genai_types.Part(text=f"Test file generated successfully: {test_filepath}")])
