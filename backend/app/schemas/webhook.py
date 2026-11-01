from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class WebhookCustomer(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    id: str = Field(
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

    @field_validator("id")
    @classmethod
    def validate_customer_id(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Customer ID cannot be empty"
            )

        return cleaned

    @field_validator("name", "phone")
    @classmethod
    def clean_optional_string(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None


class WebhookMessage(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    id: str | None = Field(
        default=None,
        max_length=255,
    )

    type: str = Field(
        default="text",
        max_length=50,
    )

    text: str = Field(
        min_length=1,
    )

    created_at: datetime | None = None

    @field_validator("id")
    @classmethod
    def clean_message_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @field_validator("text")
    @classmethod
    def validate_text(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Message text cannot be empty"
            )

        return cleaned


class IncomingWebhook(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    event_id: str = Field(
        min_length=1,
        max_length=255,
    )

    type: str = Field(
        default="message.received",
        max_length=100,
    )

    brand_id: str = Field(
        default="verdant-co",
        max_length=255,
    )

    timestamp: datetime | None = None

    customer: WebhookCustomer
    message: WebhookMessage

    @field_validator("event_id")
    @classmethod
    def validate_event_id(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Event ID cannot be empty"
            )

        return cleaned


class WebhookResponse(BaseModel):
    status: str
    detail: str

    event_id: str
    duplicate: bool = False

    customer_id: UUID | None = None
    conversation_id: UUID | None = None
    message_id: UUID | None = None