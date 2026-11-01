from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.message import MessageResponse


class CustomerPortalIdentity(BaseModel):
    external_id: str = Field(
        min_length=1,
        max_length=255,
    )

    name: str | None = Field(
        default=None,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )


class CustomerPortalMessageCreate(BaseModel):
    customer: CustomerPortalIdentity

    text: str = Field(
        min_length=1,
        max_length=5000,
    )


class CustomerPortalMessageResponse(BaseModel):
    status: str

    customer_id: UUID
    conversation_id: UUID
    message_id: UUID


class CustomerPortalConversationResponse(BaseModel):
    customer_id: UUID
    external_id: str
    name: str | None
    conversation_id: UUID | None
    status: str | None
    messages: list[MessageResponse]