from fastapi import APIRouter
from app.api_v1 import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])


@api_router.get("/", include_in_schema=False)
async def health():
    return {"status": "ok"}
