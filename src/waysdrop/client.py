from __future__ import annotations

from typing import Mapping, cast

import httpx

from waysdrop.types import (
    FleetType,
    CityLocation,
    StateLocation,
    AccountSummary,
    DeliveryDetail,
    MerchantWallet,
    CountryLocation,
    DeliveryPackage,
    PricingResponse,
    WebhookEnvelope,
    RouteDataResponse,
    ExchangeRateResponse,
    CancelDeliveryResponse,
    CreateDeliveryResponse,
    ListDeliveriesResponse,
    ConvertCurrencyResponse,
    PaymentCheckoutResponse,
)
from waysdrop.errors import WaysdropError, infer_base_url, validate_api_key


class WaysdropClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        display_currency: str | None = None,
        correlation_id: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        validate_api_key(api_key)
        self._api_key = api_key
        self._base_url = (base_url or infer_base_url(api_key)).rstrip("/")
        self._timeout = timeout
        self._display_currency = display_currency
        self._correlation_id = correlation_id
        self._client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WaysdropClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def list_countries(self, *, search: str | None = None, limit: int | None = None) -> list[CountryLocation]:
        return cast(list[CountryLocation], self._get("/api/countries", search=search, limit=limit))

    def list_states(self, *, search: str | None = None, limit: int | None = None) -> list[StateLocation]:
        return cast(list[StateLocation], self._get("/api/states", search=search, limit=limit))

    def list_cities(self, *, search: str | None = None, limit: int | None = None) -> list[CityLocation]:
        return cast(list[CityLocation], self._get("/api/cities", search=search, limit=limit))

    def get_route(self, origin: dict, destination: dict) -> RouteDataResponse:
        return cast(RouteDataResponse, self._post("/api/route", {"origin": origin, "destination": destination}))

    def list_fleet_types(self) -> list[FleetType]:
        return cast(list[FleetType], self._get("/api/fleet-types"))

    def get_pricing(self, body: dict, *, currency: str | None = None) -> PricingResponse:
    def create_or_update_package(self, body: dict, *, currency: str | None = None) -> DeliveryPackage:
        return cast(PricingResponse, self._post("/api/pricing", self._with_currency(body, currency), currency=currency))

    def create_delivery_request(self, body: dict, *, currency: str | None = None) -> CreateDeliveryResponse:

        self._request("DELETE", f"/api/package/{package_id}")
        return cast(CreateDeliveryResponse, self._post("/api/request", self._with_currency(body, currency), currency=currency))
    def cancel_delivery_request(self, delivery_id: str) -> CancelDeliveryResponse:
        return cast(CancelDeliveryResponse, self._post(f"/api/request/{delivery_id}/cancel", {}))


        return cast(DeliveryPackage, self._post("/api/package", self._with_currency(body, currency), currency=currency))

    def delete_package(self, package_id: str) -> None:
    def list_packages(self, *, currency: str | None = None) -> list[DeliveryPackage]:
        return cast(list[DeliveryPackage], self._get("/api/packages", currency=currency))

    def get_wallet(self, *, currency: str | None = None) -> MerchantWallet:
        return cast(MerchantWallet, self._get("/api/wallet", currency=currency))

    def create_payment_checkout(self, body: dict, *, currency: str | None = None) -> PaymentCheckoutResponse:
        return cast(PaymentCheckoutResponse, self._post("/api/payments/checkout", self._with_currency(body, currency), currency=currency))

    def get_account(self) -> AccountSummary:
        return cast(AccountSummary, self._get("/api/account"))

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> ExchangeRateResponse:
        return cast(ExchangeRateResponse, self._get("/api/exchange-rate", from_=from_currency, to=to_currency))

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> ConvertCurrencyResponse:
        return cast(ConvertCurrencyResponse, self._get("/api/convert", amount=amount, from_=from_currency, to=to_currency))

    def list_deliveries(
        self,
        *,
        status: str | None = None,
        search: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        currency: str | None = None,
    ) -> ListDeliveriesResponse:
        return cast(
            ListDeliveriesResponse,
            self._get("/api/deliveries", status=status, search=search, page=page, limit=limit, currency=currency),
        )

    def get_delivery(self, delivery_id: str, *, currency: str | None = None) -> DeliveryDetail:
        return cast(DeliveryDetail, self._get(f"/api/deliveries/{delivery_id}", currency=currency))

    def _with_currency(self, body: dict, currency: str | None) -> dict:
        c = currency or self._display_currency
        if c and "currency" not in body:
            return {**body, "currency": c}
        return body

    def _get(self, path: str, **params: object) -> object:
        return self._request("GET", path, params={k: v for k, v in params.items() if v is not None})

    def _post(self, path: str, body: dict, *, currency: str | None = None) -> object:
        params: dict[str, str] = {}
        c = currency or self._display_currency
        if c:
            params["currency"] = c
        return self._request("POST", path, json=body, params=params or None)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object] | None = None,
        json: dict | None = None,
    ) -> object:
        headers = {"api-key": self._api_key, "Accept": "application/json"}
        if self._correlation_id:
            headers["X-Correlation-Id"] = self._correlation_id

        query = dict(params or {})
        if method == "GET" and self._display_currency and "currency" not in query:
            query.setdefault("currency", self._display_currency)

        response = self._client.request(
            method,
            f"{self._base_url}{path}",
            headers=headers,
            params=query or None,
            json=json,
        )

        if response.status_code == 204:
            return None

        data = response.json() if response.content else {}

        if not response.is_success:
            message = data.get("message", response.reason_phrase)
            if not isinstance(message, str):
                message = str(message)
            raise WaysdropError(
                message,
                status_code=data.get("statusCode", response.status_code),
                details=data.get("details"),
                quota=data.get("quota"),
                path=data.get("path"),
            )

        if isinstance(data, dict) and data.get("success") is True and "data" in data:
            return data["data"]
        return data


class AsyncWaysdropClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        display_currency: str | None = None,
        correlation_id: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        validate_api_key(api_key)
        self._api_key = api_key
        self._base_url = (base_url or infer_base_url(api_key)).rstrip("/")
        self._timeout = timeout
        self._display_currency = display_currency
        self._correlation_id = correlation_id
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_account(self) -> AccountSummary:
        return cast(AccountSummary, await self._arequest("GET", "/api/account"))

    async def list_fleet_types(self) -> list[FleetType]:
        return cast(list[FleetType], await self._arequest("GET", "/api/fleet-types"))

    async def _arequest(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object] | None = None,
        json: dict | None = None,
    ) -> object:
        headers = {"api-key": self._api_key, "Accept": "application/json"}
        if self._correlation_id:
            headers["X-Correlation-Id"] = self._correlation_id

        response = await self._client.request(
            method,
            f"{self._base_url}{path}",
            headers=headers,
            params=params,
            json=json,
        )

        if response.status_code == 204:
            return None

        data = response.json() if response.content else {}
        if not response.is_success:
            message = data.get("message", response.reason_phrase)
            if not isinstance(message, str):
                message = str(message)
            raise WaysdropError(
                message,
                status_code=data.get("statusCode", response.status_code),
                details=data.get("details"),
                quota=data.get("quota"),
            )

        if isinstance(data, dict) and data.get("success") is True and "data" in data:
            return data["data"]
        return data
