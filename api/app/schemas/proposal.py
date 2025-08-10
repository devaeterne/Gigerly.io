"""Proposal-related schemas (Pydantic v2)"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models import ProposalStatus  # Enum üyeleri: DRAFT, PENDING, ACCEPTED, REJECTED, WITHDRAWN
from .common import MoneyAmount, AttachmentSchema


class ProposalBase(BaseModel):
    cover_letter: str = Field(..., min_length=10, max_length=8000)
    bid_amount: MoneyAmount
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")
    estimated_delivery_days: Optional[int] = Field(None, ge=1, le=365)
    proposed_milestones: Optional[List[Dict[str, Any]]] = None
    additional_services: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[AttachmentSchema]] = None
    portfolio_items: Optional[List[Dict[str, Any]]] = None
    questions_answers: Optional[List[Dict[str, Any]]] = None


class ProposalCreate(ProposalBase):
    project_id: int
    freelancer_id: int
    status: ProposalStatus = ProposalStatus.PENDING  # varsayılan


class ProposalUpdate(BaseModel):
    cover_letter: Optional[str] = Field(None, min_length=10, max_length=8000)
    bid_amount: Optional[MoneyAmount] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    estimated_delivery_days: Optional[int] = Field(None, ge=1, le=365)
    proposed_milestones: Optional[List[Dict[str, Any]]] = None
    additional_services: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[AttachmentSchema]] = None
    portfolio_items: Optional[List[Dict[str, Any]]] = None
    questions_answers: Optional[List[Dict[str, Any]]] = None
    status: Optional[ProposalStatus] = None

    @model_validator(mode="after")
    def _validate_logic(self):
        # Örn: kabul/red durumlarında bid_amount zorunlu olsun vs. (ihtiyaca göre genişlet)
        return self


class ProposalResponse(ProposalBase):
    id: int
    project_id: int
    freelancer_id: int
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProposalListResponse(BaseModel):
    id: int
    project_id: int
    freelancer_id: int
    bid_amount: MoneyAmount
    currency: str
    status: ProposalStatus
    created_at: datetime

    class Config:
        from_attributes = True
