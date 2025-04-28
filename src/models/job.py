from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    id: int
    title: str
    description: str
    user_id: int
    salary_from: Optional[float] = field(default=None)
    salary_to: Optional[float] = field(default=None)
    users: list["User"] = field(default_factory=list)