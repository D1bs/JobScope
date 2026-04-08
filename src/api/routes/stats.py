from fastapi import APIRouter, Depends

from src.api.dependencies import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(conn = Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), AVG(salary_from) FROM vacancies")

    row = cursor.fetchone()
    cursor.close()

    avg = round(float(row[1]), 2) if row[1] is not None else 0

    return {
        "total_vacancies": row[0],
        "avg_salary": avg
    }