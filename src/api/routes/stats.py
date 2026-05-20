from fastapi import APIRouter, Depends

from src.api.dependencies import get_vacancy_repo
from src.repositories.vacancy_repository import VacancyRepository
from src.schemas.vacancies import VacancyFilter

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats(
    repo: VacancyRepository = Depends(get_vacancy_repo),
    filters: VacancyFilter = Depends(),
):
    count, avg = await repo.get_stats(filters)
    return {
        "total_vacancies": count,
        "avg_salary": round(float(avg), 2) if avg is not None else 0,
    }


@router.get("/salary-distribution")
async def get_salary_distribution(
    repo: VacancyRepository = Depends(get_vacancy_repo),
    filters: VacancyFilter = Depends(),
):
    distribution = await repo.get_salary_distribution(filters)
    return {"distribution": distribution}