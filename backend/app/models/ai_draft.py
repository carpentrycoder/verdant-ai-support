from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.message import Message


class AiDraftStatus(str, enum.Enum):
    PENDING = "PENDING"
    USED = "USED"
    FAILED = "FAILED"


class AiDraft(Base):
    __tablename__ = "ai_drafts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "messages.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    draft_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[AiDraftStatus] = mapped_column(
        Enum(
            AiDraftStatus,
            name="ai_draft_status",
            native_enum=True,
        ),
        default=AiDraftStatus.PENDING,
        server_default=AiDraftStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    approved_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    message: Mapped["Message"] = relationship(
        back_populates="ai_drafts",
    )

    approver: Mapped["Agent | None"] = relationship(
        back_populates="approved_drafts",
        foreign_keys=[approved_by],
    )

    def __repr__(self) -> str:
        return (
            f"<AiDraft("
            f"id={self.id}, "
            f"message_id={self.message_id}, "
            f"status={self.status.value}"
            f")>"
        )