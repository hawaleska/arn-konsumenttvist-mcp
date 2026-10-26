# ARN Konsumenttvist MCP
# Copyright (c) 2026 Kim Andreas Hawaleska
# All rights reserved.
# Proprietary software. Unauthorized copying, modification,
# redistribution, or commercial use is prohibited without permission.
# Contact: hawaleska@gmail.com

import hashlib
import json
import os
import secrets
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FREE_SEARCHES = 10


class LicenseManager:
    """
    License manager backed by the Cloudflare D1 API Worker.

    Public methods intentionally preserve the API used by arn_mcp.py
    and arn_auth.py.
    """

    def __init__(self, db_path=None):
        self.api_url = os.getenv("ARN_D1_API_URL", "").strip().rstrip("/")
        self.api_secret = os.getenv("ARN_D1_API_SECRET", "").strip()

        if not self.api_url:
            raise RuntimeError("ARN_D1_API_URL saknas i miljön.")

        if not self.api_secret:
            raise RuntimeError("ARN_D1_API_SECRET saknas i miljön.")

    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        return hashlib.sha256(
            api_key.encode("utf-8")
        ).hexdigest()

    def _request(self, action: str, **payload):
        body = {
            "action": action,
            **payload,
        }

        data = json.dumps(body).encode("utf-8")

        request = Request(
            self.api_url,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ARN-Konsumenttvist-MCP/1.0",
            },
        )

        try:
            with urlopen(request, timeout=15) as response:
                raw = response.read().decode("utf-8")
                status = response.status

        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")

            try:
                error_data = json.loads(raw)
            except json.JSONDecodeError:
                error_data = {}

            message = error_data.get("error") or raw or str(exc)

            if exc.code == 400:
                raise ValueError(message)

            if exc.code in (401, 403):
                raise PermissionError(message)

            raise RuntimeError(
                f"D1 API HTTP {exc.code}: {message}"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                f"Kunde inte ansluta till ARN D1 API: {exc}"
            ) from exc

        except TimeoutError as exc:
            raise RuntimeError(
                "Timeout mot ARN D1 API."
            ) from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"ARN D1 API returnerade ogiltig JSON (HTTP {status})."
            ) from exc

        if not isinstance(result, dict):
            return result

        if result.get("ok") is False:
            raise RuntimeError(
                result.get("error", "ARN D1 API rapporterade ett fel.")
            )

        return result

    def create_api_key(self, user_id: str) -> str:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        result = self._request(
            "create_api_key",
            user_id=user_id,
        )

        api_key = result.get("api_key")

        if not api_key:
            raise RuntimeError(
                "ARN D1 API returnerade ingen API-nyckel."
            )

        return api_key

    def user_id_from_api_key(self, api_key: str) -> str:
        api_key = api_key.strip()

        if not api_key:
            raise ValueError("api_key krävs.")

        result = self._request(
            "user_id_from_api_key",
            api_key=api_key,
        )

        user_id = result.get("user_id")

        if not user_id:
            raise ValueError("Ogiltig API-nyckel.")

        return user_id

    def check_api_key(self, api_key: str) -> dict:
        user_id = self.user_id_from_api_key(api_key)
        return self.check(user_id)

    def consume_api_key(self, api_key: str) -> dict:
        user_id = self.user_id_from_api_key(api_key)
        return self.consume(user_id)

    def activate_paid_api_key(self, api_key: str):
        user_id = self.user_id_from_api_key(api_key)
        self.activate_paid(user_id)

    def check(self, user_id: str) -> dict:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        return self._request(
            "check",
            user_id=user_id,
        )

    def consume(self, user_id: str) -> dict:
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        return self._request(
            "consume",
            user_id=user_id,
        )

    def check_and_consume(self, user_id: str) -> dict:
        status = self.check(user_id)

        if not status["allowed"]:
            return status

        return self.consume(user_id)

    def create_subscription(
        self,
        user_id: str,
        paypal_subscription_id: str,
        plan: str,
        amount_sek: int,
        status: str = "ACTIVE",
        started_at: str | None = None,
        expires_at: str | None = None,
    ):
        user_id = user_id.strip()
        paypal_subscription_id = paypal_subscription_id.strip()
        plan = plan.strip()
        status = status.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        if not plan:
            raise ValueError("plan krävs.")

        if amount_sek <= 0:
            raise ValueError("amount_sek måste vara större än 0.")

        self._request(
            "create_subscription",
            user_id=user_id,
            paypal_subscription_id=paypal_subscription_id,
            plan=plan,
            amount_sek=amount_sek,
            status=status,
            started_at=started_at,
            expires_at=expires_at,
        )

    def update_subscription_status(
        self,
        paypal_subscription_id: str,
        status: str,
        expires_at: str | None = None,
    ):
        paypal_subscription_id = paypal_subscription_id.strip()
        status = status.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        if not status:
            raise ValueError("status krävs.")

        self._request(
            "update_subscription_status",
            paypal_subscription_id=paypal_subscription_id,
            status=status,
            expires_at=expires_at,
        )

    def get_subscription(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        return self._request(
            "get_subscription",
            user_id=user_id,
        )

    def get_subscription_by_paypal_id(
        self,
        paypal_subscription_id: str,
    ):
        paypal_subscription_id = paypal_subscription_id.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        return self._request(
            "get_subscription_by_paypal_id",
            paypal_subscription_id=paypal_subscription_id,
        )

    def get_active_subscription(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        return self._request(
            "get_active_subscription",
            user_id=user_id,
        )

    def mark_subscription_cancel_requested(
        self,
        paypal_subscription_id: str,
    ):
        paypal_subscription_id = paypal_subscription_id.strip()

        if not paypal_subscription_id:
            raise ValueError("paypal_subscription_id krävs.")

        self._request(
            "mark_subscription_cancel_requested",
            paypal_subscription_id=paypal_subscription_id,
        )

    def deactivate_paid(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        self._request(
            "deactivate_paid",
            user_id=user_id,
        )

    def activate_paid(self, user_id: str):
        user_id = user_id.strip()

        if not user_id:
            raise ValueError("user_id krävs.")

        self._request(
            "activate_paid",
            user_id=user_id,
        )
