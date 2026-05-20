from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.repositories.vacancy_repository import VacancyRepository
from fastapi import Depends


async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    yield session


async def get_vacancy_repo(session: AsyncSession = Depends(get_session)) -> VacancyRepository:
    return VacancyRepository(session)