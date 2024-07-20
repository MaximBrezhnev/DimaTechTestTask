from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status

from src.database.models import User, Account
from src.dependencies.auth_dependencies import get_current_user
from src.dependencies.basic_dependencies import get_account_service
from src.schemas.schemas import ShowAccountSchema
from src.services.services import AccountService

account_router: APIRouter = APIRouter(
    prefix="/account",
    tags=["account", ]
)


@account_router.get("/current-user", response_model=List[ShowAccountSchema])
async def get_current_user_accounts(
        user: User = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
) -> List[Account]:
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot have an account"
        )

    accounts: List[Account] = await service.get_current_user_accounts(user=user)
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The current user has no accounts"
        )

    return accounts


@account_router.get("/", response_model=List[ShowAccountSchema])
async def get_accounts_by_user_id(
        user_id: int,
        user: User = Depends(get_current_user),
        service: AccountService = Depends(get_account_service)
) -> List[Account]:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can get another user accounts"
        )
    try:
        accounts: List[Account] = await service.get_accounts_by_user_id(
            user_id=user_id
        )
        if not accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this id has no accounts"
            )

        return accounts

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot get another admin data"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id not found"
        )
