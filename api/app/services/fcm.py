# api/app/services/fcm.py
"""Firebase Cloud Messaging service"""

import logging
from typing import Dict, Any, Optional
import json

from app.core.redis import redis_manager
from app.config import settings

logger = logging.getLogger(__name__)

async def send_push_notification(
    user_id: int,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """Send push notification to user"""
    
    try:
        # Get user's device tokens from database
        from app.core.database import AsyncSessionLocal
        from app.models import DeviceToken
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DeviceToken).where(
                    DeviceToken.user_id == user_id,
                    DeviceToken.is_active == True
                )
            )
            device_tokens = result.scalars().all()
        
        if not device_tokens:
            logger.warning(f"No active device tokens for user {user_id}")
            return False
        
        # Send to each device
        success_count = 0
        for token in device_tokens:
            try:
                # Add to notification queue for worker to process
                notification_job = {
                    "user_id": user_id,
                    "token": token.fcm_token,
                    "title": title,
                    "message": message,
                    "data": data or {},
                    "platform": token.platform
                }
                
                await redis_manager.redis.rpush(
                    "notification_queue",
                    json.dumps(notification_job)
                )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to queue notification for token {token.id}: {e}")
        
        logger.info(f"Queued {success_count} notifications for user {user_id}")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Failed to send push notification to user {user_id}: {e}")
        return False

async def send_fcm_message(
    token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """Send FCM message to specific token"""
    
    if not settings.FCM_SERVER_KEY:
        logger.warning("FCM_SERVER_KEY not configured")
        return False
    
    try:
        import httpx
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
        
        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fcm.googleapis.com/fcm/send",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"FCM message sent successfully to token {token[:20]}...")
                return True
            else:
                logger.error(f"FCM send failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to send FCM message: {e}")
        return False
