from __future__ import annotations

import re

CLIENT_ID_PATTERN = re.compile(r"^wdo_(live|staging)_[a-f0-9]{32}$")


class OAuthError(Exception):
    def __init__(
        self,
        status_code: int,
        *,
        error: str | None = None,
        error_description: str | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(error_description or message or error or "OAuth request failed")
        self.status_code = status_code
        self.error = error
        self.error_description = error_description


def infer_oauth_issuer(client_id: str) -> str:
    if client_id.startswith("wdo_staging_"):
        return "https://staging-api.waysdrop.com"
    if client_id.startswith("wdo_live_"):
        return "https://api.waysdrop.com"
    return "https://staging-api.waysdrop.com"


def validate_client_id(client_id: str) -> None:
    if not CLIENT_ID_PATTERN.match(client_id):
        raise ValueError(
            "Invalid OAuth client ID format. Expected wdo_live_… or wdo_staging_… with 32 hex chars."
        )
