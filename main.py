from fastapi import FastAPI
from pydantic import BaseModel
from database import get_connection
from celery.result import AsyncResult
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from celery_app import celery_app
from tasks import parse_vacancies_task


app = FastAPI()
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


@app.post("/vacancies")
def create_vacancy(vacancy: VacancyCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vacancies (title, company, city, salary_from, salary_to, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (vacancy.title, vacancy.company, vacancy.city,
          vacancy.salary_from, vacancy.salary_to, vacancy.url))

    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return {"id": new_id, "message": "Вакансия добавлена"}

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