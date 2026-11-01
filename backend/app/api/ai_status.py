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
            temperature=0,
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply using only the word OK."
                    ),
                },
            ],
        )

        result = (
            completion
            .choices[0]
            .message.content
            or ""
        ).strip()

        if not result:
            raise ValueError(
                "Groq returned an empty response"
            )

        logger.info(
            "Groq connectivity test succeeded model=%s",
            settings.GROQ_MODEL,
        )

        return AiStatusResponse(
            status="ok",
            configured=True,
            reachable=True,
            provider="groq",
            model=settings.GROQ_MODEL,
        )

    except Exception as exc:
        logger.exception(
            "Groq connectivity test failed model=%s",
            settings.GROQ_MODEL,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Groq provider unavailable. "
                f"Error type: {type(exc).__name__}"
            ),
        )