from celery_app import celery_app
from hh_parser import fetch_vacancies, save_vacancies, fetch_and_save_skills, notify_clients


@celery_app.task
def parse_vacancies_task(query: str, city_id: int):
    vacancies = fetch_vacancies(query, city_id)
    saved = save_vacancies(vacancies)

    hh_ids = [v["id"] for v in vacancies]
    fetch_and_save_skills(hh_ids)

    notify_clients(saved)

    return {"saved": saved, "query": query, "city_id": city_id}