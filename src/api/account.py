from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from src.database.models import Account
from src.database.models import User
from src.dependencies.auth_dependencies import get_current_user
from src.dependencies.basic_dependencies import get_account_service
from src.schemas.schemas import ShowAccountSchema
from src.services.services import AccountService

account_router: APIRouter = APIRouter(
    prefix="/account",
    tags=[
        "account",
    ],
)


@account_router.get("/current-user", response_model=List[ShowAccountSchema])
async def get_current_user_accounts(
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> List[Account]:
    """
    Обработчик, отвечающий за получение своих счетов текущим пользователем. Данные о пользователе берутся
    из заголовков запроса

    В случае, если запрос на получение своего счета пытается сделать администратор, возникает исключение с кодом 403

    В случае, если у текущего пользователя нет ни одного счета, то возникает исключение с кодом 404

    В противном случае обработчик возвращает данные о счетах пользователя (их id и баланс)
    """

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin cannot have an account"
        )

    accounts: List[Account] = await service.get_current_user_accounts(user=user)
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current user has no accounts",
        )

    return accounts


@account_router.get("/", response_model=List[ShowAccountSchema])
async def get_accounts_by_user_id(
    user_id: int,
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> List[Account]:
    """
    Обработчик, отвечающий за получение счетов пользователя с указанным id администратором

    В случае, если запрос совершает не администратор или администратор пытается
    получить счета администратора, то возникает исключение с кодом 403

    В случае, если у пользователя с указанным id нет ни одного счета или пользователя с таким id не существует
    , то возникает исключение с кодом 404

    В противном случае обработчик возвращает данные о счетах пользователя (их id и баланс)
    """

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can get another user accounts",
        )
    try:
        accounts: List[Account] = await service.get_accounts_by_user_id(user_id=user_id)
        if not accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this id has no accounts",
            )

        return accounts

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot get another admin data",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found"
        )
