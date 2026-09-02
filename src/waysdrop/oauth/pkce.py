from __future__ import annotations

import base64
import hashlib
import secrets

from waysdrop.oauth.types import PkcePair


def generate_code_verifier(length: int = 64) -> str:
    raw = secrets.token_urlsafe(length)
    allowed = "".join(ch for ch in raw if ch.isalnum() or ch in "-._~")
    return allowed[:length]


def generate_code_challenge(code_verifier: str, method: str = "S256") -> str:
    if method == "plain":
        return code_verifier
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def generate_pkce_pair() -> PkcePair:
    code_verifier = generate_code_verifier()
    return {
        "code_verifier": code_verifier,
        "code_challenge": generate_code_challenge(code_verifier, "S256"),
        "code_challenge_method": "S256",
    }
