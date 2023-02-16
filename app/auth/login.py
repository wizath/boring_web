import datetime
from typing import Union

import jwt.exceptions
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, APIKeyCookie
from sqlmodel import or_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.auth.tokens import AccessToken, RefreshToken, Token
from app.database import get_async_session
from app.models import UserRefreshToken
from app.models.user import User


async def authenticate(login: str, password: str, db: AsyncSession):
    query = select(User).where(or_(User.username == login, User.email == login))
    user = (await db.execute(query)).scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    if not user.check_password(password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    return user


async def auth_generate_tokens(request: Request, user: User, db: AsyncSession):
    data = {}
    access_token = AccessToken.encode({'uid': user.id})
    refresh_token = RefreshToken.encode({'uid': user.id})

    ip_address = request.client.host
    user_agent = request.headers.get('user-agent', None)

    # create refresh token db record
    await UserRefreshToken.from_token(db, user, refresh_token, ip_address, user_agent)

    data['access_token'] = access_token
    data['refresh_token'] = refresh_token
    data['access_expire'] = datetime.datetime.utcnow() + AccessToken.expire_time
    data['refresh_expire'] = datetime.datetime.utcnow() + RefreshToken.expire_time
    data['uid'] = user.id

    return data


def auth_token_response(tokens: dict, return_token=False, return_cookie=False):
    access_expire = tokens['access_expire']
    refresh_expire = tokens['refresh_expire']

    response = {
        'access_expire': int(access_expire.timestamp()),
        'refresh_expire': int(refresh_expire.timestamp()),
        'uid': tokens['uid']
    }

    if return_token:
        response['access_token'] = tokens['access_token']
        response['refresh_token'] = tokens['refresh_token']

    response = JSONResponse(content=response)

    if return_cookie:
        response.set_cookie(key="access_token",
                            value=tokens['access_token'],
                            secure=True,
                            expires=int(AccessToken.expire_time.total_seconds()))

        response.set_cookie(key="refresh_token",
                            value=tokens['refresh_token'],
                            secure=True,
                            max_age=int(RefreshToken.expire_time.total_seconds()))

    return response


async def auth_verify_token(token, db: AsyncSession, token_class: Union[AccessToken, RefreshToken] = AccessToken):
    try:
        payload = token_class.decode(token)
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

    query = select(User).where(User.id == payload['uid'])
    user = (await db.execute(query)).scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="Wrong user credentials")

    if not user.is_active:
        HTTPException(status_code=403, detail="User is not active")

    # if token_class == RefreshToken:
    #     if UserRefreshToken.objects.filter(jti=payload.get('jti'), blacklisted=True).exists():
    #         raise exceptions.AuthenticationFailed('Token is blacklisted')

    return user


async def auth_check_token(request: Request, db: AsyncSession,
                           token_class: Union[AccessToken, RefreshToken] = AccessToken):
    access_token = await HTTPBearer(auto_error=False)(request)
    if access_token:
        token_user = await auth_verify_token(access_token.credentials, db, token_class=token_class)
        if token_user is not None:
            token_user.set_token(access_token.credentials)
            return token_user
    else:
        token_user = None

    cookie_name = 'access_token' if token_class is AccessToken else 'refresh_token'
    access_cookie = await APIKeyCookie(auto_error=False, name=cookie_name)(request)
    if access_cookie:
        cookie_user = await auth_verify_token(access_cookie, db, token_class=token_class)
    else:
        cookie_user = None

    if token_user is None and cookie_user is None:
        raise HTTPException(status_code=403, detail="Invalid token")

    cookie_user.set_token(access_cookie)
    return cookie_user


async def auth_access_token_required(request: Request, db: AsyncSession = Depends(get_async_session)):
    return await auth_check_token(request, db, token_class=AccessToken)


async def auth_refresh_token_required(request: Request, db: AsyncSession = Depends(get_async_session)):
    return await auth_check_token(request, db, token_class=RefreshToken)


async def auth_clear_tokens(user: User, db: AsyncSession):
    response = JSONResponse(content={})
    response.delete_cookie('refresh_token')
    response.delete_cookie('access_token')

    try:
        payload = RefreshToken.decode(user.token)
    except jwt.exceptions.InvalidTokenError:
        payload = None

    if payload:
        query = select(UserRefreshToken).where(UserRefreshToken.jti == payload['jti'])
        token: UserRefreshToken = (await db.execute(query)).scalars().first()
        if token:
            token.blacklisted = True
            token.blacklisted_at = datetime.datetime.utcnow()
            db.add(token)
            await db.commit()

    return response
