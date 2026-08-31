# waysdrop

Official Waysdrop Partner API SDK for Python.

## Install

```bash
pip install waysdrop
```

## Quickstart

```python
from waysdrop import WaysdropClient

client = WaysdropClient(api_key="wsp_staging_...", display_currency="NGN")
account = client.get_account()
client.close()
```

## Webhooks

```python
from waysdrop import verify_signature, parse_webhook

if not verify_signature(request.body, request.headers.get("x-waysdrop-signature"), API_KEY):
    return Response(status=401)
event = parse_webhook(request.body)
```

## License

MIT
