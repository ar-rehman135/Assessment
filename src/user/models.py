from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.db.models import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(63), primary_key=True)  # noqa: A003
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=False, unique=True
    )
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)
    token: Mapped[Optional[str]] = mapped_column(String(255))

    posts = relationship("Post", back_populates="created_by")  # Define the relationship

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
