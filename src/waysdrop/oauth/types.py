from __future__ import annotations

import base64
import hashlib
import secrets
from typing import Literal, TypedDict, cast

OAuthScope = Literal["openid", "profile", "email", "store", "courier"]


class ProfileSummary(TypedDict, total=False):
    id: str
    name: str | None
    tag: str | None
    description: str | None
    profile_photo: str | None


class UserInfo(TypedDict, total=False):
    sub: str
    email: str | None
    email_verified: bool
    name: str | None
    picture: str | None
    phone: str | None
    phone_verified: bool
    personal_profile: ProfileSummary | None
    store_profiles: list[ProfileSummary]
    courier_profiles: list[ProfileSummary]


class TokenResponse(TypedDict):
    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int
    refresh_token: str
    scope: str


class DiscoveryDocument(TypedDict, total=False):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    revocation_endpoint: str
    response_types_supported: list[str]
    grant_types_supported: list[str]
    subject_types_supported: list[str]
    token_endpoint_auth_methods_supported: list[str]
    code_challenge_methods_supported: list[str]
    scopes_supported: list[str]


class PkcePair(TypedDict):
    code_verifier: str
    code_challenge: str
    code_challenge_method: Literal["S256"]
