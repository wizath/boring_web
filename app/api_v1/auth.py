from typing import Optional

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.auth.login import authenticate, auth_token_response, auth_generate_tokens, auth_access_token_required
from app.auth.tokens import AccessToken
from app.database import get_async_session
from app.models.user import User

router = APIRouter()


class UserLogin(BaseModel):
    login: str
    password: str


class LoginToken(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    access_expire: int
    refresh_expire: int
    uid: int


@router.post("/login/cookie")
async def login_cookie(request: Request, credentials: UserLogin,
                       db: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    user: User = await authenticate(credentials, db)
    tokens = await auth_generate_tokens(request, user, db)

    return auth_token_response(tokens, return_token=False, return_cookie=True)


@router.post("/login")
@router.post("/login/token")
async def login_token(request: Request, credentials: UserLogin,
                      db: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    user: User = await authenticate(credentials.login, credentials.password, db)
    tokens = await auth_generate_tokens(request, user, db)

    return auth_token_response(tokens, return_token=True, return_cookie=False)


@router.get("/verify")
async def verify(user: User = Depends(auth_access_token_required)):
    return {'uid': user.id}
