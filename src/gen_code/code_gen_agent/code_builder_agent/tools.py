import subprocess
from pathlib import Path
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

# このファイルの場所に基づいてプロジェクトのルートディレクトリを決定します。
# tools.py が <project_root>/src/gen_code/code_gen_agent/code_builder_agent/tools.py にあると仮定します。
# ファイル構造が異なる場合は、parentsの数を調整してください。
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
# DEFAULT_EXAMPLES_PATH = str(_PROJECT_ROOT / "examples")
DEFAULT_EXAMPLES_PATH = str(_PROJECT_ROOT)

def build_source_code(
        build_directory: str,
        tool_context: ToolContext
    ) -> dict:
    """
    Builds the source code by executing 'make build' in the specified directory.
    Typically targets the 'examples' directory of the project.

    Args:
        build_directory (str): The path to the directory where 'make build' will be executed.
                                Defaults to the project's 'examples' directory
                                (e.g., '/home/user/workspace/code-gen-agent/examples' if the project is at that location).

    Returns:
        dict: A dictionary containing the build status, standard output, and standard error.
              Example: {'status': 'success' or 'error', 'stdout': '...', 'stderr': '...'}
              May also include an 'error_message' key in case of an error.
    """
    build_directory = DEFAULT_EXAMPLES_PATH
    try:
        build_path = Path(build_directory)
        # ビルドディレクトリが存在し、それがディレクトリであることを確認します
        if not build_path.is_dir():
            return {
                "status": "error",
                "stdout": f"DEFAULT_EXAMPLES_PATH: {DEFAULT_EXAMPLES_PATH}",
                "stderr": f"[ERROR] 1: Build directory '{build_directory}' not found or is not a directory.",
                "error_message": f"Build directory '{build_directory}' not found or is not a directory."
            }

        # Command to execute
        command = ["make", "build"]

        # Execute the command using subprocess.run
        # The cwd parameter specifies the working directory for the command
        process = subprocess.run(
            command,
            cwd=str(build_path),
            capture_output=True,  # Capture standard output and standard error
            text=True,            # Decode output as text
            check=False           # Do not raise an exception if the return code is non-zero
        )

        if process.returncode == 0:
            tool_context.actions.escalate = True  # Exit loop
            print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
            return {
                "status": "success",
                "stdout": process.stdout,
                "stderr": process.stderr
            }
        else:
            return {
                "status": "error",
                "stdout": process.stdout,
                "stderr": process.stderr,
                "error_message": f"[ERROR] 2: Build failed with return code: {process.returncode}"
            }
    except FileNotFoundError:
        # 'make' コマンドが見つからない場合 (subprocess.runがcwdで見つからない場合もここにくる可能性あり)
        # もしbuild_path.is_dir()チェック後なら、これは主にmakeコマンド自体の問題
        return {
            "status": "error",
            "stdout": "",
            "stderr": "[ERROR] 3: The 'make' command was not found. Please ensure make is installed and in your PATH.",
            "error_message": "The 'make' command was not found."
        }
    except Exception as e:
        # Other unexpected errors
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "error_message": f"[ERROR] 4: An unexpected error occurred: {str(e)}"
        }

# FunctionTool uses the updated build_source_code function
build_tool = FunctionTool(func=build_source_code)
