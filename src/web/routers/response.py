from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from models import User
from web.schemas.response import ResponseSchema, ResponseCreateSchema, ResponseUpdateSchema
from repositories import ResponseRepository, JobRepository
from dependencies.containers import RepositoriesContainer
from dependencies import get_current_user

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_response(
        response_data: ResponseCreateSchema,
        current_user: User = Depends(get_current_user),
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository]),
        job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
):
    # Проверка на то, что пользователь не является компанией
    if current_user.is_company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Companies are not allowed to create responses.")

    job = await job_repository.retrieve(response_data.job_id)

    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    new_response = await response_repository.create(
        response_create_dto=response_data.copy(update={"user_id": current_user.id}),
        current_user=current_user
    )

    return new_response

@router.get("/{response_id}", response_model=ResponseSchema)
@inject
async def read_response(
        response_id: int,
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository])
):
    response = await response_repository.retrieve(response_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")
    return response

@router.get("/", response_model=list[ResponseSchema])
@inject
async def read_all_responses(
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository])
):
    responses = await response_repository.retrieve_many()
    return responses

@router.get("/job/{job_id}", response_model=list[ResponseSchema])
@inject
async def read_responses_by_job_id(
        job_id: int,
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository])
):
    responses = await response_repository.get_all_by_job_id(job_id)
    return responses

@router.put("/{response_id}", response_model=ResponseSchema)
@inject
async def update_response(
        response_id: int,
        response_data: ResponseUpdateSchema,
        current_user: User = Depends(get_current_user),  # Получаем текущего пользователя
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository])
):
    # Проверка на то, что пользователь не является компанией
    if current_user.is_company:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Companies are not allowed to update responses.")

    existing_response = await response_repository.retrieve(response_id)
    if existing_response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")

    updated_response = await response_repository.update(response_id, response_data, current_user=current_user)

    return updated_response


@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_response(
        response_id: int,
        response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository])
):
    existing_response = await response_repository.retrieve(response_id)
    if existing_response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")

    await response_repository.delete(response_id)
