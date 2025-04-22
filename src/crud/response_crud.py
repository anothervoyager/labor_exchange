from sqlalchemy.ext.asyncio import AsyncSession
from storage.sqlalchemy.tables import Response
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound


async def response_job(db: AsyncSession, user_id: int, job_id: int, message: str):
    new_response = Response(user_id=user_id, job_id=job_id, message=message)
    db.add(new_response)
    await db.commit()
    await db.refresh(new_response)
    return new_response

async def get_response_by_user_id(db: AsyncSession, job_id: int):
    result = await db.execute(select(Response).where(Response.job_id == job_id))
    return result.scalars().all()

async def update_response(db: AsyncSession, response_id: int, response_update_data):
    response = await db.get(Response, response_id)
    if response is None:
        raise NoResultFound("Response not found")

    for key, value in response_update_data.items():
        setattr(response, key, value)

    await db.commit()
    await db.refresh(response)
    return response

async def delete_response(db: AsyncSession, response_id: int):
    response = await db.get(Response, response_id)
    if response is None:
        raise NoResultFound("Response not found")

    await db.delete(response)
    await db.commit()
    return response
