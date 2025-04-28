from contextlib import AbstractContextManager
from typing import Callable, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from interfaces import IRepositoryAsync
from models import Response as ResponseModel
from storage.sqlalchemy.tables.responses import Response
from web.schemas import ResponseCreateSchema


class ResponseRepository(IRepositoryAsync):
    """
    Репозиторий для работы с сущностью 'Response'.

    Предоставляет методы для создания, извлечения, обновления и удаления откликов
    в асинхронном режиме, используя SQLAlchemy для взаимодействия с базой данных.

    Attributes:
        session (Callable[..., AbstractContextManager[Session]]): Функция для создания контекста
        сессии SQLAlchemy.
    """
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, response_create_dto: ResponseCreateSchema, current_user) -> ResponseModel:
        """
        Создает новый отклик на вакансию.

        Args:
            response_create_dto (ResponseCreateSchema): DTO (объект передачи данных) с информацией об отклике.

        Returns:
            ResponseModel: Созданный отклик.
        """
        async with self.session() as session:
            response = Response(
                user_id=response_create_dto.user_id,
                job_id=response_create_dto.job_id,
                message=response_create_dto.message
            )
            session.add(response)
            await session.commit()
            await session.refresh(response)
            return response

    async def retrieve(self, response_id: int) -> Optional[ResponseModel]:
        """
        Извлекает отклик по заданному идентификатору.

        Args:
            response_id (int): Идентификатор отклика.

        Returns:
            Optional[ResponseModel]: Отклик, если найден, иначе None.
        """
        async with self.session() as session:
            query = select(Response).filter_by(id=response_id).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def retrieve_many(self) -> List[ResponseModel]:
        """
        Извлекает все отклики.

        Returns:
            List[ResponseModel]: Список откликов.
        """
        async with self.session() as session:
            query = select(Response)
            result = await session.execute(query)
            return result.scalars().all()

    async def retrieve_many_by_user_id(self, user_id: int) -> List[ResponseModel]:
        async with self.session() as session:
            query = select(Response).filter(Response.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_all_by_job_id(self, job_id: int) -> List[ResponseModel]:
        """
        Получает все отклики по идентификатору вакансии.

        Args:
            job_id (int): Идентификатор вакансии.

        Returns:
            List[ResponseModel]: Список откликов для заданной вакансии.
        """
        async with self.session() as session:
            query = select(Response).filter(Response.job_id == job_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(self, response_id: int, response_update_dto: ResponseCreateSchema, current_user) -> ResponseModel:
        """
        Обновляет отклик по заданному идентификатору.

        Args:
            response_id (int): Идентификатор отклика для обновления.
            response_update_dto (ResponseCreateSchema): DTO с обновленной информацией об отклике.

        Returns:

        ResponseModel: Обновленный отклик.

        Raises:
            ValueError: Если отклик с указанным идентификатором не найден.
        """

        async with self.session() as session:
            response = await self.retrieve(response_id)
            if response is None:
                raise ValueError("Response not found")
            if response.user_id != current_user.id: #проверка на текущего пользователя
                raise HTTPException(status_code=403, detail="You do not have permission to update this response")
            response.message = response_update_dto.message
            session.add(response)
            await session.commit()
            await session.refresh(response)
            return response


    async def delete(self, response_id: int, current_user) -> None:
        """
        Удаляет отклик по заданному идентификатору.

        Args:
            response_id (int): Идентификатор отклика для удаления.
        """
        async with self.session() as session:
            response = await self.retrieve(response_id)
            if response is not None:
                if response.user_id != current_user.id:
                    raise HTTPException(status_code=403, detail="You do not have permission to delete this response")
                await session.delete(response)
                await session.commit()
