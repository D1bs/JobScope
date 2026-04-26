from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    "jobscope",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks"]
)

celery_app.conf.beat_schedule = {
    "parse-all-every-6-hours": {
        "task": "src.tasks.parse_all_task",
        "schedule": crontab(minute=0, hour="*/6"),
    }
}