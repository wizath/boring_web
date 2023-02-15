import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyCookie, OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.auth.tokens import AccessToken, RefreshToken

router = APIRouter()


class UserLogin(BaseModel):
    username: str
    password: str


class LoginToken(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    access_expire: int
    refresh_expire: int
    uid: int


@router.post("/login/cookie")  # , response_model=LoginToken)
async def login2(request: Request, credentials: UserLogin):
    access_token = AccessToken.encode({'uid': 1})
    refresh_token = RefreshToken.encode({'uid': 1})

    data = {}
    # data['access_token'] = access_token
    # data['refresh_token'] = refresh_token
    # data['access_expire'] = int((datetime.datetime.utcnow() + AccessToken.expire_time).timestamp())
    # data['refresh_expire'] = int((datetime.datetime.utcnow() + RefreshToken.expire_time).timestamp())
    data['uid'] = 1

    return data


@router.post("/login")  # , response_model=LoginToken)
@router.post("/login/token")  # , response_model=LoginToken)
async def login(request: Request, credentials: UserLogin):
    access_token = AccessToken.encode({'uid': 1})
    refresh_token = RefreshToken.encode({'uid': 1})

    data = {}
    # data['access_token'] = access_token
    # data['refresh_token'] = refresh_token
    data['access_expire'] = int((datetime.datetime.utcnow() + AccessToken.expire_time).timestamp())
    data['refresh_expire'] = int((datetime.datetime.utcnow() + RefreshToken.expire_time).timestamp())
    data['uid'] = 1

    return data


async def auth_check_token(token, db: AsyncSession, token_class=AccessToken):
    try:
        payload = token_class.decode(token)
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

    query = select(User).where(User.id == payload['uid'])
    user = (await db.execute(query)).first()
    if not user:
        raise HTTPException(status_code=403, detail="Wrong user credentials")

    if not user.is_active:
        HTTPException(status_code=403, detail="User is not active")

    # if token_class == RefreshToken:
    #     if UserRefreshToken.objects.filter(jti=payload.get('jti'), blacklisted=True).exists():
    #         raise exceptions.AuthenticationFailed('Token is blacklisted')

    return user


async def auth_token_required(request: Request, db: AsyncSession = Depends(get_async_session)):
    # print('test', credentials)
    # cookie = APIKeyCookie(name='access_token', auto_error=False)
    # print(await cookie(request))

    bearer = HTTPBearer(auto_error=False)
    token = await bearer(request)
    return await auth_check_token(token, db)


@router.get("/verify")
async def verify(user: User = Depends(auth_token_required)):
    print(user)
    return {'status': 'ok'}
