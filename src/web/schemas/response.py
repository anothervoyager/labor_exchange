from pydantic import BaseModel

class ResponseSchema(BaseModel):
    message: str  # Сообщение отклика

    class Config:
        orm_mode = True  # Позволяет использовать SQLAlchemy модели
