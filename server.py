import json
import subprocess
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()

# 读取 token
with open("secret.token", "r") as file:
    SECRET_TOKEN = file.read().strip()

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
            var ws;
            function startTest() {
                var args = prompt("Enter CLI arguments:");
                fetch("/start_test", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({token: "your_token_here", args: args})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.ws_url) {
                        ws = new WebSocket(data.ws_url);
                        ws.onmessage = function(event) {
                            var output = document.getElementById("output");
                            output.value += event.data + "\\n";
                        };
                    } else {
                        alert("Failed to start test: " + data.message);
                    }
                });
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
    try:
        data = await websocket.receive_text()
        data = json.loads(data)
        token = data.get("token")
        args = data.get("args")

        if token != SECRET_TOKEN:
            await websocket.send_text("Invalid token.")
            await websocket.close()
            return

        process = await asyncio.create_subprocess_exec(
            'python', 'main.py', *args.split(),
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
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()

@app.post("/start_test")
async def start_test(request: Request):
    data = await request.json()
    token = data.get("token")
    args = data.get("args")

    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    ws_url = "ws://localhost:8000/ws"
    return {"message": "Test started", "args": args, "ws_url": ws_url}