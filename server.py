import subprocess
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <textarea id="output" rows="20" cols="100"></textarea><br>
        <button onclick="startTest()">Start Test</button>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var output = document.getElementById("output");
                output.value += event.data + "\\n";
            };
            function startTest() {
                var args = prompt("Enter CLI arguments:");
                ws.send(args);
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        args = data.split()
        process = await asyncio.create_subprocess_exec(
            'python', 'main.py', *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode('utf-8').strip())
        await process.wait()
        await websocket.send_text("Test completed.")