"""Common schemas used across the application"""

from typing import Any, Dict, List, Optional, Literal, Annotated
from pydantic import BaseModel, Field
from pydantic.types import condecimal
from datetime import datetime

# ---- Common base responses ----

class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: bool = True
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None

# ---- Pagination ----

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    data: List[Any]
    meta: PaginationMeta

# ---- Health ----

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    services: Dict[str, str]
    timestamp: float

# ---- Common domain schemas ----

# Sabit seçenekler (regex yerine Literal)
SkillLevel = Literal["Beginner", "Intermediate", "Advanced", "Expert"]

class SkillSchema(BaseModel):
    """Skill schema for profiles and projects"""
    name: str = Field(..., min_length=1, max_length=100)
    level: Optional[SkillLevel] = None
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    required: bool = False

class AttachmentSchema(BaseModel):
    """File attachment schema"""
    filename: str
    url: str
    size: int
    mime_type: str
    uploaded_at: datetime

# Para alanları için condecimal (maks 12 hane, 2 ondalık)
MoneyAmount = condecimal(max_digits=12, decimal_places=2, ge=0)

class MoneySchema(BaseModel):
    """Money amount with currency"""
    amount: MoneyAmount
    currency: Annotated[str, Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")]  # ISO 4217

class AddressSchema(BaseModel):
    """Address schema"""
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

class DateRangeSchema(BaseModel):
    """Date range schema"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
