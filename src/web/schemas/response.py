from pydantic import BaseModel

class ResponseSchema(BaseModel):
    message: str

    class Config:
        orm_mode = True
