from sqlalchemy.orm import Mapped, mapped_column

from app.common.db import Base, big_int_pk


class URLMapping(Base):
    """
    Represents a URL mapping in the database
    """

    __tablename__ = "url_mappings"

    id: Mapped[big_int_pk]
    original_url: Mapped[str] = mapped_column(unique=True)
    short_code: Mapped[str] = mapped_column(unique=True)
