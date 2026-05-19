from src.celery_app import celery_app
from src.parser.hh_parser import fetch_vacancies, save_vacancies, fetch_and_save_skills, remove_outdated_vacancies

QUERIES = ["Python", "JavaScript OR TypeScript", "Java",
           "Golang OR Go", "DevOps", "QA OR тестировщик",
           "Data Science OR ML", "iOS OR Swift", "Android OR Kotlin", "C#"]
CITIES = [16, 113, 2, 159]


@celery_app.task
def parse_vacancies_task(query: str, city_id: int):
    vacancies = fetch_vacancies(query, city_id)
    saved = save_vacancies(vacancies)
    hh_ids = [v["id"] for v in vacancies]
    fetch_and_save_skills(hh_ids)
    return {"saved": saved, "query": query, "city_id": city_id}


@celery_app.task
def parse_all_task():
    all_hh_ids = set()

    for query in QUERIES:
        for city_id in CITIES:
            vacancies = fetch_vacancies(query, city_id)
            saved = save_vacancies(vacancies)
            hh_ids = [v["id"] for v in vacancies]
            fetch_and_save_skills(hh_ids)
            all_hh_ids.update(hh_ids)

    removed = remove_outdated_vacancies(all_hh_ids)
    return {"total_in_db": len(all_hh_ids), "removed": removed}