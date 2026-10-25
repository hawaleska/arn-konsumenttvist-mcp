# ARN Konsumenttvist MCP
# Copyright (c) 2026 Kim Andreas Hawaleska
# All rights reserved.
# Proprietary software. Unauthorized copying, modification,
# redistribution, or commercial use is prohibited without permission.
# Contact: hawaleska@gmail.com

from mcp.server.auth.provider import AccessToken
from arn_license import LicenseManager


class ARNTokenVerifier:
    def __init__(self):
        self.license_manager = LicenseManager()

    async def verify_token(self, token: str) -> AccessToken | None:
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
