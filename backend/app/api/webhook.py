import hashlib
import hmac
import json
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.db import get_db
from app.schemas.webhook import IncomingWebhook, WebhookResponse
from app.services.webhook_service import process_incoming_webhook


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


def normalize_signature(signature: str) -> str:
    """
    Accept either:

    sha256=<hex-digest>

    or:

    <hex-digest>
    """

    normalized_signature = signature.strip()

    if normalized_signature.lower().startswith("sha256="):
        normalized_signature = normalized_signature.split(
            "=",
            maxsplit=1,
        )[1]

    return normalized_signature.strip().lower()


def verify_webhook_signature(
    raw_body: bytes,
    received_signature: str,
) -> bool:
    """
    Calculate the expected HMAC-SHA256 signature from the exact
    raw request body and compare it with the supplied signature.

    compare_digest performs constant-time comparison.
    """

    expected_signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    normalized_received_signature = normalize_signature(
        received_signature
    )

    return hmac.compare_digest(
        expected_signature,
        normalized_received_signature,
    )

#API router for receiving and processing customer-message webhooks
@router.post(
    "",
    response_model=WebhookResponse,
    responses={
    400: {
        "description": "Invalid webhook body",
    },
    401: {
        "description": "Invalid or missing HMAC signature",
    },
    422: {
        "description": "Webhook payload validation failed",
    },
    503: {
        "description": "Database unavailable",
    },
    },
    status_code=status.HTTP_200_OK,
    summary="Receive customer message webhook",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/IncomingWebhook"
                    },
                    "example": {
                        "event_id": "evt_7f3a91c2",
                        "type": "message.received",
                        "brand_id": "verdant-co",
                        "timestamp": "2026-11-03T10:15:22Z",
                        "customer": {
                            "id": "cust_1042",
                            "name": "Aisha Khan",
                            "phone": "+919800000001"
                        },
                        "message": {
                            "id": "msg_88213",
                            "type": "text",
                            "text": "Hi, my order #4471 hasn't arrived yet. Can I change the delivery address?"
                        }
                    }
                }
            }
        }
    },
)
async def receive_webhook(
    request: Request,
    db: DbSession,
    x_webhook_signature: Annotated[
        str | None,
        Header(
            alias="X-Webhook-Signature",
            description="HMAC-SHA256 signature of the raw request body",
        ),
    ] = None,
) -> WebhookResponse:
    """
    Receive and process a signed customer-message webhook.

    The signature must be generated using the exact raw JSON
    request bytes and the shared WEBHOOK_SECRET.
    """

    if x_webhook_signature is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature",
        )

    raw_body = await request.body()

    if not raw_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook request body is empty",
        )

    if not verify_webhook_signature(
        raw_body=raw_body,
        received_signature=x_webhook_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    try:
        json_payload = json.loads(raw_body)

    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body must contain valid JSON",
        )

    try:
        payload = IncomingWebhook.model_validate(json_payload)

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    try:
        return process_incoming_webhook(
            db=db,
            payload=payload,
        )

    except SQLAlchemyError:
        db.rollback()

        logger.exception(
            "Database error while processing webhook event"
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process webhook event",
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Unexpected error while processing webhook event"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected webhook processing error",
        )