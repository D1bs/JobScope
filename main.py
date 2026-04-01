from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from websocket_manager import manager
import asyncio
import redis
import json
from pydantic import BaseModel
from database import get_connection
from celery.result import AsyncResult
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from celery_app import celery_app
from tasks import parse_vacancies_task


async def redis_listener():
    r = redis.Redis(host="localhost", port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe("jobscope_events")

    for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"].decode())


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(redis_listener())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class VacancyCreate(BaseModel):
    title: str
    company: str
    city: str
    salary_from: int
    salary_to: int
    url: str


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/vacancies")
def vacancies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, company, city, salary_from, salary_to, url FROM vacancies
    """)

    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "city": row[3],
            "salary_from": row[4],
            "salary_to": row[5],
            "url": row[6]
        })

    cursor.close()
    conn.close()

    return result


@app.get("/vacancies")
def get_vacancies(
    search: str = None,
    city: str = None,
    schedule: str = None,
    employment: str = None,
    salary_min: int = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT id, title, company, city, salary_from, salary_to,
               url, employment, schedule, contract_type
        FROM vacancies
    """

    conditions = []
    params = []

    if search:
        conditions.append("(title ILIKE %s OR company ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    for column, value in {"city": city, "schedule": schedule, "employment": employment}.items():
        if value:
            conditions.append(f"{column} ILIKE %s")
            params.append(f"%{value}%")

    if salary_min:
        conditions.append("salary_from >= %s")
        params.append(salary_min)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY id DESC LIMIT 100"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    keys = ["id", "title", "company", "city", "salary_from",
            "salary_to", "url", "employment", "schedule", "contract_type"]

    return [dict(zip(keys, row)) for row in rows]


@app.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), AVG(salary_from) FROM vacancies
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "total_vacancies": row[0],
        "avg_salary": round(float(row[1]), 2)
    }


@app.post("/parse")
def parse_vacancies(query: str, city_id: int):
    task = parse_vacancies_task.delay(query, city_id)
    return {"task_id": task.id, "status": "started"}


@app.get("/parse/status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }


@app.get("/skills")
def get_skills():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM vacancy_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 15
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"skills": [{"name": row[0], "count": int(row[1])} for row in rows]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)