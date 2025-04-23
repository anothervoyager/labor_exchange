from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Response
from interfaces import IRepositoryAsync
from typing import List, Optional


class ResponseRepository(IRepositoryAsync):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, response: Response) -> Response:
        """Сохранить отклик в базе данных."""
        self.db_session.add(response)
        await self.db_session.commit()
        await self.db_session.refresh(response)
        return response

    async def get_all_by_job_id(self, job_id: int) -> List[Response]:
        """Получить все отклики по id вакансии."""
        result = await self.db_session.execute(select(Response).where(Response.job_id == job_id))
        return result.scalars().all()

    async def retrieve(self, response_id: int) -> Optional[Response]:
        """Получить отклик по его ID."""
        result = await self.db_session.execute(select(Response).filter(Response.id == response_id))
        return result.scalars().first()

    async def retrieve_many(self) -> List[Response]:
        """Получить все отклики."""
        result = await self.db_session.execute(select(Response))
        return result.scalars().all()

    async def update(self, response: Response) -> Response:
        """Обновить отклик."""
        # Проверьте, существует ли отклик
        existing_response = await self.retrieve(response.id)
        if existing_response is None:
            raise ValueError(f"Response with id {response.id} not found.")

        # Обновление полей отклика; примите во внимание, что может потребоваться указать конкретные поля
        existing_response.content = response.content  # Пример для одного поля
        self.db_session.add(existing_response)
        await self.db_session.commit()
        return existing_response

    async def delete(self, response_id: int) -> None:
        """Удалить отклик по его ID."""
        response = await self.retrieve(response_id)
        if response is None:
            raise ValueError(f"Response with id {response_id} not found.")

        self.db_session.delete(response)
        await self.db_session.commit()
