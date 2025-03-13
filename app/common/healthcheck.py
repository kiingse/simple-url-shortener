from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.db import get_async_session

router = APIRouter()


@router.get("/healthcheck", tags=["healthcheck"])
async def healthcheck(
    session: async_sessionmaker[AsyncSession] = Depends(get_async_session),
):
    try:
        async with session() as async_session:
            await async_session.execute(text("SELECT 1"))
            return {"status": "OK", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=500, detail={"status": "NOK", "database": "disconnected"}
        )
