import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes.parse import router as parse_router
from src.api.routes.skills import router as skills_router
from src.api.routes.stats import router as stats_router
from src.api.routes.vacancies import router as vacancies_router
from src.websocket_manager import manager
from src.config import settings


async def redis_listener():
    r = aioredis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("jobscope_events")

    async for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"].decode())


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