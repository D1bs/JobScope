import httpx
import asyncio
import redis
import json

from src.database import get_connection

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


async def fetch_vacancy_skills(client, hh_id: str) -> dict:
    try:
        response = await client.get(
            f"https://api.hh.ru/vacancies/{hh_id}",
            timeout=10.0
        )
        data = response.json()
        skills = [s["name"] for s in data.get("key_skills", [])]
        return {"hh_id": hh_id, "skills": skills}
    except Exception:
        return {"hh_id": hh_id, "skills": []}


async def fetch_all_skills(hh_ids: list) -> list:
    results = []
    async with httpx.AsyncClient() as client:
        for hh_id in hh_ids:
            result = await fetch_vacancy_skills(client, hh_id)
            results.append(result)
            await asyncio.sleep(0.2)
    return results


def save_skills(skills_data: list):
    conn = get_connection()
    cursor = conn.cursor()

    for item in skills_data:
        for skill in item["skills"]:
            cursor.execute("""
                INSERT INTO vacancy_skills (vacancy_hh_id, skill_name)
                VALUES (%s, %s)
                ON CONFLICT (vacancy_hh_id, skill_name) DO NOTHING
            """, (item["hh_id"], skill))

    conn.commit()
    cursor.close()
    conn.close()


def fetch_and_save_skills(hh_ids: list):
    skills_data = asyncio.run(fetch_all_skills(hh_ids))
    save_skills(skills_data)


def notify_clients(count: int):
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.publish("jobscope_events", json.dumps({
        "type": "new_vacancies",
        "count": count,
    }))
    r.close()