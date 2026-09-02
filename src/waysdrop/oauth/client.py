from __future__ import annotations

from typing import cast

import httpx

from waysdrop.oauth.authorize import build_authorize_url
from waysdrop.oauth.errors import OAuthError, infer_oauth_issuer, validate_client_id
from waysdrop.oauth.types import DiscoveryDocument, PkcePair, TokenResponse, UserInfo

DEFAULT_SCOPES = ("openid", "profile", "email")


class OAuthClient:
    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        *,
        client_secret: str | None = None,
        issuer: str | None = None,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        validate_client_id(client_id)
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._issuer = (issuer or infer_oauth_issuer(client_id)).rstrip("/")
        self._timeout = timeout
        self._client = client or httpx.Client(timeout=timeout)
        self._discovery: DiscoveryDocument | None = None

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OAuthClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get_discovery(self) -> DiscoveryDocument:
        if self._discovery is None:
            res = self._client.get(f"{self._issuer}/oauth/.well-known/openid-configuration")
            res.raise_for_status()
            self._discovery = cast(DiscoveryDocument, res.json())
        return self._discovery

    def build_authorize_url(
        self,
        *,
        scope: str | Sequence[str] | None = None,
        state: str | None = None,
        pkce: PkcePair | None = None,
    ) -> str:
        return build_authorize_url(
            f"{self._issuer}/oauth/authorize",
            self._client_id,
            self._redirect_uri,
            scope=scope,
            state=state,
            pkce=pkce,
        )

    def exchange_code(self, code: str, *, code_verifier: str | None = None) -> TokenResponse:
        body: dict[str, str] = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self._client_id,
        }
        if self._client_secret:
            body["client_secret"] = self._client_secret
        if code_verifier:
            body["code_verifier"] = code_verifier
        return self._token_request(body)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        body: dict[str, str] = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
        }
        if self._client_secret:
            body["client_secret"] = self._client_secret
        return self._token_request(body)

    def revoke_token(self, token: str) -> None:
        body: dict[str, str] = {
            "token": token,
            "client_id": self._client_id,
        }
        if self._client_secret:
            body["client_secret"] = self._client_secret
        self._request("POST", "/oauth/revoke", json=body)

    def get_user_info(self, access_token: str) -> UserInfo:
        return cast(
            UserInfo,
            self._request(
                "GET",
                "/oauth/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ),
        )

    def _token_request(self, body: dict[str, str]) -> TokenResponse:
        return cast(TokenResponse, self._request("POST", "/oauth/token", json=body))

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        res = self._client.request(
            method,
            f"{self._issuer}{path}",
            json=json,
            headers={"Accept": "application/json", **(headers or {})},
        )
        payload = res.json() if res.content else {}
        if res.status_code >= 400:
            raise OAuthError(
                res.status_code,
                error=payload.get("error") if isinstance(payload, dict) else None,
                error_description=payload.get("error_description") if isinstance(payload, dict) else None,
                message=payload.get("message") if isinstance(payload, dict) else None,
            )
        return cast(dict[str, object], payload)
