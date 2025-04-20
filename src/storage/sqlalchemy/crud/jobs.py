from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from storage.sqlalchemy.tables import Job, Response
from sqlalchemy.exc import NoResultFound
from web.routers.user import get_user_by_id


async def create_job(db: AsyncSession, job_schema):
    """
    Создает новую вакансию в БД.
    :param db: Сессия базы данных.
    :param job_schema: Данные вакансии (например, название, описание и т.д.).
    """
    new_job = Job(**job_schema)  # Создаем новую запись вакансии
    db.add(new_job)  # Добавляем запись в сессию
    await db.commit()  # Фиксируем изменения
    await db.refresh(new_job)  # Обновляем данные объекта
    return new_job


async def get_all_jobs(db: AsyncSession, limit: int = 100, skip: int = 0):
    """
    Получает все вакансии из БД с возможностью пагинации.
    :param db: Сессия базы данных.
    :param limit: Максимальное количество вакансий для возврата.
    :param skip: Количество пропускаемых вакансий.
    """
    result = await db.execute(select(Job).limit(limit).offset(skip))
    jobs = result.scalars().all()  # Получаем все вакансии
    return jobs


async def get_job_by_id(db: AsyncSession, job_id: int):
    """
    Получает вакансию по идентификатору.
    :param db: Сессия базы данных.
    :param job_id: Идентификатор вакансии.
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()  # Возвращает единственную запись или None
    if job is None:
        raise NoResultFound(f"Job with id {job_id} not found.")
    return job


async def response_job(db: AsyncSession, job_id: int, user_id: int, message: str):
    """
    Откликается на вакансию.
    :param db: Сессия базы данных.
    :param job_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя, откликающегося на вакансию.
    :param message: Сообщение отклика.
    """
    # Проверяем, существует ли пользователь
    user = await get_user_by_id(db, user_id)  # Использование новой функции

    # Проверяем, что пользователь является соискателем
    if user.role != 'candidate':
        raise HTTPException(status_code=403, detail="Only candidates can apply for jobs.")

    # Проверяем, существует ли вакансия
    job = await get_job_by_id(db, job_id)

    # Создаем новый отклик
    new_response = Response(user_id=user_id, job_id=job_id, message=message)
    db.add(new_response)  # Добавляем отклик в сессию
    await db.commit()  # Фиксируем изменения
    await db.refresh(new_response)  # Обновляем данные объекта
    return new_response


async def get_response_by_job_id(db: AsyncSession, job_id: int):
    """
    Получает отклики по идентификатору вакансии.
    :param db: Сессия базы данных.
    :param job_id: Идентификатор вакансии.
    """
    result = await db.execute(select(Response).where(Response.job_id == job_id))
    responses = result.scalars().all()  # Получаем все отклики к вакансии
    return responses
