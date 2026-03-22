from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "jobscope",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks"]
)

celery_app.conf.beat_schedule = {
    "parse-python-jobs-every-6-hours": {
        "task": "tasks.parse_vacancies_task",
        "schedule": crontab(minute=0, hour="*/6"),
        "args": ("Python", 1002)
    }
}