import datetime
import uuid

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import settings
from app.auth.tokens import AccessToken
from app.models.user import User
from app.tests.conftest import app


@pytest.mark.asyncio
class TestCookieAuth:

    @pytest.fixture(autouse=True)
    async def set_up(self, async_session: AsyncSession):
        user = User(username='testuser', name="test", email='test@test.com')
        user.set_password('testpassword')
        async_session.add(user)
        await async_session.commit()

    async def test_authorization_proper(self, async_client: AsyncClient):
        token = AccessToken.encode({'uid': 1})

        async_client.cookies.set('access_token', token)
        response = await async_client.get(app.url_path_for('verify'))

        assert response.status_code == status.HTTP_200_OK
        assert 'uid' in response.text

    async def test_authorization_no_cookie(self, async_client: AsyncClient):
        response = await async_client.get(app.url_path_for('verify'))

        assert "Invalid token" in response.text
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_authorization_wrong_cookie(self, async_client: AsyncClient):
        async_client.cookies.set('access_token', 'wrongcookie')
        response = await async_client.get(app.url_path_for('verify'))

        assert "Invalid token" in response.text
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_authorization_expired_cookie(self, async_client: AsyncClient):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = now - datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 1,
            'exp': dt.timestamp(),
            'iat': now.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': AccessToken.issuer
        }, settings.SECRET_KEY, algorithm='HS256')

        async_client.cookies.set('access_token', token)
        response = await async_client.get(app.url_path_for('verify'))

        assert "Invalid token" in response.text
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_authorization_wrong_user_cookie(self, async_client: AsyncClient):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        issued = now - datetime.timedelta(minutes=1)
        dt = now + datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 99,
            'exp': dt.timestamp(),
            'iat': issued.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': AccessToken.issuer
        }, settings.SECRET_KEY, algorithm='HS256')

        async_client.cookies.set('access_token', token)
        response = await async_client.get(app.url_path_for('verify'))

        assert 'Wrong user credentials' in response.text
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_authorization_disabled_user_cookie(self, async_client: AsyncClient):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        issued = now - datetime.timedelta(minutes=1)
        dt = now + datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 2,
            'exp': dt.timestamp(),
            'iat': issued.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': AccessToken.issuer
        }, settings.SECRET_KEY, algorithm='HS256')

        async_client.cookies.set('access_token', token)
        response = await async_client.get(app.url_path_for('verify'))

        assert 'Wrong user credentials' in response.text
        assert response.status_code == status.HTTP_403_FORBIDDEN
