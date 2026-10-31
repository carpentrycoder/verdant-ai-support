from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.db import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


DbSession = Annotated[
    Session,
    Depends(get_db),
]


def get_current_agent(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: DbSession,
) -> Agent:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        agent_id = UUID(payload["sub"])

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        raise credentials_exception

    agent = db.get(
        Agent,
        agent_id,
    )

    if agent is None:
        raise credentials_exception

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent account is inactive",
        )

    return agent


CurrentAgent = Annotated[
    Agent,
    Depends(get_current_agent),
]


@router.post(
    "/register",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_agent(
    payload: AgentCreate,
    db: DbSession,
) -> Agent:
    normalized_email = str(payload.email).strip().lower()
    normalized_name = payload.name.strip()

    if not normalized_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Agent name cannot be empty",
        )

    existing_agent = db.scalar(
        select(Agent).where(
            Agent.email == normalized_email
        )
    )

    if existing_agent is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An agent with this email already exists",
        )

    agent = Agent(
        name=normalized_name,
        email=normalized_email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )

    db.add(agent)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An agent with this email already exists",
        )

    db.refresh(agent)

    return agent


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login_agent(
    payload: LoginRequest,
    db: DbSession,
) -> LoginResponse:
    normalized_email = str(payload.email).strip().lower()

    agent = db.scalar(
        select(Agent).where(
            Agent.email == normalized_email
        )
    )

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not verify_password(
        payload.password,
        agent.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent account is inactive",
        )

    access_token = create_access_token(
        subject=agent.id,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        agent=AgentResponse.model_validate(agent),
    )


@router.get(
    "/me",
    response_model=AgentResponse,
)
def get_authenticated_agent(
    current_agent: CurrentAgent,
) -> Agent:
    return current_agent