from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel

class JobCreateSchema(BaseModel):
    title: str
    description: str
    salary_from: float = None
    salary_to: float = None


class JobSchema(JobCreateSchema):
    id: int

