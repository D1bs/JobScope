import asyncio
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes.parse import router as parse_router
from api.routes.skills import router as skills_router
from api.routes.stats import router as stats_router
from api.routes.vacancies import router as vacancies_router
from websocket_manager import manager


async def redis_listener():
    r = redis.Redis(host="localhost", port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe("jobscope_events")

    while True:
        message = pubsub.get_message()
        if message and message["type"] == "message":
            await manager.broadcast(message["data"].decode())
        await asyncio.sleep(0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(redis_listener())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(vacancies_router)
app.include_router(stats_router)
app.include_router(parse_router)
app.include_router(skills_router)


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)