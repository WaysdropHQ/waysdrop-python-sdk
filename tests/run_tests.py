#!/usr/bin/env python3
import sys
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "waysdrop"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SRC / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def bootstrap_package() -> None:
    pkg = importlib.util.module_from_spec(
        importlib.util.spec_from_loader("waysdrop", loader=None)
    )
    sys.modules["waysdrop"] = pkg
    types_mod = load_module("waysdrop.types", "types.py")
    sys.modules["waysdrop.types"] = types_mod


bootstrap_package()
errors = load_module("waysdrop_errors", "errors.py")
webhooks = load_module("waysdrop_webhooks", "webhooks.py")

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[2] / "waysdrop-api-spec" / "fixtures" / "signature.json").read_text()
)


def test_validate_api_key():
    try:
        errors.validate_api_key("bad")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    errors.validate_api_key(FIXTURE["apiKey"])


def test_infer_base_url():
    assert errors.infer_base_url(FIXTURE["apiKey"]) == "https://staging-api.waysdrop.com"


def test_verify_signature():
    assert webhooks.verify_signature(FIXTURE["rawBody"], FIXTURE["signature"], FIXTURE["apiKey"])
    assert not webhooks.verify_signature(FIXTURE["rawBody"], "bad", FIXTURE["apiKey"])


def test_parse_webhook():
    parsed = webhooks.parse_webhook(FIXTURE["rawBody"])
    assert parsed["event"] == "p2p.delivery.created"
    assert parsed["data"]["trackingId"] == "P2P-TEST-001"


def test_waysdrop_error():
    err = errors.WaysdropError("quota", status_code=429, quota={"limit": 1000})
    assert err.status_code == 429


if __name__ == "__main__":
    test_validate_api_key()
    test_infer_base_url()
    test_verify_signature()
    test_parse_webhook()
    test_waysdrop_error()
    print("all tests passed")
