from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WebhookCustomer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        min_length=1,
        max_length=255,
        description="External customer ID",
        examples=["cust_1042"],
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
    def validate_customer_id(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Customer ID cannot be empty")

        return cleaned_value

    @field_validator("name", "phone")
    @classmethod
    def normalize_optional_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


class WebhookMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(
        default=None,
        max_length=255,
        description="External message ID",
        examples=["msg_88213"],
    )

    text: str = Field(
        min_length=1,
        description="Customer message content",
    )

    created_at: datetime | None = Field(
        default=None,
        description="Message creation time from the external system",
    )

    @field_validator("id")
    @classmethod
    def normalize_message_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None

    @field_validator("text")
    @classmethod
    def validate_message_text(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Message text cannot be empty")

        return cleaned_value


class IncomingWebhook(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(
        min_length=1,
        max_length=255,
        description="Unique webhook event ID",
        examples=["evt_7f3a91c2"],
    )

    customer: WebhookCustomer
    message: WebhookMessage

    @field_validator("event_id")
    @classmethod
    def validate_event_id(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Event ID cannot be empty")

        return cleaned_value


class WebhookResponse(BaseModel):
    status: str
    detail: str

    event_id: str

    duplicate: bool = False

    customer_id: UUID | None = None
    conversation_id: UUID | None = None
    message_id: UUID | None = None