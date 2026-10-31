from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeBaseEntry:
    topic: str
    keywords: tuple[str, ...]
    content: str


KNOWLEDGE_BASE: tuple[KnowledgeBaseEntry, ...] = (
    KnowledgeBaseEntry(
        topic="return_policy",
        keywords=(
            "return",
            "returns",
            "refund",
            "exchange",
            "replace",
            "replacement",
        ),
        content=(
            "Customers may request a return within 7 days of delivery. "
            "The product should be unused and returned in its original "
            "packaging. Refunds are processed after the returned product "
            "has been received and inspected."
        ),
    ),
    KnowledgeBaseEntry(
        topic="order_tracking",
        keywords=(
            "track",
            "tracking",
            "order status",
            "where is my order",
            "delivery status",
            "shipment",
        ),
        content=(
            "Customers can track an order using the tracking link sent "
            "after dispatch. If tracking information is unavailable, an "
            "agent should request the customer's order number."
        ),
    ),
    KnowledgeBaseEntry(
        topic="delivery",
        keywords=(
            "delivery",
            "shipping",
            "arrive",
            "arrival",
            "delayed",
            "late",
        ),
        content=(
            "Standard delivery generally takes 3 to 5 business days after "
            "dispatch. Delivery timing may vary by location and carrier. "
            "Agents should avoid promising an exact delivery date unless "
            "confirmed by shipment tracking."
        ),
    ),
    KnowledgeBaseEntry(
        topic="cancellation",
        keywords=(
            "cancel",
            "cancellation",
            "cancel order",
        ),
        content=(
            "An order can be cancelled only before it has been dispatched. "
            "If the order has already been dispatched, the customer may "
            "request a return after delivery according to the return policy."
        ),
    ),
    KnowledgeBaseEntry(
        topic="payment",
        keywords=(
            "payment",
            "charged",
            "transaction",
            "failed payment",
            "money deducted",
        ),
        content=(
            "If a payment fails but the amount is deducted, customers should "
            "allow the payment provider's standard reversal process to "
            "complete. An agent should request the order ID and transaction "
            "reference before escalating the issue."
        ),
    ),
)


FALLBACK_KNOWLEDGE = (
    "No directly matching knowledge-base entry was found. "
    "Do not invent company policies, prices, dates, order details, or "
    "refund commitments. Ask the customer for the missing information "
    "or explain that an agent will review the request."
)


def search_knowledge_base(
    customer_message: str,
    limit: int = 3,
) -> list[KnowledgeBaseEntry]:
    normalized_message = customer_message.strip().lower()

    scored_entries: list[tuple[int, KnowledgeBaseEntry]] = []

    for entry in KNOWLEDGE_BASE:
        score = sum(
            1
            for keyword in entry.keywords
            if keyword.lower() in normalized_message
        )

        if score > 0:
            scored_entries.append((score, entry))

    scored_entries.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        entry
        for _, entry in scored_entries[:limit]
    ]


def build_knowledge_context(
    customer_message: str,
) -> str:
    entries = search_knowledge_base(customer_message)

    if not entries:
        return FALLBACK_KNOWLEDGE

    sections = [
        f"Topic: {entry.topic}\nPolicy: {entry.content}"
        for entry in entries
    ]

    return "\n\n".join(sections)