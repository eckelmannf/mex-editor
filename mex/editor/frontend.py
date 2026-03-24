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
NODE_VIRTUAL_ENV = CLIENT / ".nodeenv"
NODE_BIN_DIR = NODE_VIRTUAL_ENV / ("Scripts" if sys.platform == "win32" else "/bin")
NODE_BIN = NODE_BIN_DIR / ("node.exe" if sys.platform == "win32" else "node")
CLIENT_NODE_MODULES_BIN_DIR = CLIENT_NODE_MODULES / ".bin"


def _exit_if_needed(proc: subprocess.CompletedProcess[bytes]) -> None:
    if code := proc.returncode:
        sys.exit(code)


def _exec_cmd(cmd: str, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["PATH"] = f"{VENV_SCRIPTS.as_posix()}{os.pathsep}{env['PATH']}"
    return subprocess.run([cmd, *args], env=env, check=True)


def _exec_npm(npm_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["NODE_PATH"] = str(CLIENT_NODE_MODULES)
    env["NPM_CONFIG_PREFIX"] = str(CLIENT)
    env["PATH"] = f"{NODE_BIN_DIR}{os.pathsep}{env['PATH']}"

    npm_call = ["npm"]
    if sys.platform == "win32":
        npm_call = [
            f"{NODE_BIN}",
            str(NODE_BIN_DIR / "node_modules/npm/bin/npm-cli.js"),
        ]

    return subprocess.run(
        [*npm_call, *npm_args],
        check=True,
        env=env,
        cwd=CLIENT,
    )


def _exec_npx(npx_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["NODE_PATH"] = str(CLIENT_NODE_MODULES)
    env["NPM_CONFIG_PREFIX"] = str(CLIENT)
    env["PATH"] = f"{NODE_BIN_DIR}{os.pathsep}{env['PATH']}"

    npx_call = ["npx"]
    if sys.platform == "win32":
        npx_call = [
            f"{NODE_BIN}",
            str(NODE_BIN_DIR / "node_modules/npm/bin/npx-cli.js"),
        ]

    return subprocess.run(
        [*npx_call, *npx_args],
        check=True,
        env=env,
        cwd=CLIENT,
    )


async def exec_npm_async(cmd: str) -> AsyncGenerator[asyncio.subprocess.Process]:
    # CHANGE
    env = os.environ.copy()
    env["NODE_PATH"] = str(CLIENT_NODE_MODULES)
    env["NPM_CONFIG_PREFIX"] = str(CLIENT)
    env["PATH"] = f"{NODE_BIN_DIR}{os.pathsep}{env['PATH']}"

    npm_call = "npm"
    if sys.platform == "win32":
        npm_call = f"{NODE_BIN} {NODE_BIN_DIR / 'node_modules/npm/bin/npm-cli.js'}"

    process = await asyncio.create_subprocess_shell(
        f"{npm_call} {cmd}", cwd=CLIENT, env=env
    )
    yield process

    try:
        await process.wait()
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()


def test() -> None:
    _exit_if_needed(_exec_npm(["run", "test"]))


def install() -> None:
    print("VENV_SCRIPTS", VENV_SCRIPTS, VENV_SCRIPTS.exists())
    print("NODE_VIRTUAL_ENV", NODE_VIRTUAL_ENV.exists())
    _exec_cmd("uv", ["--version"])

    _exit_if_needed(
        _exec_cmd(
            "uv", ["run", "nodeenv", f"{NODE_VIRTUAL_ENV}", "--force", "--node=lts"]
        )
    )

    print("NODE_VIRTUAL_ENV", NODE_VIRTUAL_ENV.exists())
    _exec_npm(["--version"])
    _exit_if_needed(_exec_npm(["install"]))


def build() -> None:
    _exit_if_needed(_exec_npm(["run", "build"]))


def install_and_build() -> None:
    install()
    build()
