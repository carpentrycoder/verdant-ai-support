from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.auth import CurrentAgent
from app.db.db import get_db
from app.models.conversation import (
    Conversation,
    ConversationStatus,
)
from app.models.message import Message
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationStatusUpdate,
)
from app.schemas.message import MessageResponse


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=ConversationListResponse,
)
def list_conversations(
    current_agent: CurrentAgent,
    db: DbSession,
    conversation_status: ConversationStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> ConversationListResponse:
    """
    Return conversations ordered by latest activity.

    Optionally filter by OPEN or CLOSED status.
    Authentication is required.
    """

    conditions = []

    if conversation_status is not None:
        conditions.append(
            Conversation.status == conversation_status
        )

    count_statement = select(
        func.count(Conversation.id)
    )

    conversations_statement = (
        select(Conversation)
        .order_by(
            Conversation.last_activity_at.desc(),
            Conversation.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    if conditions:
        count_statement = count_statement.where(*conditions)
        conversations_statement = conversations_statement.where(
            *conditions
        )

    total = db.scalar(count_statement) or 0

    conversations = db.scalars(
        conversations_statement
    ).all()

    return ConversationListResponse(
        items=[
            ConversationResponse.model_validate(conversation)
            for conversation in conversations
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: UUID,
    current_agent: CurrentAgent,
    db: DbSession,
) -> Conversation:
    """
    Return one conversation with customer details
    and complete message history.
    """

    conversation = db.scalar(
        select(Conversation)
        .options(
            selectinload(Conversation.customer),
            selectinload(Conversation.messages),
        )
        .where(
            Conversation.id == conversation_id
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(
    conversation_id: UUID,
    current_agent: CurrentAgent,
    db: DbSession,
) -> list[Message]:
    """
    Return the complete chronological message history
    for a conversation.
    """

    conversation_exists = db.scalar(
        select(Conversation.id).where(
            Conversation.id == conversation_id
        )
    )

    if conversation_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    ).all()

    return list(messages)


@router.patch(
    "/{conversation_id}/status",
    response_model=ConversationResponse,
)
def update_conversation_status(
    conversation_id : UUID,
    payload: ConversationStatusUpdate,
    current_agent: CurrentAgent,
    db: DbSession,
) -> Conversation:
    """
    Change conversation status between OPEN and CLOSED.
    """

    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.status == payload.status:
        return conversation

    conversation.status = payload.status

    db.commit()
    db.refresh(conversation)

    return conversation