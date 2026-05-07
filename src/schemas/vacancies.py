from fastapi import Query
from dataclasses import dataclass


@dataclass
class VacancyFilter:
    search: str = Query(None)
    city: str = Query(None)
    schedule: str = Query(None)
    employment: str = Query(None)
    salary_min: int = Query(None, ge=0)
    offset: int = Query(0, ge=0)