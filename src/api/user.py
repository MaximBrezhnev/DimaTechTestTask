from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from src.database.models import User
from src.dependencies.auth_dependencies import get_current_user
from src.dependencies.basic_dependencies import get_user_service
from src.schemas.schemas import ShowUserSchema
from src.schemas.schemas import UserCreationSchema
from src.schemas.schemas import UserUpdateSchema
from src.services.services import UserService

user_router: APIRouter = APIRouter(
    prefix="/user",
    tags=[
        "user",
    ],
)


@user_router.get("/", response_model=ShowUserSchema)
async def get_user_by_id(
    user_id: int,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Обработчик, отвечающий за получение пользователя по id

    В случае, если запрос на получение делает не администратор или происходит
    попытка получить данные администратора, возникает исключение с кодом 403

    В случае, если пользователя с таким id не существует, возникает исключение с кодом 404

    В противном случае, обработчик возвращает информацию о пользователе (id, почта, имя)
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can get user data"
        )

    try:
        user: User = await service.get_user(user_id=user_id)
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot get another admin data",
        )


@user_router.get("/current-user", response_model=ShowUserSchema)
async def get_current_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Обработчик, отвечающий за получение данных текущего авторизованного пользователя. Получение информации происходит
    на основании заголовков запроса
    """

    return user


@user_router.delete("/")
async def delete_user(
    user_id: int,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> JSONResponse:
    """
    Обработчик, отвечающий за удаление пользователя по id

    В случае, если запрос на удаление совершает не администратор или происходит попытка удаления администратора,
    возникает исключение с кодом 403

    В случае, если пользователя с указанным id не существует, возникает исключение с кодом 404

    В противном случае происходит удаление пользователя из базы данных и
    возвращается сообщение об этом
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete users"
        )

    try:
        await service.delete_user(user_id=user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"User with {user_id} was successfully deleted"},
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot delete another admin",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found"
        )


@user_router.post("/", response_model=ShowUserSchema)
async def create_user(
    body: UserCreationSchema,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Обработчик, отвечающий за создание пользователя

    В случае, если запрос на создание делает не администратор, возникает исключение с кодом 403

    В случае, если пользователь с указанным e-mail уже существует, возникает исключение с кодом 409

    В противном случае, в базе данных создается новый пользователь, а информация об этом пользователе возвращается
    обработчиком
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create users"
        )
    try:
        new_user: User = await service.create_user(
            full_name=body.full_name, email=body.email, password=body.password1
        )
        return new_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@user_router.patch("/", response_model=ShowUserSchema)
async def update_user(
    user_id: int,
    body: UserUpdateSchema,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Обработчик, отвечающий за обновление информации о пользователе

    Если на вход не поступило ни одного параметра для изменения, возникает исключение с кодом 422

    Если запрос на обновление совершает не администратор или происходит попытка обновить администратора, возникает
    исключение с кодом 403

    Если пользователь с указанным id не существует, то возникает исключение с кодом 404

    Если при попытке смены e-mail оказывается, что пользователь с такой электронной почтой уже существует,
    возникает исключение с кодом 409

    В случае, если никаких исключений не возникло, обработчик возвращает обновленную информацию о пользователе
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can update users"
        )

    parameters_for_update = body.model_dump(exclude_none=True)
    if not parameters_for_update:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one parameter must be provided",
        )

    try:
        updated_user: User = await service.update_user(
            user_id=user_id, parameters_for_update=parameters_for_update
        )
        return updated_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot update another admin",
        )


@user_router.get("/list-of-users", response_model=List[ShowUserSchema])
async def get_users(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> List[User]:
    """
    Обработчик, возвращающий список всех пользователей (не являющихся администраторами)

    В случае, если запрос совершается не администратором, возникает исключение с кодом 403

    В случае, если не существует ни одного пользователя, не являющегося администратором, возникает исключение с
    кодом 404

    В противном случае возвращается список с информацией о пользователях (id, почта, имя)
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can get list of users",
        )

    users: List[User] = await service.get_users()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No non-admin users"
        )

    return users
