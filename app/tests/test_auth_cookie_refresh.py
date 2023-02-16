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
class TestTokenRefresh:

    @pytest.fixture(autouse=True)
    async def set_up(self, async_session: AsyncSession):
        user = User(username='testuser', name="test", email='test@test.com')
        user.set_password('testpassword')
        async_session.add(user)
        await async_session.commit()

    async def test_cookie_refresh_proper(self, async_client: AsyncClient):
        async_client.cookies.set('refresh_token', RefreshToken.encode({"uid": 1}))
        response = await async_client.post(app.url_path_for('token_refresh'))
        assert response.status_code == status.HTTP_200_OK

        assert response_json(response)['uid'] == 1
        assert response.cookies.get('access_token') is not None

        access_token = response.cookies.get('access_token')
        assert AccessToken.decode(access_token) is not None

    async def test_token_refresh_wrong_token(self, async_client: AsyncClient):
        async_client.cookies.set('refresh_token', 'wrongtoken')
        response = await async_client.post(app.url_path_for('token_refresh'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_token_refresh_access_token(self, async_client: AsyncClient):
        async_client.cookies.set('refresh_token', AccessToken.encode({"uid": 1}))
        response = await async_client.post(app.url_path_for('token_refresh'))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_token_refresh_dual_proper(self, async_client: AsyncClient):
        async_client.cookies.set('refresh_token', RefreshToken.encode({"uid": 1}))
        response = await async_client.post(app.url_path_for('dual_token_refresh'))
        assert response.status_code == status.HTTP_200_OK

        assert response_json(response)['uid'] == 1
        assert response.cookies.get('access_token') is not None
        assert response.cookies.get('refresh_token') is not None

        access_token = response.cookies.get('access_token')
        assert AccessToken.decode(access_token) is not None
        refresh_token = response.cookies.get('refresh_token')
        assert RefreshToken.decode(refresh_token) is not None

    async def test_token_refresh_previous_token_blacklisted(self, async_client: AsyncClient,
                                                            async_session: AsyncSession):
        # login for refresh token object
        response = await async_client.post(app.url_path_for('login_cookie'),
                                           json={'login': 'testuser', 'password': 'testpassword'})
        assert response.status_code == status.HTTP_200_OK

        refresh_token = response.cookies.get('refresh_token')
        async_client.cookies.set('refresh_token', refresh_token)
        response = await async_client.post(app.url_path_for('token_refresh'))
        assert response.status_code == status.HTTP_200_OK

        payload = RefreshToken.decode(refresh_token)
        query = select(UserRefreshToken).where(UserRefreshToken.jti == payload['jti'])
        element = (await async_session.execute(query)).scalars().first()

        assert element.blacklisted is True
