from celery_app import celery_app
from hh_parser import fetch_vacancies, save_vacancies, fetch_and_save_skills, notify_clients

QUERIES = ["Python", "JavaScript", "Java", "Go", "DevOps", "QA", "Data Science", "iOS", "Android", "C#"]
CITIES = [16, 113, 2, 159]  # Беларусь, Россия, Казахстан, Санкт-Петербург

@celery_app.task
def parse_vacancies_task(query: str, city_id: int):
    vacancies = fetch_vacancies(query, city_id)
    saved = save_vacancies(vacancies)

    hh_ids = [v["id"] for v in vacancies]
    fetch_and_save_skills(hh_ids)

    notify_clients(saved)

    return {"saved": saved, "query": query, "city_id": city_id}


@celery_app.task
def parse_all_task():
    total = 0
    for query in QUERIES:
        for city_id in CITIES:
            vacancies = fetch_vacancies(query, city_id)
            saved = save_vacancies(vacancies)
            hh_ids = [v["id"] for v in vacancies]
            fetch_and_save_skills(hh_ids)
            total += saved
    notify_clients(total)
    return {"total_saved": total}