import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
THIS_DIR = Path(__file__).parent.resolve()
VENV = ROOT_DIR / ".venv"
VENV_SCRIPTS = VENV / "Scripts"
CLIENT = THIS_DIR / "client"
CLIENT_DIST = CLIENT / "dist/mex-editor/browser"
CLIENT_NODE_MODULES = CLIENT / "node_modules"
CLIENT_NODE_MODULES_BIN = CLIENT_NODE_MODULES / ".bin"
NODE_VIRTUAL_ENV = CLIENT / ".nodeenv"
NODE_BIN = NODE_VIRTUAL_ENV / ("Scripts" if sys.platform == "win32" else "/bin")
NODE_EXEC = NODE_BIN / ("node.exe" if sys.platform == "win32" else "node")


def _exec_cmd(cmd: str) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["PATH"] = f"{VENV_SCRIPTS.as_posix()};{env['PATH']}"
    return subprocess.run(cmd)


def _exec_npm(cmd: str) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["NODE_PATH"] = str(CLIENT_NODE_MODULES)
    env["NPM_CONFIG_PREFIX"] = str(CLIENT)
    env["PATH"] = f"{NODE_BIN.as_posix()};{env['PATH']}"

    npm_call = os.path.join(NODE_BIN, "node_modules", "npm", "bin", "npm-cli.js")
    cmd_call = f"{NODE_EXEC} {npm_call} {cmd}"

    print("_exec_npm", cmd_call)
    return subprocess.run(cmd_call, cwd=CLIENT, env=env)


async def exec_npm_async(cmd: str) -> AsyncGenerator[asyncio.subprocess.Process]:
    env = os.environ.copy()
    env["NODE_PATH"] = str(CLIENT_NODE_MODULES)
    env["NPM_CONFIG_PREFIX"] = str(CLIENT)
    env["PATH"] = f"{NODE_BIN.as_posix()};{env['PATH']}"

    npm_call = os.path.join(NODE_BIN, "node_modules", "npm", "bin", "npm-cli.js")
    cmd_call = f"{NODE_EXEC} {npm_call} {cmd}"

    print("_exec_npm_async", cmd_call)
    process = await asyncio.create_subprocess_shell(cmd_call, cwd=CLIENT, env=env)
    yield process

    try:
        await process.wait()
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()


def install() -> None:
    if (not Path(NODE_VIRTUAL_ENV).exists()) and (
        code := _exec_cmd(f"uv run nodeenv {NODE_VIRTUAL_ENV} --node=lts").returncode
    ):
        sys.exit(code)

    sys.exit(_exec_npm("install").returncode)
    # sys.exit(_exec_node_cmd("install").returncode)


def build() -> None:
    sys.exit(_exec_npm("run build").returncode)
