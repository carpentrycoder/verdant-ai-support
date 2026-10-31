from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
    ConversationStatus,
)
from app.models.customer import Customer
from app.models.message import Message, SenderType
from app.schemas.webhook import IncomingWebhook, WebhookResponse

from app.models.ai_draft import AiDraft, AiDraftStatus
from app.services.ai_service import generate_ai_draft


def get_existing_webhook_message(
    db: Session,
    event_id: str,
    external_message_id: str | None,
) -> Message | None:
    """
    Check whether the webhook event or external message
    has already been processed.
    """

    existing_message = db.scalar(
        select(Message).where(
            Message.external_event_id == event_id
        )
    )

    if existing_message is not None:
        return existing_message

    if external_message_id is not None:
        existing_message = db.scalar(
            select(Message).where(
                Message.external_message_id == external_message_id
            )
        )

    return existing_message


def get_or_create_customer(
    db: Session,
    payload: IncomingWebhook,
) -> Customer:
    """
    Find a customer by external ID.

    If the customer does not exist, create one.
    If the customer exists, update provided name and phone values.
    """

    customer = db.scalar(
        select(Customer).where(
            Customer.external_id == payload.customer.id
        )
    )

    if customer is None:
        customer = Customer(
            external_id=payload.customer.id,
            name=payload.customer.name,
            phone=payload.customer.phone,
        )

        db.add(customer)
        db.flush()

        return customer

    customer_changed = False

    if (
        payload.customer.name is not None
        and customer.name != payload.customer.name
    ):
        customer.name = payload.customer.name
        customer_changed = True

    if (
        payload.customer.phone is not None
        and customer.phone != payload.customer.phone
    ):
        customer.phone = payload.customer.phone
        customer_changed = True

    if customer_changed:
        customer.updated_at = datetime.now(timezone.utc)

    db.flush()

    return customer


def get_or_create_open_conversation(
    db: Session,
    customer: Customer,
    activity_time: datetime,
) -> Conversation:
    """
    Reuse the customer's existing OPEN conversation.

    Create a new OPEN conversation only if no active
    conversation exists.
    """

    conversation = db.scalar(
        select(Conversation).where(
            Conversation.customer_id == customer.id,
            Conversation.status == ConversationStatus.OPEN,
        )
    )

    if conversation is not None:
        conversation.last_activity_at = activity_time
        conversation.updated_at = datetime.now(timezone.utc)

        db.flush()

        return conversation

    conversation = Conversation(
        customer_id=customer.id,
        status=ConversationStatus.OPEN,
        last_activity_at=activity_time,
    )

    db.add(conversation)
    db.flush()

    return conversation


def build_duplicate_response(
    event_id: str,
    existing_message: Message,
) -> WebhookResponse:
    """
    Return a safe success response for a duplicate webhook.

    Webhook providers commonly retry requests, so a duplicate
    event should not be treated as an application failure.
    """

    return WebhookResponse(
        status="ok",
        detail="Webhook event was already processed",
        event_id=event_id,
        duplicate=True,
        conversation_id=existing_message.conversation_id,
        message_id=existing_message.id,
    )

def process_incoming_webhook(
    db: Session,
    payload: IncomingWebhook,
) -> WebhookResponse:
    existing_message = get_existing_webhook_message(
        db=db,
        event_id=payload.event_id,
        external_message_id=payload.message.id,
    )

    if existing_message is not None:
        return build_duplicate_response(
            event_id=payload.event_id,
            existing_message=existing_message,
        )

    message_created_at = (
        payload.message.created_at
        or datetime.now(timezone.utc)
    )

    try:
        customer = get_or_create_customer(
            db=db,
            payload=payload,
        )

        conversation = get_or_create_open_conversation(
            db=db,
            customer=customer,
            activity_time=message_created_at,
        )

        message = Message(
            external_message_id=payload.message.id,
            external_event_id=payload.event_id,
            conversation_id=conversation.id,
            sender_type=SenderType.CUSTOMER,
            text=payload.message.text,
            created_at=message_created_at,
        )

        db.add(message)
        db.flush()

        generated_draft = generate_ai_draft(
            customer_message=message.text,
        )

        ai_draft = AiDraft(
            message_id=message.id,
            draft_text=generated_draft.text,
            status=AiDraftStatus.PENDING,
            approved_text=None,
            approved_by=None,
            approved_at=None,
        )

        db.add(ai_draft)
        db.commit()

        db.refresh(customer)
        db.refresh(conversation)
        db.refresh(message)
        db.refresh(ai_draft)

        return WebhookResponse(
            status="ok",
            detail="Webhook processed and AI draft created",
            event_id=payload.event_id,
            duplicate=False,
            customer_id=customer.id,
            conversation_id=conversation.id,
            message_id=message.id,
        )

    except IntegrityError:
        db.rollback()

        existing_message = get_existing_webhook_message(
            db=db,
            event_id=payload.event_id,
            external_message_id=payload.message.id,
        )

        if existing_message is not None:
            return build_duplicate_response(
                event_id=payload.event_id,
                existing_message=existing_message,
            )

        raise

    except Exception:
        db.rollback()
        raise