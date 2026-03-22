from celery_app import celery_app
from hh_parser import fetch_vacancies, save_vacancies

@celery_app.task
def parse_vacancies_task(query: str, city_id: int):
    vacancies = fetch_vacancies(query, city_id)
    saved = save_vacancies(vacancies)
    return {"saved": saved, "query": query, "city_id": city_id}