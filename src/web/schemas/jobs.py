from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel

class JobCreateSchema(BaseModel):
    title: str
    description: str
    user_id: int
    salary_from: float = None
    salary_to: float = None


class JobSchema(JobCreateSchema):
    id: int

class ResponseSchema(BaseModel):
    user_id: int
    message: str
