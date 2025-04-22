from pydantic import BaseModel

class ResponseSchema(BaseModel):
    user_id: int
    job_id: int
    message: str

    class Config:
        orm_mode = True
