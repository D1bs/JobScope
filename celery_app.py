from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    "jobscope",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks"]
)

celery_app.conf.beat_schedule = {
    "parse-python-jobs-every-6-hours": {
        "task": "tasks.parse_vacancies_task",
        "schedule": crontab(minute=0, hour="*/6"),
        "args": ("Python", 1002)
    }
}