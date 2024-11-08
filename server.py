import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()

# Read token
with open("secret.token", "r") as file:
    SECRET_TOKEN = file.read().strip()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Board Test</title>
    </head>
    <body>
        <h1>Board Test</h1>
        <textarea id="output" rows="20" cols="100"></textarea><br>
        <button onclick="startTest()">Start Test</button>
        <script>
            let testId = null;
            let polling = null;
            let outputLength = 0;

            async function startTest() {
                const args = prompt("Enter CLI arguments:");
                if (!args) return;

                // Create test
                const createResponse = await fetch("/create_test", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({token: "your_token_here", args: args})
                });
                const createData = await createResponse.json();
                testId = createData.test_id;

                // Start test
                const startResponse = await fetch(`/start_test/${testId}`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({token: "your_token_here"})
                });
                
                // Start polling for status and output
                polling = setInterval(async () => {
                    const statusResponse = await fetch(`/test_status/${testId}`);
                    const statusData = await statusResponse.json();

                    const outputResponse = await fetch(`/test_output/${testId}?length=${outputLength}`);
                    const outputData = await outputResponse.json();
                    document.getElementById("output").value += outputData.output;
                    outputLength += outputData.length;

                    if (statusData.status === "completed" || statusData.status === "stopped") {
                        clearInterval(polling);
                    }
                }, 1000);
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# Store active tests and their status
active_tests = {}

@app.post("/create_test")
async def create_test(request: Request):
    data = await request.json()
    token = data.get("token")
    args = data.get("args")

    if token != SECRET_TOKEN:
        print(f"Invalid token: {token}")
        raise HTTPException(status_code=403, detail="Invalid token")

    # Generate unique test ID
    test_id = str(len(active_tests) + 1)
    active_tests[test_id] = {
        "status": "created",
        "args": args,
        "output": [],
        "process": None
    }

    return {"test_id": test_id, "status": "created"}

@app.post("/start_test/{test_id}")
async def start_test(test_id: str, request: Request):
    data = await request.json()
    if data.get("token") != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")

    test = active_tests[test_id]
    if test["status"] == "running":
        raise HTTPException(status_code=400, detail="Test already running")

    process = await asyncio.create_subprocess_exec(
        'python', 'main.py', *test["args"].split(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    test["process"] = process
    test["status"] = "running"
    
    # Start background task to collect output
    asyncio.create_task(collect_output(test_id))
    
    return {"status": "started", "test_id": test_id}

@app.get("/test_status/{test_id}")
async def get_test_status(test_id: str, request: Request):
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test = active_tests[test_id]
    return {
        "status": test["status"]
    }

@app.get("/test_output/{test_id}")
async def get_test_output(test_id: str, length: int):
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test = active_tests[test_id]
    output = "".join(test["output"][length:])
    return {
        "output": output,
        "length": len(output)
    }

@app.post("/stop_test/{test_id}")
async def stop_test(test_id: str, request: Request):
    data = await request.json()
    if data.get("token") != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")

    test = active_tests[test_id]
    if test["process"]:
        test["process"].terminate()
        test["status"] = "stopped"
        return {"status": "stopped"}
    return {"status": test["status"]}

async def collect_output(test_id: str):
    test = active_tests[test_id]
    process = test["process"]
    
    while True:
        if test["status"] == "stopped":
            break
        
        char = await process.stdout.read(1)
        if not char:
            test["status"] = "completed"
            break
            
        test["output"].append(char.decode('utf-8'))
    
    await process.wait()
    
    # Ensure to read any remaining output after process completion
    remaining_output = await process.stdout.read()
    if remaining_output:
        test["output"].append(remaining_output.decode('utf-8'))