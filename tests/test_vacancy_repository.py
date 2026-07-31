from sqlalchemy import insert
from src.models.vacancy import Vacancy
from src.repositories.vacancy_repository import VacancyRepository
from src.schemas.vacancies import VacancyFilter


async def test_get_all_empty(session):
    repo = VacancyRepository(session)
    items, has_more = await repo.get_all(VacancyFilter())
    assert items == []
    assert has_more is False


async def test_get_all_with_data(session):
    stmt = insert(Vacancy).values(
        hh_id="123", title="Python Developer",
        company="Test Corp", city="Minsk",
        url="https://example.com/123",
    )
    await session.execute(stmt)
    await session.commit()

    repo = VacancyRepository(session)
    items, has_more = await repo.get_all(VacancyFilter())
    assert len(items) == 1
    assert items[0].title == "Python Developer"
    assert has_more is False


async def test_get_all_filter_by_search(session):
    for hh_id, title in [("1", "Python dev"), ("2", "Java dev")]:
        stmt = insert(Vacancy).values(hh_id=hh_id, title=title, company="C", city="Minsk", url=f"https://example.com/{hh_id}")
        await session.execute(stmt)
    await session.commit()

    repo = VacancyRepository(session)
    items, _ = await repo.get_all(VacancyFilter(search="Python"))
    assert len(items) == 1
    assert items[0].title == "Python dev"