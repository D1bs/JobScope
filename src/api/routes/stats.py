from fastapi import APIRouter, Depends
from src.api.dependencies import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(salary_from_byn) FROM vacancies")
    row = cursor.fetchone()
    cursor.close()

    avg = round(float(row[1]), 2) if row[1] is not None else 0

    return {
        "total_vacancies": row[0],
        "avg_salary": avg
    }


@router.get("/salary-distribution")
def get_salary_distribution(conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) FILTER (WHERE salary_from_byn < 1000)                            AS "0–1k",
            COUNT(*) FILTER (WHERE salary_from_byn >= 1000 AND salary_from_byn < 3000) AS "1–3k",
            COUNT(*) FILTER (WHERE salary_from_byn >= 3000 AND salary_from_byn < 6000) AS "3–6k",
            COUNT(*) FILTER (WHERE salary_from_byn >= 6000 AND salary_from_byn < 10000) AS "6–10k",
            COUNT(*) FILTER (WHERE salary_from_byn >= 10000)                           AS "10k+"
        FROM vacancies
        WHERE salary_from_byn IS NOT NULL
    """)
    row = cursor.fetchone()
    cursor.close()

    labels = ["0–1k", "1–3k", "3–6k", "6–10k", "10k+"]
    return {"distribution": dict(zip(labels, row))}