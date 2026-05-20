from fastapi import APIRouter, Depends

from src.api.dependencies import get_vacancy_repo
from src.repositories.vacancy_repository import VacancyRepository
from src.schemas.vacancies import VacancyFilter

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("")
async def get_vacancies(
    repo: VacancyRepository = Depends(get_vacancy_repo),
    filters: VacancyFilter = Depends(),
):
    vacancies, has_more = await repo.get_all(filters)
    return {
        "items": [
            {
                "id": v.id,
                "title": v.title,
                "company": v.company,
                "city": v.city,
                "salary_from": v.salary_from,
                "salary_to": v.salary_to,
                "salary_from_byn": v.salary_from_byn,
                "salary_to_byn": v.salary_to_byn,
                "currency": v.currency,
                "url": v.url,
                "employment": v.employment,
                "schedule": v.schedule,
                "contract_type": v.contract_type,
            }
            for v in vacancies
        ],
        "has_more": has_more,
        "offset": filters.offset,
    }