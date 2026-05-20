from sqlalchemy import select, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.vacancy import Vacancy, VacancySkill
from src.schemas.vacancies import VacancyFilter


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, filters: VacancyFilter) -> tuple[list[Vacancy], bool]:
        PAGE_SIZE = 50
        query = select(Vacancy)

        if filters.search:
            query = query.where(
                Vacancy.title.ilike(f"%{filters.search}%") |
                Vacancy.company.ilike(f"%{filters.search}%")
            )
        if filters.city:
            query = query.where(Vacancy.city.ilike(f"%{filters.city}%"))
        if filters.schedule:
            query = query.where(Vacancy.schedule.ilike(f"%{filters.schedule}%"))
        if filters.employment:
            query = query.where(Vacancy.employment.ilike(f"%{filters.employment}%"))
        if filters.salary_min:
            query = query.where(Vacancy.salary_from >= filters.salary_min)

        query = query.order_by(Vacancy.id.desc()).offset(filters.offset).limit(PAGE_SIZE + 1)

        result = await self.session.execute(query)
        vacancies = result.scalars().all()

        has_more = len(vacancies) > PAGE_SIZE
        return list(vacancies[:PAGE_SIZE]), has_more

    async def get_stats(self, filters: VacancyFilter) -> tuple[int, float]:
        query = select(func.count(), func.avg(Vacancy.salary_from_byn))

        if filters.search:
            query = query.where(
                Vacancy.title.ilike(f"%{filters.search}%") |
                Vacancy.company.ilike(f"%{filters.search}%")
            )
        if filters.schedule:
            query = query.where(Vacancy.schedule.ilike(f"%{filters.schedule}%"))
        if filters.employment:
            query = query.where(Vacancy.employment.ilike(f"%{filters.employment}%"))
        if filters.salary_min:
            query = query.where(Vacancy.salary_from_byn >= filters.salary_min)

        result = await self.session.execute(query)
        row = result.one()
        return row[0], row[1]

    async def get_salary_distribution(self, filters: VacancyFilter) -> dict:
        query = select(
            func.count().filter(Vacancy.salary_from_byn < 1000).label("0-1k"),
            func.count().filter(Vacancy.salary_from_byn.between(1000, 2999)).label("1-3k"),
            func.count().filter(Vacancy.salary_from_byn.between(3000, 5999)).label("3-6k"),
            func.count().filter(Vacancy.salary_from_byn.between(6000, 9999)).label("6-10k"),
            func.count().filter(Vacancy.salary_from_byn >= 10000).label("10k+"),
        ).where(Vacancy.salary_from_byn.isnot(None))

        result = await self.session.execute(query)
        row = result.one()
        return {
            "0–1k": row[0],
            "1–3k": row[1],
            "3–6k": row[2],
            "6–10k": row[3],
            "10k+": row[4],
        }

    async def get_top_skills(self, filters: VacancyFilter, limit: int = 15) -> list:
        join_query = (
            select(VacancySkill.skill_name, func.count().label("count"))
            .join(Vacancy, Vacancy.hh_id == VacancySkill.vacancy_hh_id)
        )

        if filters.search:
            join_query = join_query.where(
                Vacancy.title.ilike(f"%{filters.search}%") |
                Vacancy.company.ilike(f"%{filters.search}%")
            )
        if filters.schedule:
            join_query = join_query.where(Vacancy.schedule.ilike(f"%{filters.schedule}%"))
        if filters.employment:
            join_query = join_query.where(Vacancy.employment.ilike(f"%{filters.employment}%"))

        join_query = join_query.group_by(VacancySkill.skill_name).order_by(text("count DESC")).limit(limit)

        result = await self.session.execute(join_query)
        return [{"name": row[0], "count": row[1]} for row in result.all()]