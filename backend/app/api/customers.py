from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.auth import CurrentAgent
from app.db.db import get_db
from app.models.conversation import Conversation
from app.models.customer import Customer
from app.schemas.conversation import ConversationResponse
from app.schemas.customer import (
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=CustomerListResponse,
)
def list_customers(
    current_agent: CurrentAgent,
    db: DbSession,
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
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
) -> CustomerListResponse:
    """
    Return customers with optional search.

    Search supports:
    - external_id
    - name
    - phone
    """

    conditions = []

    if search is not None:
        normalized_search = search.strip()

        if normalized_search:
            pattern = f"%{normalized_search}%"

            conditions.append(
                or_(
                    Customer.external_id.ilike(pattern),
                    Customer.name.ilike(pattern),
                    Customer.phone.ilike(pattern),
                )
            )

    count_statement = select(
        func.count(Customer.id)
    )

    customer_statement = (
        select(Customer)
        .order_by(
            Customer.updated_at.desc(),
            Customer.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    if conditions:
        count_statement = count_statement.where(
            *conditions
        )

        customer_statement = customer_statement.where(
            *conditions
        )

    total = db.scalar(
        count_statement
    ) or 0

    customers = db.scalars(
        customer_statement
    ).all()

    return CustomerListResponse(
        items=[
            CustomerResponse.model_validate(customer)
            for customer in customers
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerDetailResponse,
)
def get_customer(
    customer_id: UUID,
    current_agent: CurrentAgent,
    db: DbSession,
) -> CustomerDetailResponse:
    """
    Return one customer and the customer's
    conversation history.
    """

    customer = db.scalar(
        select(Customer)
        .options(
            selectinload(Customer.conversations)
        )
        .where(
            Customer.id == customer_id
        )
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    conversations = sorted(
        customer.conversations,
        key=lambda conversation: conversation.created_at,
        reverse=True,
    )

    return CustomerDetailResponse(
        id=customer.id,
        external_id=customer.external_id,
        name=customer.name,
        phone=customer.phone,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        conversations=[
            ConversationResponse.model_validate(
                conversation
            )
            for conversation in conversations
        ],
    )


@router.get(
    "/{customer_id}/conversations",
    response_model=list[ConversationResponse],
)
def get_customer_conversations(
    customer_id: UUID,
    current_agent: CurrentAgent,
    db: DbSession,
) -> list[Conversation]:
    """
    Return all conversations belonging to
    one customer.
    """

    customer_exists = db.scalar(
        select(Customer.id).where(
            Customer.id == customer_id
        )
    )

    if customer_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    conversations = db.scalars(
        select(Conversation)
        .where(
            Conversation.customer_id == customer_id
        )
        .order_by(
            Conversation.created_at.desc()
        )
    ).all()

    return list(conversations)


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    current_agent: CurrentAgent,
    db: DbSession,
) -> Customer:
    """
    Update editable customer information.

    external_id cannot be changed through this endpoint.
    """

    customer = db.get(
        Customer,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        name = update_data["name"]

        if name is not None:
            name = name.strip() or None

        customer.name = name

    if "phone" in update_data:
        phone = update_data["phone"]

        if phone is not None:
            phone = phone.strip() or None

        customer.phone = phone

    db.commit()
    db.refresh(customer)

    return customer