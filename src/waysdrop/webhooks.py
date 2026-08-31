import hmac
import json
import hashlib
from typing import Any, Union


def verify_signature(
    raw_body: Union[bytes, str],
    signature_header: str | None,
    api_key: str,
) -> bool:
    if not signature_header:
        return False
    body = raw_body if isinstance(raw_body, bytes) else raw_body.encode("utf-8")
    expected = hmac.new(api_key.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def parse_webhook(raw_body: Union[bytes, str]) -> dict[str, Any]:
    text = raw_body if isinstance(raw_body, str) else raw_body.decode("utf-8")
    payload = json.loads(text)
    if "event" not in payload or "data" not in payload:
        raise ValueError("Invalid webhook payload: expected { event, data }")
    return {"event": payload["event"], "data": payload["data"]}
