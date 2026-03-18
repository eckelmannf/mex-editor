import asyncio
from collections.abc import AsyncGenerator
import subprocess
from contextlib import asynccontextmanager
import sys
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mex.editor.api.data import router as data_router

THIS = Path(__file__).parent
CLIENT = Path(THIS / "client")
DIST = Path(CLIENT / "dist/mex-editor/browser")
NODE_MODULES = Path(CLIENT / "node_modules")


# $env:NODE_PATH="./mex/editor/client/node_modules"
# $env:NPM_CONFIG_PREFIX="./mex/editor/client"
# $env:Path="./mex/editor/client/node_modules/.bin;$env:Path"
@asynccontextmanager
async def dev_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # --- STARTUP ---
    script_path: Path = THIS / "../../activate.ps1"
    powershell_cmd: str = (
        f"& '{script_path}'; Set-Location '{CLIENT.as_posix()}'; npm run watch;"
    )
    process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
        "powershell.exe",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        powershell_cmd,
    )

    yield

    if process.returncode is None:
        print("Beende NPM Watch...")
        process.terminate()
        await process.wait()

    # --- SHUTDOWN ---
    print("Bereinigung beim Herunterfahren...")


def main() -> None:
    args = sys.argv[1:]
    dev_mode = "--dev" in args

    app = FastAPI(title="mex-editor", lifespan=dev_lifespan if dev_mode else None)
    app.include_router(data_router, prefix="/api")
    app.mount("/", StaticFiles(directory=DIST, html=True), name="static")

    uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
