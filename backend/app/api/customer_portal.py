from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.models.conversation import (
    Conversation,
    ConversationStatus,
)
from app.models.customer import Customer
from app.models.message import Message
from app.schemas.customer_portal import (
    CustomerPortalConversationResponse,
    CustomerPortalMessageCreate,
    CustomerPortalMessageResponse,
)
from app.schemas.message import MessageResponse
from app.schemas.webhook import (
    IncomingWebhook,
    WebhookCustomer,
    WebhookMessage,
)
from app.services.webhook_service import (
    process_incoming_webhook,
)


router = APIRouter(
    prefix="/customer",
    tags=["Customer Portal"],
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/messages",
    response_model=CustomerPortalMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_customer_message(
    payload: CustomerPortalMessageCreate,
    db: DbSession,
) -> CustomerPortalMessageResponse:
    """
    Public customer simulator endpoint.

    Reuses the same internal processing pipeline
    used by signed external webhooks.
    """

    unique_id = uuid4().hex

    webhook_payload = IncomingWebhook(
        event_id=f"portal_evt_{unique_id}",
        customer=WebhookCustomer(
            id=payload.customer.external_id,
            name=payload.customer.name,
            phone=payload.customer.phone,
        ),
        message=WebhookMessage(
            id=f"portal_msg_{unique_id}",
            text=payload.text,
            created_at=None,
        ),
    )

    result = process_incoming_webhook(
        db=db,
        payload=webhook_payload,
    )

    if (
        result.customer_id is None
        or result.conversation_id is None
        or result.message_id is None
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create customer message",
        )

    return CustomerPortalMessageResponse(
        status="ok",
        customer_id=result.customer_id,
        conversation_id=result.conversation_id,
        message_id=result.message_id,
    )


@router.get(
    "/{external_id}/conversation",
    response_model=CustomerPortalConversationResponse,
)
def get_customer_current_conversation(
    external_id: str,
    db: DbSession,
) -> CustomerPortalConversationResponse:
    customer = db.scalar(
        select(Customer).where(
            Customer.external_id == external_id
        )
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    conversation = db.scalar(
        select(Conversation)
        .where(
            Conversation.customer_id == customer.id,
            Conversation.status == ConversationStatus.OPEN,
        )
        .order_by(
            Conversation.last_activity_at.desc()
        )
    )

    if conversation is None:
        return CustomerPortalConversationResponse(
            customer_id=customer.id,
            external_id=customer.external_id,
            name=customer.name,
            conversation_id=None,
            status=None,
            messages=[],
        )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.created_at.asc()
        )
    ).all()

    return CustomerPortalConversationResponse(
        customer_id=customer.id,
        external_id=customer.external_id,
        name=customer.name,
        conversation_id=conversation.id,
        status=conversation.status.value,
        messages=[
            MessageResponse.model_validate(
                message
            )
            for message in messages
        ],
    )