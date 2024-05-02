from fastapi import APIRouter

from app.controller.v1 import currency_converter_controller

api_router = APIRouter()
api_router.include_router(currency_converter_controller.router, prefix="/v1")
