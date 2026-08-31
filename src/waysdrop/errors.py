import re
from typing import Any, Optional

API_KEY_PATTERN = re.compile(r"^wsp_(live|staging)_[a-f0-9]{64}$")


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


def validate_api_key(api_key: str) -> None:
    if not API_KEY_PATTERN.match(api_key):
        raise ValueError(
            "Invalid API key format. Expected wsp_live_… or wsp_staging_… with 64 hex chars."
        )


def infer_base_url(api_key: str) -> str:
    if api_key.startswith("wsp_staging_"):
        return "https://staging-api.waysdrop.com"
    if api_key.startswith("wsp_live_"):
        return "https://api.waysdrop.com"
    return "https://staging-api.waysdrop.com"
