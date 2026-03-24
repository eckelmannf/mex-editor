import subprocess
import urllib.request
import time
import sys
import asyncio
import uvicorn
from mex.editor.main import create_fastapi
from mex.editor.frontend import _exec_npm, test

test_app = create_fastapi(None, "api")

def run() -> None:
    server = subprocess.Popen(["uvicorn", "mex.editor.othername_test:test_app", "--port", "8000"])
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen("http://127.0.0.1:8000/api/hello")
                break
            except Exception as e:
                print(f"error: {e}")
                time.sleep(0.5)
        else:
            print("Timeout: Server nicht gestartet")
            sys.exit(1)

        result = _exec_npm(
            ["run", "test"]
        )  # subprocess.run(["ng", "test", "--watch=false"])
        print(result.stderr)
        print(result.stdout)
        sys.exit(result.returncode)
    finally:
        print("othername_test: server shutting down...")
        server.terminate()
        server.wait()


# async def main() -> None:
#     print("TEST MAIN starting")
#     config = uvicorn.Config(create_fastapi(), port=8000)
#     server = uvicorn.Server(config)

#     # Run the server as a background task
#     server_task = asyncio.create_task(server.serve())

#     # Do other things here
#     print("Server is starting...")
#     await asyncio.sleep(5)
#     print("Five seconds have passed, server is still running.")

#     print("Running angular tests...")
#     test()

#     await server_task

# def run() -> None:
#     asyncio.run(main())

# print("TEST.py :: CURRENT __name__ is", __name__)
# if __name__ == "__main__":
#     asyncio.run(main())
