from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr


# Each class corresponds to a collection (lowercased) as per project guidance.

class Tenant(BaseModel):
    name: str
    domain: Optional[str] = None
    active: bool = True


class User(BaseModel):
    tenant_id: str
    email: EmailStr
    name: Optional[str] = None
    role: Literal["admin", "manager", "agent"] = "agent"
    active: bool = True


class Number(BaseModel):
    tenant_id: str
    e164: str = Field(..., description="E.164 formatted phone number, e.g., +15551234567")
    provider: Optional[str] = None
    assigned_to: Optional[str] = Field(None, description="User or callflow id")


class Endpoint(BaseModel):
    tenant_id: str
    kind: Literal["sip", "webrtc"]
    username: str
    display_name: Optional[str] = None
    # In a real system, password is hashed and stored securely; kept simple here
    password: Optional[str] = None


class CallflowNode(BaseModel):
    id: str
    type: Literal[
        "start",
        "menu",
        "play",
        "queue",
        "ring",
        "record",
        "voicemail",
        "hangup",
    ]
    config: dict = Field(default_factory=dict)
    next: Optional[str] = None  # id of next node


class Callflow(BaseModel):
    tenant_id: str
    name: str
    entry_id: str
    nodes: List[CallflowNode]


class Lead(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: Optional[str] = None


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
