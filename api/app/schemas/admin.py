# api/app/schemas/admin.py
"""Admin schemas"""

from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

class DashboardStats(BaseModel):
    users: Dict[str, int]
    projects: Dict[str, int]
    contracts: Dict[str, int]
    transactions: Dict[str, int]

class SystemHealthResponse(BaseModel):
    database: str
    redis: str
    memory_usage: Dict[str, Any]
    timestamp: float

class LogResponse(BaseModel):
    logs: List[str]
    total_lines: int

class MaintenanceModeResponse(BaseModel):
    message: str
    maintenance_mode: bool

class SuspendUserRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)

class CacheResponse(BaseModel):
    message: str
    keys_cleared: int

from pydantic import Field