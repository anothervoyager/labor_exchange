from pydantic import BaseModel

class ResponseSchema(BaseModel):
    message: str
    user_id: int
    timestamp: str
    class Config:
        orm_mode = True
