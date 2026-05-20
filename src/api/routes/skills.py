from fastapi import APIRouter, Depends

from src.api.dependencies import get_vacancy_repo
from src.repositories.vacancy_repository import VacancyRepository
from src.schemas.vacancies import VacancyFilter

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
async def get_skills(
    repo: VacancyRepository = Depends(get_vacancy_repo),
    filters: VacancyFilter = Depends(),
):
    skills = await repo.get_top_skills(filters)
    return {"skills": skills}