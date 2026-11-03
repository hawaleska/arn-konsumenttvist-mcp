# ARN Konsumenttvist MCP
# Copyright (c) 2026 Kim Andreas Hawaleska
# All rights reserved.

import jwt
import httpx
import asyncio
import json
from jwt.exceptions import PyJWTError
from mcp.server.auth.provider import AccessToken
from arn_license import LicenseManager

QYSLEY_ISSUER = "https://auth.qysley.se"
ARN_AUDIENCE = "https://mcp.qysley.se/arn"
JWKS_URL = f"{QYSLEY_ISSUER}/.well-known/jwks.json"
STATUS_URL = f"{QYSLEY_ISSUER}/access-token-status"


async def access_token_is_active(token):
    try:
        async with asyncio.timeout(3.0):
            return await _request_access_status(token)
    except Exception:
        return False


async def _request_access_status(token):
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0), follow_redirects=False,
                                 trust_env=False) as client:
        async with client.stream('POST', STATUS_URL, headers={
            'Authorization': 'Bearer '+token, 'Cache-Control': 'no-store',
            'Accept': 'application/json',
        }, content=b'') as response:
            if response.status_code != 200 or response.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
                return False
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > 128:
                    return False
            data = json.loads(body)
            return isinstance(data, dict) and set(data) == {'active'} and data['active'] is True


jwks_client = jwt.PyJWKClient(
    JWKS_URL,
    headers={"User-Agent": "ARN-Konsumenttvist-MCP/1.0"},
    timeout=10,
    cache_jwk_set=True,
    lifespan=300,
)


class ARNTokenVerifier:
    def __init__(self):
        self.license_manager = LicenseManager()

    async def verify_token(self, token: str) -> AccessToken | None:
        if not isinstance(token, str) or not token or len(token) > 8192:
            return None

        # JWT från Qysley Auth
        if token.count(".") == 2:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)

                claims = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    issuer=QYSLEY_ISSUER,
                    audience=ARN_AUDIENCE,
                    options={
                        "require": ["iss", "sub", "aud", "exp", "iat", "nbf"],
                    },
                )

                subject = claims["sub"]
                scopes = claims.get("scope", "").split()

                if not isinstance(subject, str) or not subject:
                    return None

                if "arn" not in scopes:
                    return None

                if not await access_token_is_active(token):
                    return None

                return AccessToken(
                    token=token,
                    client_id=subject,
                    scopes=scopes,
                    subject=f"qysley:{subject}",
                )

            except (PyJWTError, ValueError, TypeError, KeyError):
                return None

        # Befintliga ARN API-nycklar
        try:
            user_id = self.license_manager.user_id_from_api_key(token)
        except (ValueError, TypeError):
            return None

        return AccessToken(
            token=token,
            client_id=user_id,
            scopes=["arn"],
            subject=user_id,
        )


def get_authenticated_user_id() -> str:
    from mcp.server.auth.middleware.auth_context import auth_context_var

    user = auth_context_var.get()

    if user is None:
        raise ValueError("Ingen autentiserad MCP-användare.")

    return user.identity
