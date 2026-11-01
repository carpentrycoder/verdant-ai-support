import logging

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from groq import Groq
from pydantic import BaseModel

from app.api.auth import CurrentAgent
from app.core.config import settings


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class AiStatusResponse(BaseModel):
    status: str
    configured: bool
    reachable: bool
    provider: str
    model: str
    response_received: bool


@router.get(
    "/status",
    response_model=AiStatusResponse,
    responses={
        401: {
            "description": "Authentication required",
        },
        503: {
            "description": "AI provider unavailable",
        },
    },
)
def get_ai_status(
    current_agent: CurrentAgent,
) -> AiStatusResponse:

    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY is not configured",
        )

    client = Groq(
        api_key=settings.GROQ_API_KEY,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly: OK"
                    ),
                },
            ],

            temperature=0,

            max_tokens=128,

            reasoning_format="hidden",
        )

        message = (
            completion
            .choices[0]
            .message
        )

        response_text = (
            message.content
            or ""
        ).strip()

        logger.info(
            (
                "Groq connectivity test succeeded "
                "model=%s agent_id=%s "
                "response_received=%s"
            ),
            settings.GROQ_MODEL,
            current_agent.id,
            bool(response_text),
        )

        return AiStatusResponse(
            status="ok",
            configured=True,
            reachable=True,
            provider="groq",
            model=settings.GROQ_MODEL,
            response_received=bool(
                response_text
            ),
        )

    except Exception as exc:
        logger.exception(
            (
                "Groq connectivity test failed "
                "model=%s error_type=%s"
            ),
            settings.GROQ_MODEL,
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Groq provider unavailable. "
                f"Error type: {type(exc).__name__}"
            ),
        )