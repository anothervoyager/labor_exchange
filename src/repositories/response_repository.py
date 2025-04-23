from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Response
from interfaces import IRepositoryAsync

class ResponseRepository(IRepositoryAsync):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, response: Response) -> Response:
        """Сохранить отклик в базе данных."""
        self.db_session.add(response)
        await self.db_session.commit()
        await self.db_session.refresh(response)
        return response

    async def get_all_by_job_id(self, job_id: int):
        """Получить все отклики по id вакансии."""
        result = await self.db_session.execute(select(Response).where(Response.job_id == job_id))
        return result.scalars().all()

    async def retrieve(self, response_id: int) -> Response:
        result = await self.db_session.execute(select(Response).filter(Response.id == response_id))
        return result.scalars().first()

    async def update(self, response: Response):
        self.db_session.add(response)
        await self.db_session.commit()

    async def delete(self, response_id: int):
        response = await self.retrieve(response_id)
        await self.db_session.delete(response)
        await self.db_session.commit()