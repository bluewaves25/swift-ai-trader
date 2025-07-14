### services/notification_service.py

import httpx
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Handles sending notifications to users via email, SMS, or push.
    """

    def __init__(self):
        self.email_gateway = "https://api.emailservice.com/send"
        self.sms_gateway = "https://api.smsservice.com/send"

    async def send_email(self, recipient: str, subject: str, message: str) -> bool:
        payload = {
            "to": recipient,
            "subject": subject,
            "message": message
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.email_gateway, json=payload)
                response.raise_for_status()
                logger.info(f"Email sent to {recipient}")
                return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False

    async def send_sms(self, phone_number: str, message: str) -> bool:
        payload = {
            "phone": phone_number,
            "message": message
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.sms_gateway, json=payload)
                response.raise_for_status()
                logger.info(f"SMS sent to {phone_number}")
                return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False
