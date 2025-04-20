from contextlib import AbstractContextManager
from typing import Callable, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from interfaces import IRepositoryAsync
from models import Job as JobModel
from storage.sqlalchemy.tables import Job
from web.schemas import JobCreateSchema

class JobRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, job_create_dto: JobCreateSchema) -> JobModel:
        async with self.session() as session:
            job = Job(
                title=job_create_dto.title,
                description=job_create_dto.description,
                user_id=job_create_dto.user_id,
                salary_from=job_create_dto.salary_from,
                salary_to=job_create_dto.salary_to
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def retrieve(self, job_id: int) -> Optional[JobModel]:
        async with self.session() as session:
            query = select(Job).filter_by(id=job_id).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def retrieve_many(self, limit: int = 100, skip: int = 0) -> List[JobModel]:
        async with self.session() as session:
            query = select(Job).limit(limit).offset(skip)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(self, job_id: int, job_update_dto: JobCreateSchema) -> JobModel:
        async with self.session() as session:
            job = await self.retrieve(job_id)
            if job is None:
                raise ValueError("Job not found")
            job.title = job_update_dto.title
            job.description = job_update_dto.description
            job.user_id = job_update_dto.user_id
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def delete(self, job_id: int) -> None:
        async with self.session() as session:
            job = await self.retrieve(job_id)
            if job is not None:
                await session.delete(job)
                await session.commit()
