import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()

# Read token
with open("secret.token", "r") as file:
    SECRET_TOKEN = file.read().strip()

# a demo page used to test the API
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
    """
    Create a new test with the given arguments.

    Args:
        token (str): the secret token to authenticate the request.
        args (str): the arguments to pass to the test.

    Returns:
        A JSON object with the test id and status of the newly created test.

    Raises:
        HTTPException: If the token is invalid.
    """
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
    """
    Start the test process for the given test ID.

    Args:
        test_id (str): The unique identifier of the test to start.
        request (Request): The request object containing the token for authentication.

    Returns:
        A JSON object with the status of the test and the test ID.

    Raises:
        HTTPException: If the token is invalid, test is not found, or test is already running.
    """
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
    """
    Retrieve the status of a specific test.

    Args:
        test_id (str): The unique identifier of the test to retrieve the status for.
        request (Request): The request object for authentication and other request data.

    Returns:
        A JSON object with the current status of the test.

    Raises:
        HTTPException: If the test is not found.
    """
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test = active_tests[test_id]
    return {
        "status": test["status"]
    }

@app.get("/test_output/{test_id}")
async def get_test_output(test_id: str, length: int):
    """
    Retrieve a portion of the test output.

    Args:
        test_id (str): The unique identifier of the test.
        length (int): The number of characters to skip from the beginning of the output.

    Returns:
        A JSON object with the output of the test and the length of the output.

    Raises:
        HTTPException: If the test is not found.
    """
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
    """
    Stop a running test.

    Args:
        test_id (str): The unique identifier of the test to stop.
        request (Request): The request object for authentication and other request data.

    Returns:
        A JSON object with the current status of the test.

    Raises:
        HTTPException: If the test is not found or the token is invalid.
    """
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
    """
    Collect output from a running test process.

    This function is run in the background as a task to collect the output from a test process.
    It will stop when the test is stopped or completed.

    Args:
        test_id (str): The unique identifier of the test.

    Returns:
        None
    """
    
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
        
@app.post("/write_test")
async def write_test(request: Request):
    """
    Write a test configuration to a file.

    This endpoint allows writing a test configuration to a TOML file with the given test name and content.
    If the file already exists, it will be overridden.

    Args:
        request (Request): The request object containing JSON data with 'token', 'test_name', and 'test_content'.

    Returns:
        A JSON object indicating the success status, message, and whether the file was overridden.

    Raises:
        HTTPException: If the token is invalid or there is an error writing the file.
    """
    data = await request.json()
    token = data.get("token")
    test_name = data.get("test_name")
    test_content = data.get("test_content")
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    override = os.path.isfile(f"tests/{test_name}.toml")
    try:
        with open(f"tests/{test_name}.toml", "w") as file:
            file.write(test_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "message": f"{test_name}.toml written successfully", "override": override}

@app.post("/write_board_config")
async def write_board_config(request: Request):
    data = await request.json()
    token = data.get("token")
    board_config_name = data.get("board_config_name")
    board_config_content = data.get("board_config_content")
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    override = os.path.isfile(f"boards/{board_config_name}.toml")
    try:
        with open(f"boards/{board_config_name}.toml", "w") as file:
            file.write(board_config_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "message": f"{board_config_name}.toml written successfully", "override": override}
