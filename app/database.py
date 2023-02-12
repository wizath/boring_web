from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session

from app.config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
engine = create_engine(settings.DATABASE_URL, echo=True)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
