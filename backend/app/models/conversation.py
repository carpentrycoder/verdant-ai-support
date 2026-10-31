from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.message import Message


class ConversationStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Conversation(Base):
    __tablename__ = "conversations"

    __table_args__ = (
        Index(
            "uq_conversations_one_open_per_customer",
            "customer_id",
            unique=True,
            postgresql_where=text("status = 'OPEN'"),
        ),
        Index(
            "ix_conversations_customer_status",
            "customer_id",
            "status",
        ),
        Index(
            "ix_conversations_last_activity_at",
            "last_activity_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "customers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    status: Mapped[ConversationStatus] = mapped_column(
        Enum(
            ConversationStatus,
            name="conversation_status",
            native_enum=True,
        ),
        default=ConversationStatus.OPEN,
        server_default=ConversationStatus.OPEN.value,
        nullable=False,
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="conversations",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return (
            f"<Conversation("
            f"id={self.id}, "
            f"customer_id={self.customer_id}, "
            f"status={self.status.value}"
            f")>"
        )