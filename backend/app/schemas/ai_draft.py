from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_draft import AiDraftStatus
from app.schemas.message import MessageResponse


class AiDraftCreate(BaseModel):
    message_id: UUID

    draft_text: str = Field(
        min_length=1,
    )


class AiDraftApprove(BaseModel):
    approved_text: str = Field(
        min_length=1,
        max_length=5000,
        description="Final response approved by the agent",
    )


class AiDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message_id: UUID
    draft_text: str
    status: AiDraftStatus
    approved_text: str | None
    approved_by: UUID | None
    created_at: datetime
    approved_at: datetime | None


class AiDraftDetailResponse(AiDraftResponse):
    customer_message: MessageResponse


class AiDraftListResponse(BaseModel):
    items: list[AiDraftResponse]
    total: int
    limit: int
    offset: int


class AiDraftApprovalResponse(BaseModel):
    draft: AiDraftResponse
    agent_message: MessageResponse