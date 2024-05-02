from fastapi import APIRouter

from app.routers.v1 import currency_converter_router

api_router = APIRouter()
api_router.include_router(currency_converter_router.router, prefix="/v1")
