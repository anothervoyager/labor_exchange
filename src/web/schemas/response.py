from pydantic import BaseModel

class ResponseCreateSchema(BaseModel):
    job_id: int
    message: str

class ResponseUpdateSchema(BaseModel):
    message: str

class ResponseSchema(ResponseCreateSchema):
    id: int
    user_id: int
