# api/app/worker.py
"""Background worker for processing jobs"""

import asyncio
import logging

from app.core.redis import redis_manager
from app.services.email import send_email
from app.services.fcm import send_push_notification

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """Background job processor"""

    def __init__(self):
        self.running = False
        self.NOTIFICATION_QUEUE = "notification_queue"
        self.EMAIL_QUEUE = "email_queue"
        # 0 timeout blocks until a job is available
        self.QUEUE_TIMEOUT = 0

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

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(10)  # Wait longer on error

    async def stop(self):
        """Stop the worker"""
        logger.info("🛑 Stopping background worker...")
        self.running = False
        await redis_manager.disconnect()

    async def process_jobs(self):
        """Wait for and dispatch background jobs"""

        job = await redis_manager.redis.blpop(
            self.NOTIFICATION_QUEUE,
            self.EMAIL_QUEUE,
            timeout=self.QUEUE_TIMEOUT,
        )

        if not job:
            return

        queue_name, payload = job
        if queue_name == self.NOTIFICATION_QUEUE:
            await self.process_notifications(payload)
        elif queue_name == self.EMAIL_QUEUE:
            await self.process_emails(payload)

        # Add other job types here as needed

    async def process_notifications(self, notification_job: str):
        """Process a push notification payload"""

        try:
            import json

            job_data = json.loads(notification_job)

            # Send push notification
            await send_push_notification(
                user_id=job_data["user_id"],
                title=job_data["title"],
                message=job_data["message"],
                data=job_data.get("data", {}),
            )

            logger.info(f"Push notification sent to user {job_data['user_id']}")

        except Exception as e:
            logger.error(f"Failed to process notification: {e}")

    async def process_emails(self, email_job: str):
        """Process an email payload"""

        try:
            import json

            job_data = json.loads(email_job)

            # Send email
            await send_email(
                to_email=job_data["to_email"],
                subject=job_data["subject"],
                content=job_data["content"],
                template=job_data.get("template"),
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
