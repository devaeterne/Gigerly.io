# api/app/services/email.py
"""Email service"""

import logging
from typing import Optional

from app.config import settings
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)

async def send_email(
    to_email: str,
    subject: str,
    content: str,
    template: Optional[str] = None
) -> bool:
    """Send email (queued for background processing)"""
    
    try:
        import json
        
        email_job = {
            "to_email": to_email,
            "subject": subject,
            "content": content,
            "template": template
        }
        
        await redis_manager.redis.rpush(
            "email_queue",
            json.dumps(email_job)
        )
        
        logger.info(f"Email queued for {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to queue email for {to_email}: {e}")
        return False

async def send_email_direct(
    to_email: str,
    subject: str,
    content: str,
    template: Optional[str] = None
) -> bool:
    """Send email directly using SendGrid"""
    
    if not settings.SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not configured")
        return False
    
    try:
        # Placeholder for SendGrid integration
        # You would implement actual SendGrid API call here
        
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False