
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from QueueDataManager import QueueDataManager

app = FastAPI()
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATA MANAGERS
queueDataManager = QueueDataManager(None)

# Websocket connection reference
websocket_connection = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global websocket_connection
    await websocket.accept()
    websocket_connection = websocket
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.get("/test-send")
async def test_send_socket():
    global websocket_connection
    if websocket_connection:
        await websocket_connection.send_text("Hello from server")
        return JSONResponse(content={"status": "success"})
    else:
        return JSONResponse(content={"status": "error", "message": "No websocket connection"})

@app.post("/request-queue")
async def request_queue(
        queue:dict
):
    id = queueDataManager.insert(queue)
    queue = queueDataManager.getOne(id)
    return JSONResponse(content=queue)

@app.get('/category/{category}/queue')
async def get_queue_by_category(category):
    queue = queueDataManager.getCollectionByCategory(category)
    return JSONResponse(content=queue)