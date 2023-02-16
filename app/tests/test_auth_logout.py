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
class TestLogout:

    @pytest.fixture(autouse=True)
    async def set_up(self, async_session: AsyncSession):
        user = User(username='testuser', name="test", email='test@test.com')
        user.set_password('testpassword')
        async_session.add(user)
        await async_session.commit()

    async def test_logout_clear_cookies(self, async_client: AsyncClient):
        async_client.cookies.set('access_token', AccessToken.encode({'uid': 1}))
        async_client.cookies.set('refresh_token', RefreshToken.encode({'uid': 1}))
        response = await async_client.post(app.url_path_for('logout'))

        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get('refresh_token') is None
        assert response.cookies.get('access_token') is None

    async def test_logout_with_token(self, async_client: AsyncClient):
        async_client.headers.update({
            'authorization': f'Bearer {RefreshToken.encode({"uid": 1})}'
        })
        login_response = await async_client.post(app.url_path_for('logout'))
        assert login_response.status_code == status.HTTP_200_OK

    async def test_logout_token_blacklist(self, async_client: AsyncClient, async_session: AsyncSession):
        response = await async_client.post(app.url_path_for('login_token'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        async_client.headers.update({
            'authorization': f'Bearer {response_json(response)["refresh_token"]}'
        })
        login_response = await async_client.post(app.url_path_for('logout'))
        assert login_response.status_code == status.HTTP_200_OK

        query = select(UserRefreshToken)
        element = (await async_session.execute(query)).scalars().first()

        assert element.user == 1
        assert element.blacklisted is True
        assert element.ip_address == '127.0.0.1'

    async def test_logout_cookie_blacklist(self, async_client: AsyncClient, async_session: AsyncSession):
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        refresh_token = response.cookies.get('refresh_token')
        async_client.cookies.set('refresh_token', refresh_token)
        login_response = await async_client.post(app.url_path_for('logout'))
        assert login_response.status_code == status.HTTP_200_OK

        query = select(UserRefreshToken)
        element = (await async_session.execute(query)).scalars().first()

        assert element.user == 1
        assert element.blacklisted is True
        assert element.ip_address == '127.0.0.1'
