import datetime

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, APIKeyCookie
from sqlmodel import or_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.auth.tokens import AccessToken, RefreshToken
from app.database import get_async_session
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
    # UserRefreshToken.from_token(refresh_token, ip_address, user_agent)

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
                            expires=AccessToken.expire_time.seconds)

        response.set_cookie(key="refresh_token",
                            value=tokens['refresh_token'],
                            secure=True,
                            expires=RefreshToken.expire_time.seconds)

    return response


async def auth_check_token(token, db: AsyncSession, token_class=AccessToken):
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


async def auth_access_token_required(request: Request, db: AsyncSession = Depends(get_async_session)):
    access_token = await HTTPBearer(auto_error=False)(request)
    if access_token:
        token_user = await auth_check_token(access_token.credentials, db)
        if token_user is not None:
            return token_user
    else:
        token_user = None

    access_cookie = await APIKeyCookie(auto_error=False, name='access_token')(request)
    if access_cookie:
        cookie_user = await auth_check_token(access_cookie, db)
    else:
        cookie_user = None

    if token_user is None and cookie_user is None:
        raise HTTPException(status_code=403, detail="Invalid token")

    return cookie_user
