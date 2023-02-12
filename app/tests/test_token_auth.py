import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from sqlalchemy.future import select


@pytest.mark.asyncio
class TestTokenAuth:

    @pytest.fixture(autouse=True)
    async def set_up(self, async_session: AsyncSession):
        user = User(username='testuser', name="test", email='test@test.com')
        user.set_password('testpassword')
        async_session.add(user)
        await async_session.commit()

    async def test_proper_user_model(self, async_session: AsyncSession):
        result = await async_session.execute(select(User))
        songs = result.scalars().all()
