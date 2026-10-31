from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.conversation import ConversationStatus
from app.schemas.message import MessageResponse


class ConversationCreate(BaseModel):
    customer_id: UUID


class ConversationStatusUpdate(BaseModel):
    status: ConversationStatus


class ConversationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    customer_id: UUID
    status: ConversationStatus
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime


class ConversationCustomerResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    external_id: str
    name: str | None
    phone: str | None
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    customer: ConversationCustomerResponse
    messages: list[MessageResponse]


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    limit: int
    offset: int