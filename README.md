# waysdrop (Python SDK)

Official Waysdrop **Partner API** SDK for Python 3.10+.

All 18 `/api/*` endpoints, TypedDict response types, sync + async clients, and webhook helpers.

## Install

```bash
pip install waysdrop
```

## Authentication

API keys (`wsp_live_…` / `wsp_staging_…`) are sent as the `api-key` header. Staging keys default to `https://staging-api.waysdrop.com`; live keys to `https://api.waysdrop.com`.

## Client

```python
from waysdrop import WaysdropClient

with WaysdropClient(
    api_key="wsp_staging_...",
    display_currency="NGN",
    correlation_id="req-123",
) as client:
    account = client.get_account()
```

Async variant: `AsyncWaysdropClient` (currently exposes `get_account` and `list_fleet_types`; extend as needed or use sync client for full coverage).

Errors raise `WaysdropError` with `status_code`, `message`, `details`, and `quota`.

---

## API reference

### Account

| Method          | HTTP               | Returns          |
| --------------- | ------------------ | ---------------- |
| `get_account()` | `GET /api/account` | `AccountSummary` |

```python
account = client.get_account()
```

### Locations

| Method                            | HTTP                 | Parameters       | Returns                 |
| --------------------------------- | -------------------- | ---------------- | ----------------------- |
| `list_countries(search=, limit=)` | `GET /api/countries` | optional filters | `list[CountryLocation]` |
| `list_states(search=, limit=)`    | `GET /api/states`    | optional filters | `list[StateLocation]`   |
| `list_cities(search=, limit=)`    | `GET /api/cities`    | optional filters | `list[CityLocation]`    |

```python
countries = client.list_countries(search="nigeria", limit=10)
```

### Routing & pricing

| Method                           | HTTP                   | Returns             |
| -------------------------------- | ---------------------- | ------------------- |
| `get_route(origin, destination)` | `POST /api/route`      | `RouteDataResponse` |
| `list_fleet_types()`             | `GET /api/fleet-types` | `list[FleetType]`   |
| `get_pricing(body, currency=)`   | `POST /api/pricing`    | `PricingResponse`   |

```python
route = client.get_route(
    {"address": "Ikeja, Lagos"},
    {"address": "Lekki, Lagos"},
)
pricing = client.get_pricing(
    {
        "origin": {"address": "Ikeja, Lagos"},
        "destination": {"address": "Lekki, Lagos"},
        "packagesId": ["package-uuid"],
        "courierSelection": "ANYONE",
    },
    currency="NGN",
)
```

### Packages

| Method                                      | HTTP                      | Returns                 |
| ------------------------------------------- | ------------------------- | ----------------------- |
| `create_or_update_package(body, currency=)` | `POST /api/package`       | `DeliveryPackage`       |
| `delete_package(package_id)`                | `DELETE /api/package/:id` | `None`                  |
| `list_packages(currency=)`                  | `GET /api/packages`       | `list[DeliveryPackage]` |

### Deliveries

| Method                                                        | HTTP                           | Returns                  |
| ------------------------------------------------------------- | ------------------------------ | ------------------------ |
| `create_delivery_request(body, currency=)`                    | `POST /api/request`            | `CreateDeliveryResponse` |
| `cancel_delivery_request(delivery_id)`                        | `POST /api/request/:id/cancel` | `CancelDeliveryResponse` |
| `list_deliveries(status=, search=, page=, limit=, currency=)` | `GET /api/deliveries`          | `ListDeliveriesResponse` |
| `get_delivery(delivery_id, currency=)`                        | `GET /api/deliveries/:id`      | `DeliveryDetail`         |

```python
created = client.create_delivery_request(
    {
        "origin": {"address": "Ikeja, Lagos"},
        "destination": {"address": "Lekki, Lagos"},
        "packagesId": [pkg["id"]],
        "type": "PICKUP",
        "courierSelection": "ANYONE",
        "destinationContactName": "Jane Doe",
        "destinationContactPhone": "+2348012345678",
        "destinationContactEmail": "jane@example.com",
    },
    currency="NGN",
)
```

### Wallet & payments

| Method                                     | HTTP                          | Returns                   |
| ------------------------------------------ | ----------------------------- | ------------------------- |
| `get_wallet(currency=)`                    | `GET /api/wallet`             | `MerchantWallet`          |
| `create_payment_checkout(body, currency=)` | `POST /api/payments/checkout` | `PaymentCheckoutResponse` |

### FX

| Method                                                 | HTTP                     | Returns                   |
| ------------------------------------------------------ | ------------------------ | ------------------------- |
| `get_exchange_rate(from_currency, to_currency)`        | `GET /api/exchange-rate` | `ExchangeRateResponse`    |
| `convert_currency(amount, from_currency, to_currency)` | `GET /api/convert`       | `ConvertCurrencyResponse` |

---

## Webhooks

```python
from waysdrop import verify_signature, parse_webhook, is_webhook_event

raw = request.body  # bytes, unchanged
if not verify_signature(raw, request.headers.get("x-waysdrop-signature"), api_key):
    raise PermissionError("invalid signature")

envelope = parse_webhook(raw)
if is_webhook_event(envelope, "p2p.delivery.created"):
    tracking_id = envelope["data"]["trackingId"]
```

---

## Types

Import from `waysdrop`: `AccountSummary`, `PricingResponse`, `DeliveryDetail`, `WebhookEnvelope`, `WebhookEventName`, etc.

---

## OAuth (v1.1)

```python
from waysdrop.oauth import OAuthClient, generate_pkce_pair

oauth = OAuthClient("wdo_staging_…", "https://example.com/oauth/callback")
pkce = generate_pkce_pair()
url = oauth.build_authorize_url(state="csrf", pkce=pkce)
# tokens = oauth.exchange_code(code, code_verifier=pkce["code_verifier"])
```

See `examples/oauth/` and [OAuth docs](https://docs.waysdrop.com/get-started/oauth).

---

## License

MIT
