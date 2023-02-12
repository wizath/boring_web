import logging
import os

from starlette.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from app.config import settings
from app.api_v1 import api_router


def get_application() -> FastAPI:
    logging.info(f"Starting app {settings.TITLE} version {settings.VERSION} config {os.environ.get('APP_CONFIG')}")

    application = FastAPI(**settings.fastapi_kwargs)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    return application


app = get_application()
