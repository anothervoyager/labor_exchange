from sqlalchemy.ext.asyncio import AsyncSession
from storage.sqlalchemy.tables import Job
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound


async def create_job(db: AsyncSession, job_schema):
    new_job = Job(**job_schema.dict())  # Предполагается, что job_schema - это Pydantic модель
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job

async def get_all_jobs(db: AsyncSession, limit: int = 100, skip: int = 0):
    result = await db.execute(select(Job).offset(skip).limit(limit))
    return result.scalars().all()

async def get_job_by_id(db: AsyncSession, job_id: int):
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()

async def update_job(db: AsyncSession, job_id: int, job_update_data):
    job = await get_job_by_id(db, job_id)
    if job is None:
        raise NoResultFound("Job not found")

    for key, value in job_update_data.items():
        setattr(job, key, value)

    await db.commit()
    await db.refresh(job)
    return job

async def delete_job(db: AsyncSession, job_id: int):
    job = await get_job_by_id(db, job_id)
    if job is None:
        raise NoResultFound("Job not found")

    await db.delete(job)
    await db.commit()
    return job
