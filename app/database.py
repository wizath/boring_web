import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session

from app.config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
engine = create_engine(settings.SYNC_DATABASE_URL, echo=settings.DEBUG)


def get_local_session() -> Session:
    return Session(engine)


async def get_async_session() -> AsyncSession:
    print(f'opening database {settings.DATABASE_URL} {os.getcwd()}')
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False)
    async with async_session() as session:
        yield session
