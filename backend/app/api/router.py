from fastapi import APIRouter

from app.api.ai_drafts import router as ai_drafts_router
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.customers import router as customers_router
from app.api.webhook import router as webhook_router
from app.api.customer_portal import (
    router as customer_portal_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(conversations_router)
api_router.include_router(ai_drafts_router)
api_router.include_router(webhook_router)
api_router.include_router(customer_portal_router)