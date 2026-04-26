import redis
import json

from fastapi import WebSocket
from src.config import settings


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)

        for connection in dead:
            self.active_connections.remove(connection)


manager = ConnectionManager()


def notify_clients(count: int):
    r = redis.from_url(settings.REDIS_URL)
    r.publish("jobscope_events", json.dumps({
        "type": "new_vacancies",
        "count": count,
    }))
    r.close()