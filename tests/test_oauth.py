import json
from pathlib import Path

from waysdrop.oauth import (
    OAuthClient,
    OAuthError,
    build_authorize_url,
    generate_code_challenge,
    generate_pkce_pair,
    infer_oauth_issuer,
    validate_client_id,
)

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "oauth.json").read_text())


def test_validate_client_id() -> None:
    try:
        validate_client_id("bad")
        assert False, "expected ValueError"
    except ValueError:
        pass
    validate_client_id(FIXTURE["clientId"])


def test_infer_oauth_issuer() -> None:
    assert infer_oauth_issuer(FIXTURE["clientId"]) == "https://staging-api.waysdrop.com"
    assert infer_oauth_issuer("wdo_live_" + "a" * 32) == "https://api.waysdrop.com"


def test_pkce_vector() -> None:
    assert (
        generate_code_challenge(FIXTURE["code_verifier"], "S256")
        == FIXTURE["code_challenge"]
    )
    pair = generate_pkce_pair()
    assert pair["code_challenge_method"] == "S256"
    assert generate_code_challenge(pair["code_verifier"], "S256") == pair["code_challenge"]


def test_build_authorize_url() -> None:
    pkce = generate_pkce_pair()
    url = build_authorize_url(
        FIXTURE["discovery"]["authorization_endpoint"],
        FIXTURE["clientId"],
        FIXTURE["redirectUri"],
        scope="openid profile",
        state="xyz",
        pkce=pkce,
    )
    assert "client_id=" in url
    assert "code_challenge=" in url
    assert "state=xyz" in url


class MockTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def handle(self, request):
        import httpx

        url = str(request.url)
        self.calls.append((request.method, url))
        if "/oauth/token" in url:
            return httpx.Response(200, json=FIXTURE["tokenResponse"])
        if "/oauth/userinfo" in url:
            return httpx.Response(200, json=FIXTURE["userInfo"])
        if "/oauth/revoke" in url:
            return httpx.Response(200, json={"revoked": True})
        if "/.well-known/openid-configuration" in url:
            return httpx.Response(200, json=FIXTURE["discovery"])
        return httpx.Response(404, json={"error": "not_found"})


def test_oauth_client_flow() -> None:
    import httpx

    transport = MockTransport()
    with httpx.Client(transport=httpx.MockTransport(transport.handle)) as http:
        client = OAuthClient(
            FIXTURE["clientId"],
            FIXTURE["redirectUri"],
            client_secret="wdos_secret",
            client=http,
        )
        discovery = client.get_discovery()
        assert discovery["issuer"] == FIXTURE["discovery"]["issuer"]
        tokens = client.exchange_code("code123", code_verifier=FIXTURE["code_verifier"])
        assert tokens["access_token"] == FIXTURE["tokenResponse"]["access_token"]
        user = client.get_user_info(tokens["access_token"])
        assert user["sub"] == FIXTURE["userInfo"]["sub"]
        client.revoke_token(tokens["refresh_token"])
        assert any("/oauth/revoke" in url for _, url in transport.calls)


def test_oauth_error() -> None:
    import httpx

    def handler(request):
        return httpx.Response(
            400,
            json={"error": "invalid_grant", "error_description": "Code expired"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        client = OAuthClient(FIXTURE["clientId"], FIXTURE["redirectUri"], client=http)
        try:
            client.exchange_code("bad")
            assert False, "expected OAuthError"
        except OAuthError as err:
            assert err.status_code == 400
            assert err.error == "invalid_grant"
