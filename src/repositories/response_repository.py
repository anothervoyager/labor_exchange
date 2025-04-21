from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models import Response


class ResponseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, response: Response) -> Response:
        """Сохраняет отклик в базе данных.

        Args:
            response (Response): Объект отклика для сохранения.

        Returns:
            Response: Сохраненный отклик из базы данных.

        Raises:
            Exception: Если возникает ошибка при сохранении.
        """
        try:
            self.db_session.add(response)
            await self.db_session.commit()
            await self.db_session.refresh(response)
            return response
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise Exception("Ошибка при сохранении отклика в базе данных.") from e

    async def get_all_by_job_id(self, job_id: int) -> list[Response]:
        """Получает все отклики по идентификатору вакансии.

        Args:
            job_id (int): Идентификатор вакансии.

        Returns:
            list[Response]: Список откликов на указанную вакансию.

        Raises:
            Exception: Если возникает ошибка при получении данных.
        """
        try:
            result = await self.db_session.execute(select(Response).where(Response.job_id == job_id))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise Exception("Ошибка при получении откликов из базы данных.") from e
