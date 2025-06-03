import subprocess
from google.adk.tools import FunctionTool

def build_source_code(build_dir: str = "examples/build", target: str = None) -> dict:
    """
    CMakeでソースコードをビルドします。
    build_dirが初期化されていなければ初期化も行います。
    Args:
        build_dir (str): ビルドディレクトリのパス
        target (str): ビルドターゲット名（省略時は全体ビルド）
        generator (str): CMakeジェネレータ（例: "Ninja"）
        toolchain (str): CMakeツールチェーンファイルのパス
    Returns:
        dict: {'status': 'success' or 'error', 'stdout': ..., 'stderr': ...}
    """
    import os
    import shutil
    generator = "Ninja"
    toolchain = "cmake/gcc.cmake"
    cmake_lists = os.path.join(os.path.dirname(build_dir), "CMakeLists.txt")
    src_dir = os.path.dirname(build_dir) if os.path.exists(cmake_lists) else os.path.abspath("examples")
    stdout_all = ""
    stderr_all = ""
    try:
        # build_dirが存在する場合は安全のため削除
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
            except Exception as e:
                return {"status": "error", "stdout": stdout_all, "stderr": f"build_dir削除失敗: {e}"}
        # 初期化
        init_cmd = [
            "cmake", "-S", src_dir, "-B", build_dir,
            "-G", generator,
            "-D", f"CMAKE_TOOLCHAIN_FILE={toolchain}"
        ]
        proc_init = subprocess.run(init_cmd, capture_output=True, text=True)
        stdout_all += proc_init.stdout
        stderr_all += proc_init.stderr
        if proc_init.returncode != 0:
            return {"status": "error", "stdout": stdout_all, "stderr": stderr_all}
        # ビルド
        build_cmd = ["cmake", "--build", build_dir]
        if target:
            build_cmd += ["--target", target]
        proc_build = subprocess.run(build_cmd, capture_output=True, text=True)
        stdout_all += proc_build.stdout
        stderr_all += proc_build.stderr
        return {
            "status": "success" if proc_build.returncode == 0 else "error",
            "stdout": stdout_all,
            "stderr": stderr_all,
        }
    except Exception as e:
        return {"status": "error", "stdout": stdout_all, "stderr": str(e)}

build_tool = FunctionTool(func=build_source_code)
