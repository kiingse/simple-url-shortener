from fastapi import APIRouter

from .url_route import router as _url_router

url_router = APIRouter(prefix="", tags=["URL"])
url_router.include_router(_url_router)
