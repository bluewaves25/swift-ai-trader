### services/payment_service.py

import httpx
import os
from waves_quant_agi.shared.settings import settings


class PaymentService:
    """
    Handles interactions with Paystack for payment processing.
    """

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    async def initialize_payment(self, amount: float, email: str, reference: str) -> str:
        """
        Initialize a payment with Paystack
        """
        url = f"{self.base_url}/transaction/initialize"
        payload = {
            "amount": int(amount * 100),  # Convert to kobo
            "email": email,
            "reference": reference
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

        if not data.get("status"):
            raise Exception("Failed to initialize payment")

        return data["data"]["authorization_url"]

    async def verify_payment(self, reference: str) -> bool:
        """
        Verify payment status via Paystack
        """
        url = f"{self.base_url}/transaction/verify/{reference}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

        if not data.get("status"):
            return False

        return data["data"]["status"] == "success"
