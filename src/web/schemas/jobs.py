from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel

class JobCreateSchema(BaseModel):
    title: str
    description: str
    user_id: int  # Измените это поле на user_id
    salary_from: float = None  # Вы можете добавить по желанию
    salary_to: float = None  # Вы можете добавить по желанию


class JobSchema(JobCreateSchema):
    id: int  # Идентификатор вакансии.

class ResponseSchema(BaseModel):
    user_id: int
    message: str  # Сообщение отклика.
