# api/app/worker.py
"""Background worker for processing jobs"""

import asyncio
import logging
from typing import Any, Dict

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.core.redis import redis_manager
from app.services.fcm import send_push_notification
from app.services.email import send_email
from app.models import Notification

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """Background job processor"""
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """Start the worker"""
        logger.info("🔄 Starting background worker...")
        
        self.running = True
        
        # Connect to Redis
        await redis_manager.connect()
        
        # Start processing jobs
        while self.running:
            try:
                await self.process_jobs()
                await asyncio.sleep(5)  # Check for jobs every 5 seconds
                
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(10)  # Wait longer on error
    
    async def stop(self):
        """Stop the worker"""
        logger.info("🛑 Stopping background worker...")
        self.running = False
        await redis_manager.disconnect()
    
    async def process_jobs(self):
        """Process pending background jobs"""
        
        # Process notification queue
        await self.process_notifications()
        
        # Process email queue
        await self.process_emails()
        
        # Add other job types here as needed
    
    async def process_notifications(self):
        """Process pending push notifications"""
        
        # Get pending notifications from Redis queue
        notification_job = await redis_manager.redis.lpop("notification_queue")
        
        if notification_job:
            try:
                import json
                job_data = json.loads(notification_job)
                
                # Send push notification
                await send_push_notification(
                    user_id=job_data["user_id"],
                    title=job_data["title"],
                    message=job_data["message"],
                    data=job_data.get("data", {})
                )
                
                logger.info(f"Push notification sent to user {job_data['user_id']}")
                
            except Exception as e:
                logger.error(f"Failed to process notification: {e}")
    
    async def process_emails(self):
        """Process pending emails"""
        
        email_job = await redis_manager.redis.lpop("email_queue")
        
        if email_job:
            try:
                import json
                job_data = json.loads(email_job)
                
                # Send email
                await send_email(
                    to_email=job_data["to_email"],
                    subject=job_data["subject"],
                    content=job_data["content"],
                    template=job_data.get("template")
                )
                
                logger.info(f"Email sent to {job_data['to_email']}")
                
            except Exception as e:
                logger.error(f"Failed to process email: {e}")

# Worker instance
worker = BackgroundWorker()

async def main():
    """Main worker function"""
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    finally:
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())