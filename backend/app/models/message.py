from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_draft import AiDraft
    from app.models.conversation import Conversation


class SenderType(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    external_message_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    external_event_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    sender_type: Mapped[SenderType] = mapped_column(
        Enum(
            SenderType,
            name="sender_type",
            native_enum=True,
        ),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )

    ai_drafts: Mapped[list["AiDraft"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AiDraft.created_at",
    )

    def __repr__(self) -> str:
        return (
            f"<Message("
            f"id={self.id}, "
            f"conversation_id={self.conversation_id}, "
            f"sender_type={self.sender_type.value}"
            f")>"
        )