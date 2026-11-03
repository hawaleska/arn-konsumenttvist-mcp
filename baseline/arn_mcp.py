# ARN Konsumenttvist MCP
# Copyright (c) 2026 Kim Andreas Hawaleska
# All rights reserved.
# Proprietary software. Unauthorized copying, modification,
# redistribution, or commercial use is prohibited without permission.
# Contact: support@qysley.se

from __future__ import annotations

import json

import base64
import html
import os
import sqlite3
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from mcp.server.auth.settings import AuthSettings

from arn_auth import ARNTokenVerifier, get_authenticated_user_id
from arn_client import ARNClient
from arn_license import LicenseManager
from arn_public_responses import public_response
from arn_errors import failure, safe_event, tool_errors, route_errors, http_error


# ============================================================
# BASIC CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
LICENSE_DB = BASE_DIR / "arn_license.db"


def load_env_file():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key:
            os.environ[key] = value


load_env_file()


# ============================================================
# PUBLIC URL / AUTH
# ============================================================

ARN_PUBLIC_URL = os.getenv(
    "ARN_PUBLIC_URL",
    "https://mcp.qysley.se/arn",
).rstrip("/")


# ============================================================
# PAYPAL CONFIGURATION
# ============================================================

PAYPAL_ENV = os.getenv("PAYPAL_ENV", "sandbox").lower().strip()

if PAYPAL_ENV == "live":
    PAYPAL_API_BASE = "https://api-m.paypal.com"
else:
    PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"


PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")

PAYPAL_MONTHLY_PLAN_ID = os.getenv(
    "PAYPAL_MONTHLY_PLAN_ID",
    "P-80851304UG961843DNLNZ2ZQ",
)

PAYPAL_YEARLY_PLAN_ID = os.getenv(
    "PAYPAL_YEARLY_PLAN_ID",
    "P-6AY53511LL407783BNLNZ27A",
)


PAYPAL_MONTHLY_AMOUNT = 59
PAYPAL_YEARLY_AMOUNT = 590


if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
    raise RuntimeError("PayPal credentials saknas i .env")


# ============================================================
# MCP SERVER
# ============================================================

token_verifier = ARNTokenVerifier()

auth_settings = AuthSettings(
    issuer_url="https://auth.qysley.se",
    resource_server_url=ARN_PUBLIC_URL,
    required_scopes=["arn"],
    validate_token_resource=False,
)

server = MCPServer(
    name="ARN Konsumenttvist",
    description=(
        "MCP-server för sökning och hämtning av offentliga "
        "beslut från Allmänna reklamationsnämnden (ARN)."
    ),
    version="1.0.3",
    token_verifier=token_verifier,
    auth=auth_settings,
)

client = ARNClient()
license_manager = LicenseManager()


# ============================================================
# PAYPAL TOKEN CACHE
# ============================================================

_paypal_token = None
_paypal_token_expires_at = 0.0


def paypal_access_token():
    global _paypal_token
    global _paypal_token_expires_at

    now = time.time()

    if _paypal_token and now < (_paypal_token_expires_at - 60):
        return _paypal_token

    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={
            "grant_type": "client_credentials",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    _paypal_token = data["access_token"]

    expires_in = int(data.get("expires_in", 900))
    _paypal_token_expires_at = now + expires_in

    return _paypal_token



def verify_paypal_webhook_with_api(
    body: bytes,
    headers: dict,
) -> bool:
    try:
        payload = json.loads(body.decode("utf-8"))

        verify_payload = {
            "auth_algo": headers.get("PAYPAL-AUTH-ALGO"),
            "cert_url": headers.get("PAYPAL-CERT-URL"),
            "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID"),
            "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG"),
            "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
            "webhook_id": PAYPAL_WEBHOOK_ID,
            "webhook_event": payload,
        }

        safe_event('verify_paypal_webhook_with_api')

        response = requests.post(
            f"{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {paypal_access_token()}",
            },
            json=verify_payload,
            timeout=30,
        )

        safe_event('verify_paypal_webhook_with_api', status=response.status_code)

        if response.status_code != 200:
            return False

        return response.json().get("verification_status") == "SUCCESS"

    except Exception as exc:
        failure('backend_unavailable', 'verify_paypal_webhook_with_api', exc)
        return False


# ============================================================
# PAYPAL CERTIFICATE CACHE
# ============================================================

_paypal_cert_cache = {}

ALLOWED_PAYPAL_CERT_HOSTS = {
    "api.paypal.com",
    "api-m.paypal.com",
    "api.sandbox.paypal.com",
    "api-m.sandbox.paypal.com",
}


def get_paypal_certificate(cert_url: str):
    parsed = urlparse(cert_url)

    if parsed.scheme != "https":
        raise ValueError("PayPal cert_url måste använda HTTPS.")

    if not parsed.hostname:
        raise ValueError("PayPal cert_url saknar hostname.")

    hostname = parsed.hostname.lower()

    if hostname not in ALLOWED_PAYPAL_CERT_HOSTS:
        raise ValueError(
            f"Otillåten PayPal cert-host: {hostname}"
        )

    cached = _paypal_cert_cache.get(cert_url)

    if cached:
        return cached

    response = requests.get(
        cert_url,
        timeout=30,
    )

    response.raise_for_status()

    certificate = x509.load_pem_x509_certificate(
        response.content
    )

    _paypal_cert_cache[cert_url] = certificate

    return certificate


# ============================================================
# PAYPAL LOCAL SIGNATURE VERIFICATION
# ============================================================

def verify_paypal_signature(
    body: bytes,
    auth_algo: str,
    cert_url: str,
    transmission_id: str,
    transmission_sig: str,
    transmission_time: str,
    webhook_id: str,
) -> bool:

    if auth_algo.upper() != "SHA256WITHRSA":
        safe_event('verify_paypal_signature')
        return False

    try:
        certificate = get_paypal_certificate(cert_url)

        crc = zlib.crc32(body) & 0xFFFFFFFF

        message = (
            f"{transmission_id}|"
            f"{transmission_time}|"
            f"{webhook_id}|"
            f"{crc}"
        ).encode("utf-8")

        signature = base64.b64decode(
            transmission_sig,
            validate=True,
        )

        certificate.public_key().verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        return True

    except InvalidSignature:
        return False

    except Exception as exc:
        failure('backend_unavailable', 'verify_paypal_signature', exc)
        return False


def verify_paypal_webhook(
    body: bytes,
    auth_algo: str,
    cert_url: str,
    transmission_id: str,
    transmission_sig: str,
    transmission_time: str,
) -> bool:

    if not PAYPAL_WEBHOOK_ID:
        safe_event('verify_paypal_webhook')
        return False

    # --------------------------------------------------------
    # Först: normalt registrerat webhook-ID.
    # Detta gäller riktiga PayPal-events.
    # --------------------------------------------------------

    if verify_paypal_signature(
        body,
        auth_algo,
        cert_url,
        transmission_id,
        transmission_sig,
        transmission_time,
        PAYPAL_WEBHOOK_ID,
    ):
        return True

    # --------------------------------------------------------
    # PayPal Simulator:
    # Simulatorn använder bokstavligen "WEBHOOK_ID".
    #
    # Vi avgör INTE simulator genom event-id.
    # Riktiga PayPal-event kan också börja med WH-.
    # --------------------------------------------------------

    if PAYPAL_ENV == "sandbox":

        parsed = urlparse(cert_url)
        hostname = (
            parsed.hostname.lower()
            if parsed.hostname
            else ""
        )

        if hostname == "api.paypal.com":

            if verify_paypal_signature(
                body,
                auth_algo,
                cert_url,
                transmission_id,
                transmission_sig,
                transmission_time,
                "WEBHOOK_ID",
            ):
                safe_event('verify_paypal_webhook')
                return True

    return False


# ============================================================
# PAYPAL WEBHOOK DATABASE / IDEMPOTENCY
# ============================================================

def init_paypal_webhook_store():

    with sqlite3.connect(LICENSE_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS paypal_webhook_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                received_at TEXT NOT NULL,
                processed_at TEXT,
                status TEXT NOT NULL
            )
            """
        )

        conn.commit()


def claim_paypal_event(
    event_id: str,
    event_type: str,
) -> bool:

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(LICENSE_DB) as conn:

        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO paypal_webhook_events
            (
                event_id,
                event_type,
                received_at,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                event_id,
                event_type,
                now,
                "processing",
            ),
        )

        conn.commit()

        return cursor.rowcount == 1


def complete_paypal_event(event_id: str):

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(LICENSE_DB) as conn:

        conn.execute(
            """
            UPDATE paypal_webhook_events
            SET
                processed_at = ?,
                status = ?
            WHERE event_id = ?
            """,
            (
                now,
                "processed",
                event_id,
            ),
        )

        conn.commit()


def release_paypal_event(event_id: str):

    with sqlite3.connect(LICENSE_DB) as conn:

        conn.execute(
            """
            DELETE FROM paypal_webhook_events
            WHERE event_id = ?
            """,
            (event_id,),
        )

        conn.commit()


# ============================================================
# PAYPAL HELPERS
# ============================================================

def paypal_plan_from_id(plan_id: str | None):

    if plan_id == PAYPAL_MONTHLY_PLAN_ID:
        return "monthly", PAYPAL_MONTHLY_AMOUNT

    if plan_id == PAYPAL_YEARLY_PLAN_ID:
        return "yearly", PAYPAL_YEARLY_AMOUNT

    return None, None


def get_subscription_id_from_resource(resource: dict):

    return (
        resource.get("id")
        or resource.get("subscription_id")
        or resource.get("billing_agreement_id")
    )


def get_user_id_from_subscription(
    paypal_subscription_id: str,
    resource: dict,
):

    custom_id = resource.get("custom_id")

    if custom_id:
        return str(custom_id).strip()

    try:
        subscription = (
            license_manager.get_subscription_by_paypal_id(
                paypal_subscription_id
            )
        )

        if subscription:
            return subscription.get("user_id")

    except Exception as exc:
        failure('backend_unavailable', 'get_user_id_from_subscription', exc)

    return None


def store_subscription_if_possible(
    user_id: str | None,
    paypal_subscription_id: str | None,
    resource: dict,
    status: str,
):

    if not user_id or not paypal_subscription_id:
        return

    plan_id = resource.get("plan_id")

    plan, amount = paypal_plan_from_id(plan_id)

    if not plan:
        existing = None

        try:
            existing = (
                license_manager.get_subscription_by_paypal_id(
                    paypal_subscription_id
                )
            )
        except Exception:
            pass

        if existing:
            plan = existing.get("plan")
            amount = existing.get("amount_sek")

    if not plan or not amount:
        safe_event('store_subscription_if_possible')
        return

    started_at = (
        resource.get("start_time")
        or datetime.now(timezone.utc).isoformat()
    )

    billing_info = resource.get("billing_info") or {}

    expires_at = (
        billing_info.get("next_billing_time")
        or resource.get("next_billing_time")
    )

    license_manager.create_subscription(
        user_id=user_id,
        paypal_subscription_id=paypal_subscription_id,
        plan=plan,
        amount_sek=amount,
        status=status,
        started_at=started_at,
        expires_at=expires_at,
    )


# ============================================================
# PAYPAL EVENT PROCESSING
# ============================================================

def process_paypal_event(event: dict):

    event_type = event.get("event_type", "")
    resource = event.get("resource") or {}

    event_id = event.get("id")

    if not event_id:
        raise ValueError("PayPal event saknar event-id.")

    # --------------------------------------------------------
    # Subscription events
    # --------------------------------------------------------

    subscription_id = get_subscription_id_from_resource(
        resource
    )

    if event_type.startswith("BILLING.SUBSCRIPTION."):

        if not subscription_id:
            safe_event('process_paypal_event')
            return

        user_id = get_user_id_from_subscription(
            subscription_id,
            resource,
        )

        if event_type == "BILLING.SUBSCRIPTION.CREATED":

            store_subscription_if_possible(
                user_id,
                subscription_id,
                resource,
                "CREATED",
            )

            return

        if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":

            store_subscription_if_possible(
                user_id,
                subscription_id,
                resource,
                "ACTIVE",
            )

            if user_id:
                license_manager.activate_paid(user_id)

            return

        if event_type == "BILLING.SUBSCRIPTION.RE-ACTIVATED":

            store_subscription_if_possible(
                user_id,
                subscription_id,
                resource,
                "ACTIVE",
            )

            if user_id:
                license_manager.activate_paid(user_id)

            return

        if event_type == "BILLING.SUBSCRIPTION.UPDATED":

            status = str(
                resource.get("status", "UPDATED")
            ).upper()

            if status == "ACTIVE" and user_id:
                license_manager.activate_paid(user_id)

            try:
                license_manager.update_subscription_status(
                    subscription_id,
                    status,
                )
            except Exception:
                store_subscription_if_possible(
                    user_id,
                    subscription_id,
                    resource,
                    status,
                )

            return

        if event_type == "BILLING.SUBSCRIPTION.CANCELLED":

            billing_info = resource.get(
                "billing_info"
            ) or {}

            expires_at = (
                billing_info.get(
                    "next_billing_time"
                )
            )

            license_manager.update_subscription_status(
                subscription_id,
                "CANCELLED",
                expires_at=expires_at,
            )


            safe_event('process_paypal_event')

            return

        if event_type == "BILLING.SUBSCRIPTION.EXPIRED":

            license_manager.update_subscription_status(
                subscription_id,
                "EXPIRED",
            )


            return

        if event_type == "BILLING.SUBSCRIPTION.SUSPENDED":

            license_manager.update_subscription_status(
                subscription_id,
                "SUSPENDED",
            )

            return

        if event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":

            license_manager.update_subscription_status(
                subscription_id,
                "PAYMENT_FAILED",
            )

            return

        safe_event('process_paypal_event')

        return

    # --------------------------------------------------------
    # PAYMENT.SALE.COMPLETED
    # --------------------------------------------------------

    if event_type == "PAYMENT.SALE.COMPLETED":

        subscription_id = (
            resource.get("billing_agreement_id")
            or resource.get("subscription_id")
        )

        if not subscription_id:
            safe_event('process_paypal_event')
            return

        try:
            subscription = (
                license_manager.get_subscription_by_paypal_id(
                    subscription_id
                )
            )

            if subscription:
                user_id = subscription.get("user_id")

                license_manager.update_subscription_status(
                    subscription_id,
                    "ACTIVE",
                )

                if user_id:
                    license_manager.activate_paid(
                        user_id
                    )

        except Exception as exc:
            failure('backend_unavailable', 'process_paypal_event', exc)
            raise

        return

    safe_event('process_paypal_event')


# ============================================================
# PAYPAL WEBHOOK
# ============================================================

@server.custom_route(
    "/paypal/webhook",
    methods=["POST"],
    name="paypal_webhook",
    include_in_schema=False,
)
@route_errors('paypal_webhook')
async def paypal_webhook(request: Request):

    body = await request.body()

    try:
        event = await request.json()
    except Exception:
        return http_error('invalid_request', 'paypal_webhook', 400)

    auth_algo = request.headers.get(
        "PAYPAL-AUTH-ALGO"
    )

    cert_url = request.headers.get(
        "PAYPAL-CERT-URL"
    )

    transmission_id = request.headers.get(
        "PAYPAL-TRANSMISSION-ID"
    )

    transmission_sig = request.headers.get(
        "PAYPAL-TRANSMISSION-SIG"
    )

    transmission_time = request.headers.get(
        "PAYPAL-TRANSMISSION-TIME"
    )

    safe_event('paypal_webhook')

    if not all(
        [
            auth_algo,
            cert_url,
            transmission_id,
            transmission_sig,
            transmission_time,
        ]
    ):
        return http_error('invalid_request', 'paypal_webhook', 400)

    if not verify_paypal_webhook(
        body,
        auth_algo,
        cert_url,
        transmission_id,
        transmission_sig,
        transmission_time,
    ):
        safe_event('paypal_webhook')

        if not verify_paypal_webhook_with_api(
            body,
            request.headers,
        ):
            safe_event('paypal_webhook')

            return http_error('signature_invalid', 'paypal_webhook', 401)

        safe_event('paypal_webhook')

    event_id = event.get("id")

    event_type = event.get(
        "event_type",
        "UNKNOWN",
    )

    if not event_id:
        return http_error('missing_event_id', 'paypal_webhook', 400)

    # --------------------------------------------------------
    # Idempotency
    # --------------------------------------------------------

    if not claim_paypal_event(
        event_id,
        event_type,
    ):
        safe_event('paypal_webhook')

        return JSONResponse(
            {"status": "already_processed"}
        )

    try:

        process_paypal_event(event)

        complete_paypal_event(event_id)

    except Exception as exc:

        release_paypal_event(event_id)

        failure('backend_unavailable', 'paypal_webhook', exc)

        # 500 gör att PayPal kan försöka igen.
        return http_error('webhook_processing_failed', 'paypal_webhook', 500, exc)

    resource = event.get("resource") or {}

    safe_event('paypal_webhook')

    return JSONResponse(
        {"status": "received"}
    )


# ============================================================
# PAYPAL CREATE SUBSCRIPTION
# ============================================================

@server.tool(
    name="arn_create_subscription",
    title="Skapa prenumeration",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False),
    description=(
        "Skapa en PayPal-prenumeration för ARN Konsumenttvist. "
        "Välj monthly eller yearly. Verktyget returnerar en "
        "PayPal-länk där användaren godkänner prenumerationen."
    ),
)
@tool_errors('arn_create_subscription')
def arn_create_subscription(
    plan: str = "monthly",
) -> dict:

    user_id = get_authenticated_user_id()

    existing_subscription = license_manager.get_active_subscription(user_id)

    if existing_subscription:
        return {
            "error": "already_subscribed",
            "message": (
                "Du har redan en aktiv prenumeration. "
                "Avsluta den befintliga prenumerationen innan "
                "du tecknar en ny."
            ),
            "subscription_id": existing_subscription[
                "paypal_subscription_id"
            ],
            "plan": existing_subscription["plan"],
        }

    plan = plan.lower().strip()

    if plan not in {
        "monthly",
        "yearly",
    }:
        return {
            "error": "invalid_plan",
            "message": (
                "Plan måste vara 'monthly' "
                "eller 'yearly'."
            ),
        }

    if plan == "monthly":
        plan_id = PAYPAL_MONTHLY_PLAN_ID
        amount = PAYPAL_MONTHLY_AMOUNT

    else:
        plan_id = PAYPAL_YEARLY_PLAN_ID
        amount = PAYPAL_YEARLY_AMOUNT

    access_token = paypal_access_token()

    payload = {
        "plan_id": plan_id,
        "custom_id": user_id,
        "application_context": {
            "brand_name": "ARN Konsumenttvist",
            "locale": "sv-SE",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "SUBSCRIBE_NOW",
            "return_url": (
                f"{ARN_PUBLIC_URL}/paypal/success"
            ),
            "cancel_url": (
                f"{ARN_PUBLIC_URL}/paypal/cancel"
            ),
        },
    }

    response = requests.post(
        f"{PAYPAL_API_BASE}/v1/billing/subscriptions",
        headers={
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {access_token}"
            ),
        },
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    subscription_id = data.get("id")

    approval_url = None

    for link in data.get("links", []):
        if link.get("rel") == "approve":
            approval_url = link.get("href")
            break

    if subscription_id:
        license_manager.create_subscription(
            user_id=user_id,
            paypal_subscription_id=subscription_id,
            plan=plan,
            amount_sek=amount,
            status="APPROVAL_PENDING",
        )

    return {
        "status": "approval_pending",
        "plan": plan,
        "amount_sek": amount,
        "currency": "SEK",
        "paypal_subscription_id":
            subscription_id,
        "approval_url": approval_url,
        "message": (
            "Öppna approval_url för att slutföra "
            "PayPal-prenumerationen."
        ),
    }


# ============================================================
# PAYPAL SUCCESS PAGE
# ============================================================

@server.custom_route(
    "/paypal/success",
    methods=["GET"],
    name="paypal_success",
    include_in_schema=False,
)
@route_errors('paypal_success')
async def paypal_success(request: Request):

    subscription_id = (
        request.query_params.get(
            "subscription_id"
        )
        or request.query_params.get("token")
    )

    if subscription_id:

        try:

            access_token = paypal_access_token()

            response = requests.get(
                f"{PAYPAL_API_BASE}"
                f"/v1/billing/subscriptions/"
                f"{subscription_id}",
                headers={
                    "Authorization":
                        f"Bearer {access_token}",
                    "Accept":
                        "application/json",
                },
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

            status = str(
                data.get("status", "")
            ).upper()

            user_id = data.get("custom_id")

            if (
                status == "ACTIVE"
                and user_id
            ):

                plan_id = data.get("plan_id")

                plan, amount = paypal_plan_from_id(
                    plan_id
                )

                if plan and amount:

                    license_manager.create_subscription(
                        user_id=user_id,
                        paypal_subscription_id=
                            subscription_id,
                        plan=plan,
                        amount_sek=amount,
                        status="ACTIVE",
                        started_at=data.get(
                            "start_time"
                        ),
                    )

                license_manager.activate_paid(
                    user_id
                )

        except Exception as exc:

            failure('backend_unavailable', 'paypal_success', exc)

    return HTMLResponse(
        """
        <!doctype html>
        <html lang="sv">
        <head>
            <meta charset="utf-8">
            <title>ARN Konsumenttvist</title>
        </head>
        <body>
            <h1>Tack!</h1>
            <p>
                Din PayPal-prenumeration har registrerats.
            </p>
            <p>
                Om aktiveringen fortfarande behandlas
                sker den automatiskt via PayPal-webhooken.
            </p>
        </body>
        </html>
        """
    )


# ============================================================
# CANCEL ACTIVE PAYPAL SUBSCRIPTION
# ============================================================

@server.tool(
    name="arn_cancel_subscription",
    title="Avsluta prenumeration",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=False),
    description=(
        "Avsluta användarens aktiva PayPal-prenumeration. "
        "Det stoppar framtida förnyelser."
    ),
)
@tool_errors('arn_cancel_subscription')
def arn_cancel_subscription() -> dict:

    user_id = get_authenticated_user_id()

    subscription = license_manager.get_active_subscription(user_id)

    if not subscription:
        return {
            "error": "no_active_subscription",
            "message": "Du har ingen aktiv prenumeration att avsluta.",
        }

    paypal_subscription_id = subscription["paypal_subscription_id"]

    try:
        access_token = paypal_access_token()

        response = requests.post(
            f"{PAYPAL_API_BASE}/v1/billing/subscriptions/"
            f"{paypal_subscription_id}/cancel",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "reason": "Kunden har begärt att avsluta sin prenumeration."
            },
            timeout=30,
        )

        if response.status_code not in (200, 204):
            safe_event('arn_cancel_subscription', status=response.status_code)

            return {
                "error": "paypal_cancel_failed",
                "message": (
                    "PayPal kunde inte avsluta prenumerationen. "
                    "Försök igen senare."
                ),
                "status_code": response.status_code,
            }

        license_manager.mark_subscription_cancel_requested(
            paypal_subscription_id
        )

        return {
            "success": True,
            "message": (
                "Din prenumeration har avslutats och kommer inte "
                "att förnyas."
            ),
            "subscription_id": paypal_subscription_id,
            "plan": subscription["plan"],
        }

    except Exception as exc:
        failure('paypal_cancel_error', 'arn_cancel_subscription', exc)

        return {
            "error": failure('paypal_cancel_error', 'arn_cancel_subscription', exc),
            "message": (
                "Ett fel uppstod när prenumerationen skulle avslutas."
            ),
        }


# ============================================================
# PAYPAL CANCEL PAGE
# ============================================================

@server.custom_route(
    "/paypal/cancel",
    methods=["GET"],
    name="paypal_cancel",
    include_in_schema=False,
)
@route_errors('paypal_cancel')
async def paypal_cancel(request: Request):

    return HTMLResponse(
        """
        <!doctype html>
        <html lang="sv">
        <head>
            <meta charset="utf-8">
            <title>ARN Konsumenttvist</title>
        </head>
        <body>
            <h1>Betalningen avbröts</h1>
            <p>
                Ingen prenumeration aktiverades.
            </p>
        </body>
        </html>
        """
    )


# ============================================================
# ARN SEARCH
# ============================================================

@server.tool(
    name="arn_search",
    title="Sök ARN-beslut",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Sök efter ARN-beslut. Sökningen kan göras med "
        "ärendenummer, produkt, företag, problem eller fritext."
    ),
)
@public_response('arn_search')
def arn_search(
    query: str,
    category: str = "alla",
    outcome: str = "obegransad",
    from_year: str = "",
    to_year: str = "",
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    results = client.search(
        query=query,
        category=category,
        outcome=outcome,
        from_year=from_year,
        to_year=to_year,
    )

    license_status = license_manager.consume(
        user_id
    )

    return {
        "query": query,
        "count": len(results),
        "results": results,
        "license": license_status,
    }


# ============================================================
# ARN GET DECISION
# ============================================================

@server.tool(
    name="arn_get_decision",
    title="Hämta ARN-beslut",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Hämta hela texten från ett ARN-beslut genom "
        "att ange ärendenummer, exempelvis 2022-17895."
    ),
)
@public_response('arn_get_decision')
def arn_get_decision(
    case_number: str,
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    result = client.get_decision(
        case_number=case_number
    )

    license_status = license_manager.consume(
        user_id
    )

    return {
        "results": result,
        "license": license_status,
    }


# ============================================================
# ARN SEARCH AND READ
# ============================================================

@server.tool(
    name="arn_search_and_read",
    title="Sök och läs ARN-beslut",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Sök efter ARN-beslut och hämta den fullständiga "
        "beslutstexten för de första resultaten."
    ),
)
@public_response('arn_search_and_read')
def arn_search_and_read(
    query: str,
    category: str = "alla",
    outcome: str = "obegransad",
    from_year: str = "",
    to_year: str = "",
    max_results: int = 5,
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    max_results = max(
        1,
        min(max_results, 20),
    )

    results = client.search(
        query=query,
        category=category,
        outcome=outcome,
        from_year=from_year,
        to_year=to_year,
    )

    license_manager.consume(user_id)

    decisions = []

    for result in results[:max_results]:

        try:

            decision = client.get_decision(
                case_number=result["case_number"],
                file_id=result["file_id"],
                xsessiontag=result["xsessiontag"],
            )

            decisions.append(decision)

        except Exception as exc:

            decisions.append(
                {
                    **result,
                    "error": failure('decision_unavailable', 'arn_search_and_read', exc),
                }
            )

    return {
        "query": query,
        "count": len(decisions),
        "decisions": decisions,
    }


# ============================================================
# ARN SEARCH COMPANY
# ============================================================

@server.tool(
    name="arn_search_company",
    title="Sök företag i ARN",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Sök efter ARN-beslut kopplade till ett företag. "
        "Stödjer företag, kategori, utfall och årtal."
    ),
)
@public_response('arn_search_company')
def arn_search_company(
    company: str,
    category: str = "alla",
    outcome: str = "obegransad",
    from_year: str = "",
    to_year: str = "",
    max_results: int = 20,
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    max_results = max(
        1,
        min(max_results, 50),
    )

    results = client.search(
        query=company,
        category=category,
        outcome=outcome,
        from_year=from_year,
        to_year=to_year,
    )

    license_status = license_manager.consume(
        user_id
    )

    results = results[:max_results]

    return {
        "company": company,
        "category": category,
        "outcome": outcome,
        "from_year": from_year,
        "to_year": to_year,
        "count": len(results),
        "results": results,
        "license": license_status,
    }


# ============================================================
# ARN SEARCH COMPANY AND READ
# ============================================================

@server.tool(
    name="arn_search_company_and_read",
    title="Sök och läs företagsärenden",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Sök efter ARN-beslut kopplade till ett företag "
        "och hämta den fullständiga beslutstexten för "
        "de första resultaten."
    ),
)
@public_response('arn_search_company_and_read')
def arn_search_company_and_read(
    company: str,
    category: str = "alla",
    outcome: str = "obegransad",
    from_year: str = "",
    to_year: str = "",
    max_results: int = 5,
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    max_results = max(
        1,
        min(max_results, 20),
    )

    results = client.search(
        query=company,
        category=category,
        outcome=outcome,
        from_year=from_year,
        to_year=to_year,
    )

    license_manager.consume(user_id)

    decisions = []

    for result in results[:max_results]:

        try:

            decision = client.get_decision(
                case_number=result["case_number"],
                file_id=result["file_id"],
                xsessiontag=result["xsessiontag"],
            )

            decisions.append(decision)

        except Exception as exc:

            decisions.append(
                {
                    **result,
                    "error": failure('decision_unavailable', 'arn_search_company_and_read', exc),
                }
            )

    return {
        "company": company,
        "category": category,
        "outcome": outcome,
        "from_year": from_year,
        "to_year": to_year,
        "count": len(decisions),
        "decisions": decisions,
    }


# ============================================================
# ARN SIMILAR CASES
# ============================================================

@server.tool(
    name="arn_similar_cases",
    title="Hitta liknande ARN-ärenden",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False),
    description=(
        "Hitta tidigare ARN-beslut som kan vara relevanta "
        "för ett beskrivet konsumentproblem."
    ),
)
@public_response('arn_similar_cases')
def arn_similar_cases(
    problem: str,
    category: str = "alla",
    outcome: str = "obegransad",
    from_year: str = "",
    to_year: str = "",
    max_results: int = 10,
) -> dict:

    user_id = get_authenticated_user_id()

    license_status = license_manager.check(
        user_id
    )

    if not license_status["allowed"]:
        return {
            "error": "payment_required",
            "message": (
                "Du har använt dina 10 fria sökningar. "
                "Fortsatt användning kräver en aktiv prenumeration. "
                "Välj mellan 59 SEK/månad eller 590 SEK/år genom "
                "verktyget arn_create_subscription för att få en säker "
                "PayPal-betalningslänk."
            ),
            "license": license_status,
        }

    result = client.similar_cases(
        problem=problem,
        category=category,
        outcome=outcome,
        from_year=from_year,
        to_year=to_year,
        max_results=max_results,
    )

    license_manager.consume(user_id)

    return result


# ============================================================
# STARTUP
# ============================================================

init_paypal_webhook_store()


if __name__ == "__main__":

    transport = os.getenv(
        "MCP_TRANSPORT",
        "stdio",
    )

    if transport == "streamable-http":
        from mcp.server.streamable_http import TransportSecuritySettings

        transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[
                "mcp.qysley.se",
                "localhost",
                "127.0.0.1",
            ],
        )

        server.run(
            "streamable-http",
            transport_security=transport_security,
        )

    elif transport == "sse":
        server.run("sse")

    else:
        server.run("stdio")
