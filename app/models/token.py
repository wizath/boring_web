import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field

from app.auth.tokens import RefreshToken
from app.models import User


class UserRefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str
    user: int = Field(foreign_key="user.id")
    jti: str = Field(max_length=255)
    created_at: datetime.datetime
    expires_at: datetime.datetime
    blacklisted_at: datetime.datetime = Field(nullable=True)
    blacklisted: bool = False
    ip_address: str = Field(default="", max_length=39)
    user_agent: str = Field(default="", max_length=255)

    @staticmethod
    async def from_token(db: AsyncSession, user: User, token, ip_address=None, user_agent=None):
        payload = RefreshToken.decode(token)
        ut = UserRefreshToken(
            token=token,
            user=user.id,
            jti=payload.get('jti'),
            user_id=payload.get('uid'),
            user_agent=user_agent,
            created_at=datetime.datetime.fromtimestamp(payload.get('iat')),
            expires_at=datetime.datetime.fromtimestamp(payload.get('exp')),
            ip_address=ip_address
        )
        db.add(ut)
        await db.commit()
