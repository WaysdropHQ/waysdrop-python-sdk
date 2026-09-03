import re
from typing import Any, Literal, Optional

SECRET_KEY_PATTERN = re.compile(r"^wsp_(live|staging)_[a-f0-9]{64}$")
PUBLIC_KEY_PATTERN = re.compile(r"^wsp_pub_(live|staging)_[a-f0-9]{64}$")

ApiKeyType = Literal["secret", "public"]


class WaysdropError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        details: Optional[dict[str, Any]] = None,
        quota: Optional[dict[str, Any]] = None,
        path: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details
        self.quota = quota
        self.path = path


def infer_key_type(api_key: str) -> ApiKeyType:
    if PUBLIC_KEY_PATTERN.match(api_key):
        return "public"
    if SECRET_KEY_PATTERN.match(api_key):
        return "secret"
    raise ValueError(
        "Invalid API key format. Expected secret (wsp_live_/wsp_staging_) "
        "or public (wsp_pub_live_/wsp_pub_staging_) with 64 hex chars."
    )


def validate_api_key(api_key: str) -> None:
    if not SECRET_KEY_PATTERN.match(api_key) and not PUBLIC_KEY_PATTERN.match(api_key):
        raise ValueError(
            "Invalid API key format. Expected wsp_live_/wsp_staging_ or "
            "wsp_pub_live_/wsp_pub_staging_ with 64 hex chars."
        )


def infer_base_url(api_key: str) -> str:
    if "_staging_" in api_key:
        return "https://staging-api.waysdrop.com"
    if "_live_" in api_key:
        return "https://api.waysdrop.com"
    return "https://staging-api.waysdrop.com"
