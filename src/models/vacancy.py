from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hh_id: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    salary_from_byn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to_byn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(Text)
    employment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vacancy_hh_id: Mapped[str] = mapped_column(String(50))
    skill_name: Mapped[str] = mapped_column(String(100))