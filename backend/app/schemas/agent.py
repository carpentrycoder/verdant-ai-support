from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AgentBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr


class AgentCreate(AgentBase):
    password: str = Field(min_length=8, max_length=128)


class AgentResponse(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
