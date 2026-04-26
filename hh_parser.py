import httpx
import asyncio
import redis
import json

from src.database import get_connection
from src.config import settings


def get_hh_headers() -> dict:
    return {
        "User-Agent": f"JobScope/1.0 ({settings.HH_CLIENT_ID})",
        "Authorization": f"Bearer {get_access_token()}",
    }


def get_access_token() -> str:
    return settings.HH_ACCESS_TOKEN


def fetch_vacancies(query: str, city_id: int):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "area": city_id,
        "per_page": 20,
        "search_field": "name",
    }

    response = httpx.get(url, params=params, headers=get_hh_headers(), timeout=10.0)
    data = response.json()

    if "items" not in data:
        print(f"[HH ERROR] {data}")
        return []

    return data["items"]


def save_vacancies(vacancies: list):
    conn = get_connection()
    cursor = conn.cursor()
    saved = 0

    for vacancy in vacancies:
        salary        = vacancy.get("salary") or {}
        salary_from   = salary.get("from")
        salary_to     = salary.get("to")

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
            vacancy["alternate_url"],
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
            headers={"Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}"},
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
    r = redis.from_url(settings.REDIS_URL)
    r.publish("jobscope_events", json.dumps({
        "type": "new_vacancies",
        "count": count,
    }))
    r.close()