#!/usr/bin/env python3
"""Public client (PKCE) OAuth example — redirect user to authorizeUrl, then exchange code."""

from waysdrop.oauth import OAuthClient, generate_pkce_pair

client = OAuthClient(
    "wdo_staging_your_client_id_here",
    "https://example.com/oauth/callback",
)

pkce = generate_pkce_pair()
print("Redirect user to:", client.build_authorize_url(state="csrf", pkce=pkce))

# After callback:
# tokens = client.exchange_code(code, code_verifier=pkce["code_verifier"])
# user = client.get_user_info(tokens["access_token"])
