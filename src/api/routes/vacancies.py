from fastapi import APIRouter, Depends


from src.api.dependencies import get_db
from src.schemas.vacancies import VacancyFilter

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("")
def get_vacancies(
    conn = Depends(get_db),
    filters: VacancyFilter = Depends(),
):
    cursor = conn.cursor()

    sql = """
        SELECT id, title, company, city, salary_from, salary_to,
               url, employment, schedule, contract_type
        FROM vacancies
    """

    conditions = []
    params = []

    if filters.search:
        conditions.append("(title ILIKE %s OR company ILIKE %s)")
        params.extend([f"%{filters.search}%", f"%{filters.search}%"])

    for column, value in {"city": filters.city, "schedule": filters.schedule, "employment": filters.employment}.items():
        if value:
            conditions.append(f"{column} ILIKE %s")
            params.append(f"%{value}%")

    if filters.salary_min:
        conditions.append("salary_from >= %s")
        params.append(filters.salary_min)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY id DESC LIMIT 100"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()

    keys = ["id", "title", "company", "city", "salary_from",
            "salary_to", "url", "employment", "schedule", "contract_type"]

    return [dict(zip(keys, row)) for row in rows]