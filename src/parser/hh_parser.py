import httpx
import asyncio

from src.database import get_connection
from src.config import settings
from src.currency import convert_to_byn


def get_hh_headers() -> dict:
    return {
        "User-Agent": f"JobScope/1.0 ({settings.HH_CLIENT_ID})",
        "Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}",
    }


def fetch_vacancies(query: str, city_id: int):
    url = "https://api.hh.ru/vacancies"

    it_roles = ["96", "156", "104", "107", "112", "113", "148", "114", "116", "121", "124", "125", "126"]

    params = [
        ("text", query),
        ("per_page", 20),
        ("search_field", "name"),
    ]

    if city_id and city_id != 0:
        params.append(("area", city_id))

    for role_id in it_roles:
        params.append(("professional_role", role_id))

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
        currency      = salary.get("currency")
        contract_type = vacancy.get("type", {}).get("name")

        salary_from_byn = convert_to_byn(salary_from, currency)
        salary_to_byn   = convert_to_byn(salary_to, currency)

        cursor.execute("""
            INSERT INTO vacancies
                (hh_id, title, company, city, salary_from, salary_to, currency,
                 salary_from_byn, salary_to_byn, url, contract_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (hh_id) DO NOTHING
        """, (
            vacancy["id"],
            vacancy["name"],
            vacancy["employer"]["name"],
            vacancy["area"]["name"],
            salary_from,
            salary_to,
            currency,
            salary_from_byn,
            salary_to_byn,
            vacancy["alternate_url"],
            contract_type,
        ))

        if cursor.rowcount == 1:
            saved += 1

    conn.commit()
    cursor.close()
    conn.close()
    return saved


async def fetch_vacancy_details(client, hh_id: str) -> dict:
    try:
        response = await client.get(
            f"https://api.hh.ru/vacancies/{hh_id}",
            headers={"Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}"},
            timeout=10.0
        )
        data = response.json()

        skills = [s["name"] for s in data.get("key_skills", [])]

        work_formats = data.get("work_format") or []
        schedule = ", ".join(f["name"] for f in work_formats) if work_formats else None

        employment_form = data.get("employment_form") or {}
        employment = employment_form.get("name")

        return {
            "hh_id": hh_id,
            "skills": skills,
            "employment": employment,
            "schedule": schedule,
        }
    except Exception:
        return {"hh_id": hh_id, "skills": [], "employment": None, "schedule": None}


async def fetch_all_details(hh_ids: list) -> list:
    results = []
    async with httpx.AsyncClient() as client:
        for hh_id in hh_ids:
            result = await fetch_vacancy_details(client, hh_id)
            results.append(result)
            await asyncio.sleep(0.2)
    return results


def save_skills(skills_data: list):
    conn = get_connection()
    cursor = conn.cursor()

    for item in skills_data:
        # обновляем employment и schedule
        if item.get("employment") or item.get("schedule"):
            cursor.execute("""
                UPDATE vacancies
                SET employment = %s, schedule = %s
                WHERE hh_id = %s
            """, (item["employment"], item["schedule"], item["hh_id"]))

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
    details = asyncio.run(fetch_all_details(hh_ids))
    save_skills(details)