import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette import status

from app.auth.tokens import AccessToken, RefreshToken
from app.models import UserRefreshToken
from app.models.user import User
from app.tests.conftest import app, response_json


@pytest.mark.asyncio
class TestCookieLogin:

    @pytest.fixture(autouse=True)
    async def set_up(self, async_session: AsyncSession):
        user = User(username='testuser', name="test", email='test@test.com')
        user.set_password('testpassword')
        async_session.add(user)
        await async_session.commit()

    async def test_no_credentials(self, async_client: AsyncClient):
        response = await async_client.post(app.url_path_for('login_cookie'))
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_wrong_credentials(self, async_client: AsyncClient):
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'wrong', 'password': 'wrong'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_login_ok(self, async_client: AsyncClient):
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        assert response_json(response)['uid'] == 1
        assert 'access_token' not in response_json(response).keys()
        assert 'refresh_token' not in response_json(response).keys()

        access_token = response.cookies.get('access_token')
        assert AccessToken.decode(access_token) is not None
        refresh_token = response.cookies.get('refresh_token')
        assert RefreshToken.decode(refresh_token) is not None

    async def test_login_verify(self, async_client: AsyncClient):
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        assert response_json(response)['uid'] == 1
        assert 'access_token' not in response_json(response).keys()
        assert 'refresh_token' not in response_json(response).keys()

        access_token = response.cookies.get('access_token')
        async_client.cookies.set('access_token', access_token)
        login_response = await async_client.get(app.url_path_for('verify'))
        assert login_response.status_code == status.HTTP_200_OK

    async def test_login_refresh_object_created(self, async_client: AsyncClient, async_session: AsyncSession):
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        query = select(UserRefreshToken)
        element = (await async_session.execute(query)).scalars().first()

        assert element.user == 1
        assert element.blacklisted is False
        assert element.ip_address == '127.0.0.1'
