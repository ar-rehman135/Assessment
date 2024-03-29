from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from src.core.db.models import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Post(Base):
    """
    Represents a post in the database.
    """

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)  # noqa: A003
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now(), nullable=False
    )
    created_by_id: Mapped[int] = mapped_column(
        String(63), ForeignKey("user.id"), nullable=False
    )

    # Define relationships
    created_by = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Post object.
        """
        return f"Post(id={self.id}, title={self.title}, created_at={self.created_at})"
