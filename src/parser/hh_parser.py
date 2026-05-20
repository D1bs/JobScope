import asyncio
import httpx

from sqlalchemy import delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings
from src.currency import convert_to_byn
from src.models.vacancy import Vacancy, VacancySkill


def get_hh_headers() -> dict:
    return {
        "User-Agent": f"JobScope/1.0 ({settings.HH_CLIENT_ID})",
        "Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}",
    }


def _make_session_factory():
    DATABASE_URL = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    engine = create_async_engine(DATABASE_URL, echo=False)
    return async_sessionmaker(engine, expire_on_commit=False), engine


def fetch_vacancies(query: str, city_id: int) -> list:
    url = "https://api.hh.ru/vacancies"
    all_vacancies = []

    for page in range(10):
        params = {
            "text": query,
            "per_page": 20,
            "page": page,
            "search_field": "name",
        }
        if city_id and city_id != 0:
            params["area"] = city_id

        response = httpx.get(url, params=params, headers=get_hh_headers(), timeout=10.0)
        data = response.json()

        if "items" not in data:
            print(f"[HH ERROR] {data}")
            break

        all_vacancies.extend(data["items"])

        if page >= data.get("pages", 1) - 1:
            break

    return all_vacancies


async def save_vacancies_async(vacancies: list) -> int:
    factory, engine = _make_session_factory()
    saved = 0
    try:
        async with factory() as session:
            for vacancy in vacancies:
                salary        = vacancy.get("salary") or {}
                salary_from   = salary.get("from")
                salary_to     = salary.get("to")
                currency      = salary.get("currency")
                contract_type = vacancy.get("type", {}).get("name")

                stmt = insert(Vacancy).values(
                    hh_id=vacancy["id"],
                    title=vacancy["name"],
                    company=vacancy["employer"]["name"],
                    city=vacancy["area"]["name"],
                    salary_from=salary_from,
                    salary_to=salary_to,
                    currency=currency,
                    salary_from_byn=convert_to_byn(salary_from, currency),
                    salary_to_byn=convert_to_byn(salary_to, currency),
                    url=vacancy["alternate_url"],
                    contract_type=contract_type,
                ).on_conflict_do_nothing(index_elements=["hh_id"])

                result = await session.execute(stmt)
                if result.rowcount == 1:
                    saved += 1

            await session.commit()
    finally:
        await engine.dispose()
    return saved


def save_vacancies(vacancies: list) -> int:
    return asyncio.run(save_vacancies_async(vacancies))


async def fetch_vacancy_details(client: httpx.AsyncClient, hh_id: str) -> dict:
    try:
        response = await client.get(
            f"https://api.hh.ru/vacancies/{hh_id}",
            headers={"Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}"},
            timeout=10.0,
        )
        data = response.json()
        skills = [s["name"] for s in data.get("key_skills", [])]
        work_formats = data.get("work_format") or []
        schedule = ", ".join(f["name"] for f in work_formats) if work_formats else None
        employment = (data.get("employment_form") or {}).get("name")
        return {"hh_id": hh_id, "skills": skills, "employment": employment, "schedule": schedule}
    except Exception:
        return {"hh_id": hh_id, "skills": [], "employment": None, "schedule": None}


async def fetch_and_save_skills_async(hh_ids: list) -> None:
    factory, engine = _make_session_factory()
    try:
        async with httpx.AsyncClient() as client:
            async with factory() as session:
                for hh_id in hh_ids:
                    detail = await fetch_vacancy_details(client, hh_id)

                    if detail["employment"] or detail["schedule"]:
                        await session.execute(
                            update(Vacancy)
                            .where(Vacancy.hh_id == hh_id)
                            .values(employment=detail["employment"], schedule=detail["schedule"])
                        )

                    for skill in detail["skills"]:
                        stmt = insert(VacancySkill).values(
                            vacancy_hh_id=hh_id,
                            skill_name=skill,
                        ).on_conflict_do_nothing()
                        await session.execute(stmt)

                    await asyncio.sleep(0.2)

                await session.commit()
    finally:
        await engine.dispose()


def fetch_and_save_skills(hh_ids: list) -> None:
    asyncio.run(fetch_and_save_skills_async(hh_ids))


async def remove_outdated_vacancies_async(actual_hh_ids: set) -> int:
    if not actual_hh_ids:
        return 0

    factory, engine = _make_session_factory()
    try:
        async with factory() as session:
            result = await session.execute(
                delete(Vacancy).where(Vacancy.hh_id.not_in(actual_hh_ids))
            )
            await session.commit()
            return result.rowcount
    finally:
        await engine.dispose()


def remove_outdated_vacancies(actual_hh_ids: set) -> int:
    return asyncio.run(remove_outdated_vacancies_async(actual_hh_ids))