from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.base_repository import AsyncBaseRepository
from app.common.db import get_async_session
from app.models import URLMapping


class AsyncURLMappingRepository(AsyncBaseRepository[URLMapping]):
    def __init__(
        self, session: async_sessionmaker[AsyncSession] = Depends(get_async_session)
    ):
        super().__init__(URLMapping, session)

    async def get_by_url(self, original_url: str) -> URLMapping | None:
        async with self._async_session() as session:
            stmt = select(URLMapping).where(URLMapping.original_url == original_url)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_by_short_code(self, short_code: str) -> URLMapping | None:
        async with self._async_session() as session:
            stmt = select(URLMapping).where(URLMapping.short_code == short_code)
            result = await session.execute(stmt)
            return result.scalars().first()
