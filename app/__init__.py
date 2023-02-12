import logging
from starlette.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from app.config import settings


def get_application() -> FastAPI:
    logging.info('starting app')

    application = FastAPI(**settings.fastapi_kwargs)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_application()
