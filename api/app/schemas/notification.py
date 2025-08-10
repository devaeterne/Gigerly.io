"""Notification & Device Token schemas"""

from typing import Optional, Dict, Literal
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import NotificationType, NotificationPriority

# -------------------------
# Notifications
# -------------------------

class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.normal
    title: str = Field(..., max_length=200)
    message: str
    payload: Optional[Dict] = None
    is_read: bool = False
    is_sent_push: bool = False
    is_sent_email: bool = False
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    title: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    payload: Optional[Dict] = None
    is_read: Optional[bool] = None
    is_sent_push: Optional[bool] = None
    is_sent_email: Optional[bool] = None
    read_at: Optional[datetime] = None
    sent_push_at: Optional[datetime] = None
    sent_email_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    payload: Optional[Dict]
    is_read: bool
    is_sent_push: bool
    is_sent_email: bool
    read_at: Optional[datetime]
    sent_push_at: Optional[datetime]
    sent_email_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------------------------
# Device Tokens (FCM)
# -------------------------

DevicePlatform = Literal["ios", "android", "web", "desktop"]

class DeviceTokenBase(BaseModel):
    fcm_token: str = Field(..., min_length=10, max_length=500)
    platform: DevicePlatform
    device_id: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

class DeviceTokenCreate(DeviceTokenBase):
    user_id: int

class DeviceTokenUpdate(BaseModel):
    fcm_token: Optional[str] = Field(None, min_length=10, max_length=500)
    platform: Optional[DevicePlatform] = None
    device_id: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    last_used_at: Optional[datetime] = None

class DeviceTokenResponse(DeviceTokenBase):
    id: int
    user_id: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Geriye dönük import isimleri (bazı route'lar bu adları bekleyebilir)
class RegisterDeviceTokenRequest(DeviceTokenCreate):
    pass

class UpdateDeviceTokenRequest(DeviceTokenUpdate):
    pass
