import subprocess
from pathlib import Path
from typing import Optional
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

from gen_code.code_gen_agent.common.constants import ROOT_DIR

DEFAULT_TEST_ROOT_PATH = str(ROOT_DIR)

def execute_tests(
        tool_context: ToolContext,
        target_directory: Optional[str] = None
    ) -> dict:
    """
    Executes unit tests by running 'make tests' in the specified directory.
    If no directory is specified, the project's root directory is used as the default.

    Args:
        target_directory (Optional[str]): The path to the directory where 'make tests' will be executed.
                                     If None, the project root directory will be used.
        tool_context (ToolContext): The context for the tool execution, used for actions like escalation.

    Returns:
        dict: A dictionary containing the status of the test execution, standard output, and standard error.
              Example: {'status': 'success' or 'error', 'stdout': '...', 'stderr': '...'}
              In case of an error, an 'error_message' key may also be included.
    """
    # Use the directory specified in the arguments, or the default path if not specified
    target_directory = DEFAULT_TEST_ROOT_PATH
    if target_directory is None:
        effective_test_directory = DEFAULT_TEST_ROOT_PATH
        print(f"  [Tool Call] No target directory specified for {tool_context.agent_name}, using default: {effective_test_directory}")
    else:
        effective_test_directory = target_directory
        print(f"  [Tool Call] Target directory for {tool_context.agent_name}: {effective_test_directory}")

    try:
        test_path = Path(effective_test_directory)
        # Check if the test directory exists and is a directory
        if not test_path.is_dir():
            error_msg = f"Test directory '{effective_test_directory}' not found or is not a directory."
            print(f"  [Tool Call Error] {error_msg}")
            return {
                "status": "error",
                "stdout": f"Checked path: {effective_test_directory}",
                "stderr": f"[ERROR] 1: {error_msg}",
                "error_message": error_msg
            }

        # Command to execute (for unit tests)
        command = ["make", "tests"]
        print(f"  [Tool Call] Executing command: '{' '.join(command)}' in '{effective_test_directory}'")

        # Use subprocess.run to execute the command
        # The cwd parameter specifies the working directory for the command
        process = subprocess.run(
            command,
            cwd=str(test_path),
            capture_output=True,  # Capture standard output and standard error
            text=True,            # Decode output as text
            check=False           # Do not raise an exception if the return code is non-zero
        )

        if process.returncode == 0:
            # On test success, terminate the agent's loop (this behavior can be adjusted based on agent design)
            tool_context.actions.escalate = True
            print(f"  [Tool Call] Test execution successful in '{effective_test_directory}'. Escalation triggered by {tool_context.agent_name}.")
            return {
                "status": "success",
                "stdout": process.stdout,
                "stderr": process.stderr
            }
        else:
            error_msg = f"Test execution failed in '{effective_test_directory}' with return code: {process.returncode}"
            print(f"  [Tool Call Error] {error_msg}")
            print(f"  [Tool Call STDOUT]:\n{process.stdout}")
            print(f"  [Tool Call STDERR]:\n{process.stderr}")
            return {
                "status": "error",
                "stdout": process.stdout,
                "stderr": process.stderr,
                "error_message": f"[ERROR] 2: {error_msg}"
            }
    except FileNotFoundError:
        # If the 'make' command is not found
        error_msg = "The 'make' command was not found. Please ensure make is installed and in your PATH."
        print(f"  [Tool Call Error] {error_msg}")
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"[ERROR] 3: {error_msg}",
            "error_message": "The 'make' command was not found."
        }
    except Exception as e:
        # Other unexpected errors
        error_msg = f"An unexpected error occurred during test execution in '{effective_test_directory}': {str(e)}"
        print(f"  [Tool Call Error] {error_msg}")
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "error_message": f"[ERROR] 4: {error_msg}"
        }

# FunctionTool uses the updated execute_tests_in_directory function
# Change the tool name to be more specific
test_tool = FunctionTool(func=execute_tests)
