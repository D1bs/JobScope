from fastapi import APIRouter
from src.tasks import parse_vacancies_task
from celery.result import AsyncResult
from src.celery_app import celery_app

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("")
def parse_vacancies(query: str, city_id: int):
    task = parse_vacancies_task.delay(query, city_id)
    return {"task_id": task.id, "status": "started"}


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }