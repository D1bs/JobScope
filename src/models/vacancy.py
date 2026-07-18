from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[intpk]
    hh_id: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    salary_from: Mapped[int | None]
    salary_to: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(10))
    salary_from_byn: Mapped[int | None]
    salary_to_byn: Mapped[int | None]
    url: Mapped[str] = mapped_column(Text)
    employment: Mapped[str | None] = mapped_column(String(100))
    schedule: Mapped[str | None] = mapped_column(String(200))
    contract_type: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    id: Mapped[intpk]
    vacancy_hh_id: Mapped[str] = mapped_column(String(50))
    skill_name: Mapped[str] = mapped_column(String(100))