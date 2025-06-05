"""
Callback function for generating primary code files (e.g., .h and .c files).

This module defines the `generate_file_callback` which is intended to be used
as an `after_agent_callback` in the ADK framework. It handles the logic for
extracting code from LLM responses and writing it to appropriate files, often
differentiating between header and source files based on agent-specific logic
or JSON structures in the LLM output.
"""
from typing import Optional, Dict, Any
from pathlib import Path

from google.adk.services.action_handler import CallbackContext # Adjusted from google.adk.agents.callback_context
from google.genai import types as genai_types # For return type hint, aliased for clarity

from gen_code.code_gen_agent.common.constants import ROOT_DIR, AGENT_STATE_KEYS
from .callback_utils import (
    get_llm_output_from_context,
    extract_json_data,
    extract_code_from_markdown,
    write_code_to_file
)

def generate_file_callback(
    callback_context: CallbackContext
) -> Optional[genai_types.Content]:
    """
    Handles the generation of code files based on LLM output.

    This callback is designed to be triggered after an agent (like CodeWriterAgent
    or CodeRefactorerAgent) completes its execution. It performs the following steps:
    1.  Retrieves the LLM output string using `get_llm_output_from_context` from
        `callback_utils`. This utility checks both the agent's state and its
        latest direct output.
    2.  Determines if the agent is expected to produce JSON output containing
        separate header and source files (e.g., CodeWriterAgent, CodeRefactorerAgent).
        - If JSON is expected:
            - It uses `extract_json_data` to parse the LLM output.
            - If successful, it extracts header and source content based on
              predefined keys (e.g., "header_file_content", "source_file_content").
            - Writes these to appropriately named .h and .c files (e.g.,
              "doorlock_control.h", "doorlock_control.c") in a configured directory.
            - If JSON parsing or key extraction fails, it attempts a fallback to
              extract a single C code block using `extract_code_from_markdown`.
        - If JSON is not expected (or as a default behavior):
            - It attempts to extract a single C code block from the LLM output
              using `extract_code_from_markdown`.
            - If successful, writes the code to a .c file.
    3.  Uses `write_code_to_file` for all file writing operations, ensuring
        directories are created and errors are logged.
    4.  File paths and some agent-specific behaviors (like JSON keys and output
        filenames) are currently defined within this function but are marked with
        #TODO for future configurability.

    Args:
        callback_context: The context object provided by the ADK framework,
                          containing agent state, latest output, agent name, etc.

    Returns:
        Optional[google.genai.types.Content]: Typically None, as this callback
        primarily performs side effects (writing files). However, it can return
        a Content object if required by ADK conventions for signaling status,
        though this is not currently implemented.
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id # Useful for debugging/tracing
    print(f"\n[Callback] In 'generate_file_callback' for agent: {agent_name} (Inv: {invocation_id})")

    # Retrieve the agent output key from the central constants mapping.
    agent_output_key = AGENT_STATE_KEYS.get(agent_name)
    if not agent_output_key:
        print(f"[Callback] Error: No output key configured for agent '{agent_name}' in AGENT_STATE_KEYS. Cannot process files.")
        return None # Critical: cannot determine where to look for output.

    # Get the LLM's output string using the common utility.
    llm_output_str = get_llm_output_from_context(callback_context, agent_output_key)

    if not llm_output_str: # Check if output is None or an empty string
        print(f"[Callback] Error: Agent '{agent_name}' produced no text content (via key '{agent_output_key}' or latest_output). Files not written.")
        return None

    # --- File path and naming configuration (candidates for external configuration) ---
    # TODO: Make output directory and base filenames more configurable,
    # potentially based on agent configuration or input parameters/state.
    output_base_filename_default = f"file_{agent_name.lower().replace('agent', '')}"
    # Default directory for generated source files.
    output_dir_path: Path = ROOT_DIR / "examples" / "src" / "body_app"

    # --- Agent-specific logic for handling JSON vs. single markdown output ---
    header_key: Optional[str] = None
    source_key: Optional[str] = None
    is_json_expected = False
    current_output_base_filename = output_base_filename_default

    # Configure behavior based on the agent that triggered this callback.
    if agent_name == "CodeWriterAgent":
        header_key = "header_file_content" # Expected JSON key for header code
        source_key = "source_file_content" # Expected JSON key for source code
        # Optionally, use a more specific base filename for this agent's output.
        # current_output_base_filename = "doorlock_control" # Example
        is_json_expected = True
    elif agent_name == "CodeRefactorerAgent":
        header_key = "refactored_header_file_content"
        source_key = "refactored_source_file_content"
        current_output_base_filename = "doorlock_control" # Refactored files often target a specific module
        is_json_expected = True
    # Add other agents that are expected to output JSON for H/C files here.
    # Example:
    # elif agent_name == "AnotherMultiFileAgent":
    #     header_key = "h_content"
    #     source_key = "c_content"
    #     is_json_expected = True

    if is_json_expected and header_key and source_key:
        # This agent is expected to produce a JSON object with header and source code.
        print(f"[Callback] Agent '{agent_name}' expects JSON output with keys: '{header_key}', '{source_key}'.")
        json_data = extract_json_data(llm_output_str) # Utility from callback_utils

        if json_data:
            header_content = json_data.get(header_key)
            source_content = json_data.get(source_key)

            # Ensure both header and source content are valid, non-empty strings.
            if isinstance(header_content, str) and header_content.strip() and \
               isinstance(source_content, str) and source_content.strip():

                header_filepath = output_dir_path / f"{current_output_base_filename}.h"
                source_filepath = output_dir_path / f"{current_output_base_filename}.c"

                # Write the extracted header and source files.
                write_code_to_file(header_filepath, header_content, agent_name, f"{agent_name} header file")
                write_code_to_file(source_filepath, source_content, agent_name, f"{agent_name} source file")
            else:
                # Log if content is missing, not a string, or empty.
                missing_keys_info = []
                if not isinstance(header_content, str) or not header_content.strip():
                    missing_keys_info.append(f"header ('{header_key}') empty or not string")
                if not isinstance(source_content, str) or not source_content.strip():
                    missing_keys_info.append(f"source ('{source_key}') empty or not string")
                print(f"[Callback] Warning: {' and '.join(missing_keys_info)} in JSON from '{agent_name}'. Files not written.")
        else:
            # Fallback: LLM was expected to produce JSON but failed or returned malformed JSON.
            # Try to extract a single C code block from the raw output as a last resort.
            print(f"[Callback] Warning: Failed to parse JSON or extract required keys for '{agent_name}'. "
                  "Attempting C markdown extraction as fallback.")
            c_code_fallback = extract_code_from_markdown(llm_output_str, language="c") # Utility
            if c_code_fallback:
                # Use a distinct name for fallback files to avoid overwriting and indicate issues.
                fallback_filepath = output_dir_path / f"{current_output_base_filename}_fallback.c"
                write_code_to_file(fallback_filepath, c_code_fallback, agent_name, "C code file (JSON fallback)")
            else:
                print(f"[Callback] Warning: Fallback C markdown extraction also failed for agent '{agent_name}'. No file written from this agent.")
    else:
        # Default behavior: Agent is not configured for JSON multi-file output.
        # Attempt to extract a single C code file from markdown.
        print(f"[Callback] Info: Agent '{agent_name}' attempting single C file markdown extraction (not configured for JSON H/C generation).")
        c_code = extract_code_from_markdown(llm_output_str, language="c") # Utility
        if c_code: # Ensure extracted code is not empty
            single_output_filepath = output_dir_path / f"{current_output_base_filename}.c"
            write_code_to_file(single_output_filepath, c_code, agent_name, "C code file")
        else:
            print(f"[Callback] Warning: Could not extract C code using markdown from '{agent_name}' output. File not written.")
            # For debugging, it can be useful to save the raw output if extraction fails.
            # raw_output_path = output_dir_path / f"{current_output_base_filename}_raw_output.txt"
            # write_code_to_file(raw_output_path, llm_output_str, agent_name, "raw LLM output (markdown extraction failed)")

    # ADK callbacks might expect a Content object. Returning None is typical for side-effect-only callbacks.
    # If status reporting back to the ADK framework is needed, construct a genai_types.Content here.
    return None
