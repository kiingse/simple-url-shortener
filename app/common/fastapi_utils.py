from typing import Self

from fastapi import APIRouter

from app.common.config import config


class RouterBuilder:
    def __init__(self):
        self._router = APIRouter(prefix=f"/{config.API_PREFIX}")

    def with_router(self, router: APIRouter) -> Self:
        self._router.include_router(router)
        return self

    def build(self) -> APIRouter:
        return self._router
