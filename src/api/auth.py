from typing import Dict

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi import Depends

from src.database.models import User
from src.dependencies.auth_dependencies import get_current_user
from src.dependencies.basic_dependencies import get_auth_service
from src.schemas.schemas import LoginSchema, TokenSchema
from src.services.services import AuthService


auth_router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["auth", ]
)


@auth_router.post(path="/login", response_model=TokenSchema)
async def login(
    body: LoginSchema,
    service: AuthService = Depends(get_auth_service),
) -> TokenSchema:
    try:
        token_data: Dict[str, str] = await service.login(
            email=body.email,
            password=body.password
        )
        return TokenSchema(**token_data)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )


@auth_router.post(path="/refresh-token", response_model=TokenSchema)
async def refresh_token(
    user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> TokenSchema:
    token_data: Dict[str, str] = service.refresh_token(user=user)

    return TokenSchema(**token_data)
