import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mex.editor.api.data import router as data_router
from mex.editor.frontend import CLIENT_DIST, exec_npm_async


def ensure_directory(dir: Path | str) -> None:
    path = Path(dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


async def consume_gen(gen: AsyncGenerator[asyncio.subprocess.Process]) -> None:
    try:
        async for _ in gen:
            pass
    except asyncio.CancelledError:
        # Erlaubt das saubere Abbrechen durch den Task
        pass


@asynccontextmanager
async def dev_lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # --- STARTUP ---
    print("LIFESPAN STARTUP")
    gen = exec_npm_async("run watch")

    # Den Prozess über den Generator starten
    process = await anext(gen)

    # Task erstellen, der den Generator im Hintergrund "besetzt" hält
    watch_task = asyncio.create_task(consume_gen(gen))

    yield
    # yield

    # --- SHUTDOWN ---
    print("Bereinigung beim Herunterfahren...")


def create_fastapi(mode: Literal["dev"] | None = None) -> FastAPI:
    app = FastAPI(title="mex-editor", lifespan=dev_lifespan if mode == "dev" else None)
    app.include_router(data_router, prefix="/api")

    if CLIENT_DIST.exists():
        app.mount("/", StaticFiles(directory=CLIENT_DIST, html=True))

    return app


def main() -> None:
    args = sys.argv[1:]
    dev_mode = "--dev" in args
    app = create_fastapi("dev" if dev_mode else None)
    uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
