from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    id: int
    title: str
    description: str
    user_id: int  # Чтобы ссылаться на пользователя, создавшего эту работу
    salary_from: Optional[float] = field(default=None)  # Минимальная зарплата, может быть пустым
    salary_to: Optional[float] = field(default=None)  # Максимальная зарплата, может быть пустым
    users: list["User"] = field(default_factory=list)