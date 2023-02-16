import asyncio
import json
from typing import Generator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import app, settings
from app.database import async_engine


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    settings.TESTING = True
    async with AsyncClient(app=app, base_url=f"http://127.0.0.1:8000") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


def response_json(response: httpx.Response) -> dict:
    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        return {}
