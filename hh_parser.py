import httpx
from database import get_connection

def fetch_vacancies(query: str, city_id: int):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "area": city_id,
        "per_page": 20
    }
    response = httpx.get(url, params=params)
    data = response.json()
    return data["items"]


def save_vacancies(vacancies: list):
    conn = get_connection()
    cursor = conn.cursor()
    saved = 0

    for vacancy in vacancies:
        salary = vacancy.get("salary")
        salary_from = salary["from"] if salary else None
        salary_to = salary["to"] if salary else None

        cursor.execute("""
            INSERT INTO vacancies (hh_id, title, company, city, salary_from, salary_to, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (hh_id) DO NOTHING
        """, (
            vacancy["id"],
            vacancy["name"],
            vacancy["employer"]["name"],
            vacancy["area"]["name"],
            salary_from,
            salary_to,
            vacancy["alternate_url"]
        ))

        if cursor.rowcount == 1:
            saved += 1

    conn.commit()
    cursor.close()
    conn.close()
    return saved