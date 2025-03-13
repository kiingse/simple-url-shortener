import datetime
from typing import Annotated, Any, Dict, Generator, Iterable

from sqlalchemy import BigInteger, DateTime, create_engine, inspect, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker

from app.common.config import Config

app_config = Config()

# Types shortcuts
big_int_pk = Annotated[int, mapped_column(primary_key=True)]
datetime_now = Annotated[datetime.datetime, mapped_column(server_default=text("now()"))]
jsonb = Annotated[Dict[str, Any], mapped_column()]

# Sync engine
engine = create_engine(
    str(app_config.DATABASE_URI), pool_pre_ping=True, pool_size=5, echo=False
)
session = sessionmaker(engine, autocommit=False, autoflush=False)


# Async engine
async_engine = create_async_engine(
    str(app_config.ASYNC_DATABASE_URI), pool_pre_ping=True, pool_size=5, echo=False
)
async_session = async_sessionmaker(
    async_engine, expire_on_commit=False, autoflush=False
)


def get_async_session() -> Generator[async_sessionmaker[AsyncSession], None, None]:
    yield async_session


class Base(DeclarativeBase):
    type_annotation_map: dict[Any, Any] = {
        big_int_pk: BigInteger,
        datetime_now: DateTime(timezone=True),
        jsonb: JSONB,
    }

    id: Any

    def to_dict(
        self,
        columns: Iterable[str] | None = None,
        exclude: list[str] | None = None,
    ):
        model_cols = [column.key for column in inspect(self).mapper.column_attrs]
        if not columns:
            columns = model_cols

        if not exclude:
            exclude = []

        return {
            column: getattr(self, column)
            for column in columns
            if column in model_cols and column not in exclude
        }
