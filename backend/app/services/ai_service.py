import logging
from dataclasses import dataclass

from groq import Groq

from app.core.config import settings
from app.services.knowledge_base import build_knowledge_context


logger = logging.getLogger(__name__)

client = Groq(
    api_key=settings.GROQ_API_KEY,
)


SYSTEM_PROMPT = """
You are an AI assistant that prepares draft replies for customer-support
agents.

Rules:
1. Use only the supplied knowledge-base context.
2. Never invent policies, prices, timelines, order states, refunds,
   discounts, or commitments.
3. If required information is missing, ask a short follow-up question.
4. Do not claim that an action has already been completed.
5. Keep the response concise, professional, and customer-friendly.
6. Return only the suggested customer reply.
7. Do not include headings such as "Draft response" or "AI response".
""".strip()


@dataclass(frozen=True)
class GeneratedDraft:
    text: str
    knowledge_context: str
    generated_by_ai: bool


def build_fallback_draft(customer_message: str) -> str:
    normalized_message = customer_message.strip().lower()

    if any(
        keyword in normalized_message
        for keyword in ("return", "refund", "exchange")
    ):
        return (
            "Returns may be requested within 7 days of delivery, provided "
            "the product is unused and in its original packaging. Please "
            "share your order number so the support team can review your "
            "request."
        )

    if any(
        keyword in normalized_message
        for keyword in ("track", "delivery", "order status", "shipment")
    ):
        return (
            "Please share your order number so the support team can check "
            "the latest tracking and delivery information."
        )

    if any(
        keyword in normalized_message
        for keyword in ("cancel", "cancellation")
    ):
        return (
            "An order may be cancelled before it has been dispatched. "
            "Please share your order number so the support team can verify "
            "its current status."
        )

    return (
        "Thank you for contacting support. Please share any relevant order "
        "number or additional details so the support team can review your "
        "request."
    )


def generate_ai_draft(
    customer_message: str,
) -> GeneratedDraft:
    cleaned_message = customer_message.strip()

    if not cleaned_message:
        raise ValueError("Customer message cannot be empty")

    knowledge_context = build_knowledge_context(
        customer_message=cleaned_message
    )

    if not settings.GROQ_API_KEY:
        logger.warning(
            "GROQ_API_KEY is not configured. Using fallback draft."
        )

        return GeneratedDraft(
            text=build_fallback_draft(cleaned_message),
            knowledge_context=knowledge_context,
            generated_by_ai=False,
        )

    client = Groq(
        api_key=settings.GROQ_API_KEY,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        "Knowledge-base context:\n"
                        f"{knowledge_context}\n\n"
                        "Customer message:\n"
                        f"{cleaned_message}\n\n"
                        "Prepare a suggested reply for an agent to review."
                    ),
                },
            ],
        )

        draft_text = (
            completion.choices[0].message.content or ""
        ).strip()

        if not draft_text:
            raise ValueError("AI provider returned an empty draft")

        return GeneratedDraft(
            text=draft_text,
            knowledge_context=knowledge_context,
            generated_by_ai=True,
        )

    except Exception:
        logger.exception(
            "AI draft generation failed. Using fallback draft."
        )

        return GeneratedDraft(
            text=build_fallback_draft(cleaned_message),
            knowledge_context=knowledge_context,
            generated_by_ai=False,
        )