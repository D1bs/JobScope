from fastapi import APIRouter, Depends

from src.api.dependencies import get_db

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
def get_skills(conn = Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM vacancy_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 15
    """)

    rows = cursor.fetchall()
    cursor.close()

    return {"skills": [{"name": row[0], "count": int(row[1])} for row in rows]}