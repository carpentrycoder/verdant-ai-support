from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.auth import CurrentAgent
from app.db.db import get_db
from app.models.ai_draft import AiDraft, AiDraftStatus
from app.models.conversation import Conversation
from app.models.message import Message, SenderType
from app.schemas.ai_draft import (
    AiDraftApprovalResponse,
    AiDraftApprove,
    AiDraftDetailResponse,
    AiDraftListResponse,
    AiDraftResponse,
)
from app.schemas.message import MessageResponse


router = APIRouter(
    prefix="/ai-drafts",
    tags=["AI Drafts"],
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "/pending",
    response_model=AiDraftListResponse,
)
def list_pending_ai_drafts(
    current_agent: CurrentAgent,
    db: DbSession,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AiDraftListResponse:
    """
    Return AI drafts waiting for agent review.
    """

    total = db.scalar(
        select(
            func.count(AiDraft.id)
        ).where(
            AiDraft.status == AiDraftStatus.PENDING
        )
    ) or 0

    drafts = db.scalars(
        select(AiDraft)
        .where(
            AiDraft.status == AiDraftStatus.PENDING
        )
        .order_by(
            AiDraft.created_at.asc()
        )
        .limit(limit)
        .offset(offset)
    ).all()

    return AiDraftListResponse(
        items=[
            AiDraftResponse.model_validate(draft)
            for draft in drafts
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{draft_id}",
    response_model=AiDraftDetailResponse,
)
def get_ai_draft(
    draft_id: UUID,
    current_agent: CurrentAgent,
    db: DbSession,
) -> AiDraftDetailResponse:
    """
    Return one AI draft with its original customer message.
    """

    draft = db.get(
        AiDraft,
        draft_id,
    )

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI draft not found",
        )

    customer_message = db.get(
        Message,
        draft.message_id,
    )

    if customer_message is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The customer message linked to this draft was not found",
        )

    return AiDraftDetailResponse(
        id=draft.id,
        message_id=draft.message_id,
        draft_text=draft.draft_text,
        status=draft.status,
        approved_text=draft.approved_text,
        approved_by=draft.approved_by,
        created_at=draft.created_at,
        approved_at=draft.approved_at,
        customer_message=MessageResponse.model_validate(
            customer_message
        ),
    )


@router.post(
    "/{draft_id}/approve",
    response_model=AiDraftApprovalResponse,
    status_code=status.HTTP_200_OK,
        responses={
        401: {
            "description": "Authentication required",
        },
        404: {
            "description": "AI draft not found",
        },
        409: {
            "description": "AI draft already used",
        },
        422: {
            "description": "Invalid request",
        },
    },

)
def approve_ai_draft(
    draft_id: UUID,
    payload: AiDraftApprove,
    current_agent: CurrentAgent,
    db: DbSession,
) -> AiDraftApprovalResponse:
    """
    Approve or edit an AI-generated response.

    This operation:
    1. Updates the AI draft to USED.
    2. Stores the final approved text.
    3. Records the approving agent and time.
    4. Creates an AGENT message in conversation history.

    Both operations run inside the same database transaction.
    """

    approved_text = payload.approved_text.strip()

    if not approved_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Approved text cannot be empty",
        )

    try:
        # Lock the draft row so two agents cannot approve
        # the same draft concurrently.
        draft = db.scalar(
            select(AiDraft)
            .where(
                AiDraft.id == draft_id
            )
            .with_for_update()
        )

        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI draft not found",
            )

        if draft.status != AiDraftStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="AI draft has already been used or cannot be approved",
            )

        customer_message = db.get(
            Message,
            draft.message_id,
        )

        if customer_message is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The customer message linked to this draft was not found",
            )

        if customer_message.sender_type != SenderType.CUSTOMER:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="AI draft is not linked to a customer message",
            )

        approved_at = datetime.now(timezone.utc)

        draft.status = AiDraftStatus.USED
        draft.approved_text = approved_text
        draft.approved_by = current_agent.id
        draft.approved_at = approved_at

        agent_message = Message(
            external_message_id=None,
            external_event_id=None,
            conversation_id=customer_message.conversation_id,
            sender_type=SenderType.AGENT,
            text=approved_text,
            created_at=approved_at,
        )

        db.add(agent_message)
        db.flush()

        conversation = db.get(
            Conversation,
            customer_message.conversation_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conversation linked to this draft was not found",
            )

        conversation.last_activity_at = approved_at
        conversation.updated_at = approved_at

        db.commit()

        db.refresh(draft)
        db.refresh(agent_message)

        return AiDraftApprovalResponse(
            draft=AiDraftResponse.model_validate(draft),
            agent_message=MessageResponse.model_validate(
                agent_message
            ),
        )

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to approve this AI draft",
        )

    except Exception:
        db.rollback()
        raise