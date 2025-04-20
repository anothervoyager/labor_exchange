from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from models import Response, User, Job  # Импортируйте свои модели
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
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
) -> JobSchema:
    try:
        job = await job_repository.create(job_create_dto)
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
    job = await job_repository.retrieve(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobSchema)
@inject
async def update_job(
    job_id: int,
    job_update_dto: JobCreateSchema,
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
) -> JobSchema:
    try:
        updated_job = await job_repository.update(job_id, job_update_dto)
        return updated_job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating job: {str(e)}")

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_job(
    job_id: int,
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
) -> None:
    try:
        await job_repository.delete(job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting job: {str(e)}")

@router.post("/{job_id}/responses", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_response(
    job_id: int,
    response_data: ResponseSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(Provide[RepositoriesContainer.response_repository]),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository])
):
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
