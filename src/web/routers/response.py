from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from models import Response, User
from web.schemas.response import ResponseSchema
from repositories import ResponseRepository, JobRepository
from dependencies.containers import RepositoriesContainer
from dependencies import get_current_user

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/jobs/{job_id}", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_response(
    job_id: int,
    response_data: ResponseSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository]),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
):
    """
    Создает отклик на вакансию.

    Args:
        job_id (int): Идентификатор вакансии.
        response_data (ResponseSchema): DTO с данными отклика.
        current_user (User): Текущий пользователь.
        response_repository (ResponseRepository): Репозиторий для работы с откликами.
        job_repository (JobRepository): Репозиторий для работы с вакансиями.

    Returns:
        Response: Созданный отклик на вакансию.

    Raises:
        HTTPException: Если вакансия не найдена.
    """
    job = await job_repository.retrieve(job_id)

    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    new_response = Response(
        user_id=current_user.id,
        job_id=job_id,
        message=response_data.message
    )

    await response_repository.create(new_response)

    return new_response
