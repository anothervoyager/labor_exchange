from dataclasses import asdict
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from tools.security import hash_password
from web.schemas import UserCreateSchema, UserSchema, UserUpdateSchema

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@inject
async def get_user_by_id(db, user_id: int) -> User:
    """
    Получает пользователя по идентификатору.
    :param db: Сессия базы данных.
    :param user_id: Идентификатор пользователя.
    :return: Пользователь.
    """
    user_repository: UserRepository = Provide[RepositoriesContainer.user_repository]
    user = await user_repository.retrieve_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found.")
    return user


@router.get("")
@inject
async def read_users(
        limit: int = 100,
        skip: int = 0,
        user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> list[UserSchema]:
    users_model = await user_repository.retrieve_many(limit, skip)

    users_schema = [UserSchema(id=model.id, name=model.name, email=model.email, is_company=model.is_company) for model
                    in users_model]

    logger.info("Retrieved users list.")

    return users_schema


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
        user_create_dto: UserCreateSchema,
        user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema:
    user = await user_repository.create(
        user_create_dto, hashed_password=hash_password(user_create_dto.password)
    )
    logger.info(f"User created: {user.email}")
    return UserSchema(**asdict(user))


@router.put("")
@inject
async def update_user(
        user_update_schema: UserUpdateSchema,
        user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
        current_user: User = Depends(get_current_user),
) -> UserSchema:
    existing_user = await user_repository.retrieve(email=user_update_schema.email)

    if existing_user and existing_user.id != current_user.id:
        logger.warning(f"Unauthorized access attempt by user {current_user.id} to update user {existing_user.id}.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")

    try:
        updated_user = await user_repository.update(current_user.id, user_update_schema)
        logger.info(f"User updated: {updated_user.email}")
        return UserSchema(**asdict(updated_user))

    except ValueError:
        logger.error(f"User with ID {current_user.id} not found for updating.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
