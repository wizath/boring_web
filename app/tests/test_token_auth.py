import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


@pytest.mark.asyncio
class TestTokenAuth:

    @pytest.fixture(autouse=True)
    async def set_up(self, session: AsyncSession):
        user = User(username='testuser', email='test@test.com')
        user.set_password('testpassword')
        session.add(user)
        await session.commit()
