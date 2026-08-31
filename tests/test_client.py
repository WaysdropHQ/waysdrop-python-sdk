import json
from pathlib import Path

import pytest

from waysdrop.errors import WaysdropError, infer_base_url, validate_api_key
from waysdrop.webhooks import parse_webhook, verify_signature

FIXTURES = Path(__file__).resolve().parents[2] / "waysdrop-api-spec" / "fixtures"
SIGNATURE = json.loads((FIXTURES / "signature.json").read_text())


def test_validate_api_key():
    with pytest.raises(ValueError, match="Invalid API key"):
        validate_api_key("bad")
    validate_api_key(SIGNATURE["apiKey"])


def test_infer_base_url():
    assert infer_base_url(SIGNATURE["apiKey"]) == "https://staging-api.waysdrop.com"
    assert infer_base_url("wsp_live_" + "a" * 64) == "https://api.waysdrop.com"


def test_verify_signature():
    assert verify_signature(SIGNATURE["rawBody"], SIGNATURE["signature"], SIGNATURE["apiKey"])
    assert not verify_signature(SIGNATURE["rawBody"], "bad", SIGNATURE["apiKey"])


def test_parse_webhook():
    parsed = parse_webhook(SIGNATURE["rawBody"])
    assert parsed["event"] == "p2p.delivery.created"
    assert parsed["data"]["trackingId"] == "P2P-TEST-001"


def test_waysdrop_error():
    err = WaysdropError("quota", status_code=429, quota={"limit": 1000})
    assert err.status_code == 429
    assert err.quota == {"limit": 1000}
