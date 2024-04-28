from datetime import datetime

import fastapi.responses
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse, Response, FileResponse
from QueueDataManager import QueueDataManager
from statistics import plotQueue

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
websocket_connection = {
    '10-wheels': None,
    '6-wheels': None,
    'pickup': None,
    'central': None
}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket, endpoint: str):
    global websocket_connection
    await websocket.accept()
    websocket_connection[endpoint] = websocket
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


@app.get("/notify-refresh/{endpoint}")
async def notify_refresh(endpoint: str):
    global websocket_connection
    if websocket_connection[endpoint]:
        await websocket_connection[endpoint].send_text("refresh")
        return JSONResponse(content={"status": "success"})
    else:
        return JSONResponse(content={"status": "error", "message": "No websocket connection"})

@app.post("/request-queue")
async def request_queue(
        queue:dict
):
    id = queueDataManager.insert(queue)
    queue = queueDataManager.getOne(id)
    category = queue['category']
    # Notify officers and send refreshed data
    refreshed_queue = queueDataManager.getAwaitingCollectionByCategory(category)
    if websocket_connection[category]:
        await websocket_connection[category].send_json(refreshed_queue)

    return JSONResponse(content=queue)

@app.get('/category/{category}/queue')
async def get_queue_by_category(category):
    queue = queueDataManager.getAwaitingCollectionByCategory(category)
    return JSONResponse(content=queue)

@app.get('/warehouse/{warehouse}/queue/{id}')
async def get_queue_by_id(warehouse, id):
    queue = queueDataManager.getOne(id)
    queue['warehouse'] = warehouse
    queue['enter_time'] = datetime.now()
    queueDataManager.update(queue)
    queue = queueDataManager.getOne(id)

    # Notify the 'central' to refresh the queue and append the lastly appended item
    data = {
        'category': queue['category'],
        'entityList': queueDataManager.getCalledQueueByCategory(queue['category']),
        'lastQueue': queue
    }
    if websocket_connection['central']:
        await websocket_connection['central'].send_json(data)
    # Notify the siblings, TODO: should need to fix
    if websocket_connection[queue['category']]:
        await websocket_connection[queue['category']].send_json(data)
    return JSONResponse(content=queue)

@app.post('/queue/{id}/finish')
async def finish_queue(id):
    queue = queueDataManager.getOne(id)
    queue['exit_time'] = datetime.now()
    queueDataManager.update(queue)
    queue = queueDataManager.getOne(id)
    return JSONResponse(content=queue)

@app.get('/export/pdf')
async def export_pdf(
        response_class=FileResponse
):
    pdffile = plotQueue()
    return FileResponse(pdffile)

