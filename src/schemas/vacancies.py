from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VacancyFilter:
    search: Optional[str] = None
    city: Optional[str] = None
    schedule: Optional[str] = None
    employment: Optional[str] = None
    salary_min: Optional[int] = None
    offset: int = 0