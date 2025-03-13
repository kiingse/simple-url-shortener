from typing import Generic, Optional, Sequence, Type, TypeVar

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.db import Base, get_async_session

ModelType = TypeVar("ModelType", bound=Base)


class AsyncBaseRepository(Generic[ModelType]):

    def __init__(
        self,
        model: Type[ModelType],
        session: async_sessionmaker[AsyncSession] = Depends(get_async_session),
    ):
        self.model = model
        self._async_session = session

    async def get(self, obj_id: int) -> Optional[ModelType]:
        async with self._async_session() as session:
            stmt = select(self.model).where(self.model.id == obj_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_all(self, page: int, limit: int) -> Sequence[ModelType]:
        async with self._async_session() as session:
            stmt = select(self.model).limit(limit).offset((page - 1) * limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def add(self, obj: ModelType) -> ModelType:
        async with self._async_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        async with self._async_session.begin() as session:
            await session.delete(obj)
        return None
