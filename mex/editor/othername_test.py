import asyncio
import uvicorn
from mex.editor.main import create_fastapi
from mex.editor.frontend import test


async def main() -> None:
    print("TEST MAIN starting")
    config = uvicorn.Config(create_fastapi(), port=8000)
    server = uvicorn.Server(config)

    # Run the server as a background task
    server_task = asyncio.create_task(server.serve())

    # Do other things here
    print("Server is starting...")
    await asyncio.sleep(5)
    print("Five seconds have passed, server is still running.")

    print("Running angular tests...")
    test()

    await server_task


print("TEST.py :: CURRENT __name__ is", __name__)
if __name__ == "__main__":
    asyncio.run(main())
