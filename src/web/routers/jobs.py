from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from models import Response, User, Job
from web.schemas.response import ResponseSchema
from web.schemas.jobs import JobCreateSchema, JobSchema
from repositories import JobRepository, ResponseRepository
from dependencies.containers import RepositoriesContainer
from dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_job(
    job_create_dto: JobCreateSchema,
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:
    """
    Создает новую запись о вакансии.

    Args:
        job_create_dto (JobCreateSchema): DTO с данными для создания вакансии.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.

    Returns:
        JobSchema: Созданная запись о вакансии.

    Raises:
        HTTPException: При ошибках валидации или создании вакансии.
    """

    if not current_user.is_company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only company users can create jobs")

    try:
        job = await job_repository.create(job_create_dto, current_user)
        return job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating job: {str(e)}")

@router.get("", response_model=list[JobSchema])
@inject
async def read_jobs(
    limit: int = 100,
    skip: int = 0,
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
) -> list[JobSchema]:
    """
    Извлекает список вакансий с поддержкой пагинации.

    Args:
        limit (int, optional): Максимальное количество вакансий для извлечения. По умолчанию 100.
        skip (int, optional): Количество записей, которые следует пропустить. По умолчанию 0.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.

    Returns:
        list[JobSchema]: Список записей о вакансиях.

    Raises:
        HTTPException: При ошибках извлечения вакансий.
    """
    try:
        jobs = await job_repository.retrieve_many(limit, skip)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving jobs: {str(e)}")

@router.get("/{job_id}", response_model=JobSchema)
@inject
async def read_job(
    job_id: int,
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
) -> JobSchema:
    """
    Извлекает вакансию по заданному идентификатору.

    Args:
        job_id (int): Идентификатор вакансии.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.

    Returns:
        JobSchema: Запись о вакансии.

    Raises:
        HTTPException: Если вакансия не найдена.
    """
    job = await job_repository.retrieve(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobSchema)
@inject
async def update_job(
        job_id: int,
        job_update_dto: JobCreateSchema,
        job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
        current_user: User = Depends(get_current_user),
) -> JobSchema:
    """
    Обновляет запись о вакансии по заданному идентификатору.

    Args:
        job_id (int): Идентификатор вакансии для обновления.
        job_update_dto (JobCreateSchema): DTO с обновленной информацией о вакансии.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.
        current_user (User): Пользователь, выполняющий запрос.

    Returns:
        JobSchema: Обновленная запись о вакансии.

    Raises:
        HTTPException: Если вакансия не найдена или при других ошибках.
    """

    if not current_user.is_company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only company users can update jobs")



    try:
        updated_job = await job_repository.update(job_id, job_update_dto,
                                                  current_user)
        return updated_job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating job: {str(e)}")


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_job(
        job_id: int,
        job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
        current_user: User = Depends(get_current_user),
) -> None:
    """
    Удаляет запись о вакансии по заданному идентификатору.

    Args:
        job_id (int): Идентификатор вакансии для удаления.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.
        current_user (User): Пользователь, выполняющий запрос.

    Raises:
        HTTPException: Если вакансия не найдена или при других ошибках.
    """

    if not current_user.is_company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only company users can delete jobs")

    try:
        await job_repository.delete(job_id, current_user)  # Передаем current_user в метод delete
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting job: {str(e)}")