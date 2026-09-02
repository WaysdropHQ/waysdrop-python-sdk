from __future__ import annotations

from typing import Sequence
from urllib.parse import urlencode

from waysdrop.oauth.types import PkcePair

DEFAULT_SCOPES = ("openid", "profile", "email")


def build_authorize_url(
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    *,
    scope: str | Sequence[str] | None = None,
    state: str | None = None,
    pkce: PkcePair | None = None,
) -> str:
    scopes = " ".join(scope) if isinstance(scope, (list, tuple)) else (scope or " ".join(DEFAULT_SCOPES))
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
    }
    if state:
        params["state"] = state
    if pkce:
        params["code_challenge"] = pkce["code_challenge"]
        params["code_challenge_method"] = pkce["code_challenge_method"]
    return f"{authorization_endpoint}?{urlencode(params)}"
