from contextlib import AbstractContextManager
from typing import Callable, List, Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from interfaces import IRepositoryAsync
from models import Job as JobModel
from storage.sqlalchemy.tables import Job, Response
from web.schemas import JobCreateSchema

class JobRepository(IRepositoryAsync):
    """
        Репозиторий для работы с сущностью 'Job'.

        Предоставляет методы для создания, извлечения, обновления и удаления записей о вакансиях
        в асинхронном режиме, используя SQLAlchemy для взаимодействия с базой данных.

        Attributes:
            session (Callable[..., AbstractContextManager[Session]]): Функция для создания контекста
            сессии SQLAlchemy.
        """
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, job_create_dto: JobCreateSchema, current_user) -> Job:
        """
        Создает новую запись о вакансии.

        Args:
            job_create_dto (JobCreateSchema): DTO (объект передачи данных) с информацией о вакансии.
            current_user: Пользователь, создающий вакансию.

        Returns:
            Job: Созданная запись о вакансии.
        """
        async with self.session() as session:
            job = Job(
                title=job_create_dto.title,
                description=job_create_dto.description,
                user_id=current_user.id,
                salary_from=job_create_dto.salary_from,
                salary_to=job_create_dto.salary_to,
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def retrieve(self, job_id: int) -> Optional[JobModel]:
        """
                Извлекает запись о вакансии по заданному идентификатору.

                Args:
                    job_id (int): Идентификатор вакансии.

                Returns:
                    Optional[JobModel]: Запись о вакансии, если найдена, иначе None.
                """
        async with self.session() as session:
            query = select(Job).filter_by(id=job_id).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def retrieve_many(self, limit: int = 100, skip: int = 0) -> List[JobModel]:
        """
                Извлекает множество записей о вакансиях .

                Args:
                    limit (int, optional): Максимальное количество вакансий для извлечения. По умолчанию 100.
                    skip (int, optional): Количество записей, которые следует пропустить. По умолчанию 0.

                Returns:
                    List[JobModel]: Список записей о вакансиях.
                """
        async with self.session() as session:
            query = select(Job).limit(limit).offset(skip)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(self, job_id: int, job_update_dto: JobCreateSchema, current_user) -> Job:
        """
        Обновляет запись о вакансии по заданному идентификатору.

        Args:
            job_id (int): Идентификатор вакансии для обновления.
            job_update_dto (JobCreateSchema): DTO с обновленной информацией о вакансии.

        Returns:
            Job: Обновленная запись о вакансии.

        Raises:
            ValueError: Если вакансия с указанным идентификатором не найдена.
        """
        async with self.session() as session:
            job = await session.get(Job, job_id)
            if job is None:
                raise ValueError("Job not found")

            if job.user_id != current_user.id:  # Проверка на владение вакансией
                raise ValueError("You do not have permission to update this job")


            job.title = job_update_dto.title
            job.description = job_update_dto.description
            job.salary_from = job_update_dto.salary_from
            job.salary_to = job_update_dto.salary_to

            await session.commit()
            await session.refresh(job)
            return job

    async def delete(self, job_id: int, current_user) -> None:
        """
        Удаляет запись о вакансии по заданному идентификатору.

        Args:
            job_id (int): Идентификатор вакансии для удаления.
        """
        async with self.session() as session:
            job = await self.retrieve(job_id)
            if job is not None:

                if job.user_id != current_user.id:
                    raise ValueError("You do not have permission to delete this job")


                await session.execute(
                    delete(Response).where(Response.job_id == job_id)
                )


                await session.delete(job)
                await session.commit()
            else:
                raise ValueError("Job not found")
