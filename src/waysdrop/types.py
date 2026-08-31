from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

DeliveryStatus = Literal[
    "REQUEST_CREATED",
    "ASSIGNING",
    "ACCEPTED",
    "AWAITING_COLLECTION",
    "PACKAGE_COLLECTED",
    "IN_TRANSIT",
    "DELIVERED",
    "CANCELLED",
]

RouteType = Literal["INTRA_CITY", "INTER_CITY", "INTER_STATE", "INTER_COUNTRY"]
PackageSize = Literal["SMALL", "MEDIUM", "LARGE", "EXTRA_LARGE"]
PaymentProcessor = Literal["PAYSTACK", "NOMBA", "STRIPE"]
DeliveryType = Literal["P2P", "ERRAND", "STORE", "PERSONAL"]

WebhookEventName = Literal[
    "p2p.delivery.created",
    "p2p.delivery.cancelled",
    "errand.delivery.created",
    "errand.delivery.cancelled",
    "delivery.request.accepted",
    "delivery.request.declined",
    "delivery.awaiting.collection",
    "delivery.collected",
    "delivery.in.transit",
    "delivery.delivered",
    "delivery.reassignment.created",
    "delivery.reassignment.direct_assigned",
    "delivery.reassignment.requested",
    "delivery.reassignment.collected",
    "payment.received",
    "order.created",
    "order.cancelled",
    "order.confirmed",
    "order.declined",
    "order.requested",
]


class DisplayMoneyLocal(TypedDict, total=False):
    currency: str
    amount: float
    symbol: str


class DisplayMoney(TypedDict):
    usd: float
    local: NotRequired[DisplayMoneyLocal]


class DistanceInfo(TypedDict):
    distanceKm: float
    etaSeconds: float


class GeoLocation(TypedDict, total=False):
    id: str
    addressLine1: str
    lgaOrCity: str
    state: str
    country: str
    countryCode: str
    lat: float
    lon: float
    googlePlaceId: str


class CountryLocation(TypedDict, total=False):
    value: str
    name: str
    type: Literal["INTER_COUNTRY"]
    country: str
    countryCode: str


class StateLocation(TypedDict, total=False):
    value: str
    name: str
    type: Literal["INTER_STATE"]
    state: str
    country: str
    countryCode: str


class CityLocation(TypedDict, total=False):
    locationId: str
    value: str
    country: str
    countryCode: str
    lat: float
    lon: float
    lgaOrCity: str
    state: str


class FleetType(TypedDict, total=False):
    id: str
    name: str
    icon: str | None
    description: str | None


class PricingCosts(TypedDict, total=False):
    base: float | str
    weight: float | str
    fleet: float | str
    insurance: float | str
    surcharge: float | str
    serviceFee: float | str
    deliverySubtotal: float | str
    total: float | str
    totalDisplay: DisplayMoney


class PricingResponse(TypedDict, total=False):
    distance: DistanceInfo
    routeType: RouteType
    costs: PricingCosts


class RouteDataResponse(TypedDict):
    distance: DistanceInfo
    routeType: RouteType
    origin: GeoLocation
    destination: GeoLocation


class DeliveryPackage(TypedDict, total=False):
    id: str
    name: str
    quantity: int
    weight: float | str
    value: float | str
    valueDisplay: DisplayMoney
    size: PackageSize
    p2pDeliveryId: str | None


class DeliverySummary(TypedDict, total=False):
    id: str
    trackingId: str
    status: DeliveryStatus
    type: DeliveryType
    routeType: RouteType
    deliveryFee: float | str
    deliveryFeeDisplay: DisplayMoney
    origin: GeoLocation
    destination: GeoLocation


class DeliveryDetail(DeliverySummary, total=False):
    deliverySteps: list[dict[str, object]]
    proofs: list[dict[str, object]]
    fleetType: FleetType
    p2pDelivery: dict[str, object]
    courier: dict[str, object]


class CreateDeliveryResponse(TypedDict, total=False):
    id: str
    status: str
    totalWeight: float | str
    totalValue: float | str
    deliveryId: str
    delivery: DeliverySummary
    processor: PaymentProcessor
    reference: str
    charge_currency: str
    charge_amount: float
    authorization_url: str
    checkout_url: str


class CancelDeliveryResponse(TypedDict):
    delivery: dict[str, str]


class MerchantWallet(TypedDict, total=False):
    id: str
    currencyCode: str
    balance: str
    balanceDisplay: DisplayMoney


class PaymentCheckoutResponse(TypedDict, total=False):
    processor: PaymentProcessor
    reference: str
    charge_currency: str
    charge_amount: float
    authorization_url: str
    checkout_url: str


class StoreProfile(TypedDict):
    id: str
    name: str
    tag: str


class AccountSummary(TypedDict, total=False):
    userId: str
    countryCode: str
    displayCurrency: str
    merchantWalletCurrencyCode: str
    storeProfile: StoreProfile | None


ExchangeRateResponse = TypedDict(
    "ExchangeRateResponse",
    {"from": str, "to": str, "rate": float, "isStale": NotRequired[bool]},
)

ConvertCurrencyResponse = TypedDict(
    "ConvertCurrencyResponse",
    {
        "from": str,
        "to": str,
        "amount": float,
        "convertedAmount": float,
        "rate": float,
    },
)


class PaginatedMeta(TypedDict):
    total: int
    page: int
    limit: int
    totalPages: int


class ListDeliveriesResponse(TypedDict):
    data: list[DeliveryDetail]
    meta: PaginatedMeta


class WebhookEnvelope(TypedDict):
    event: WebhookEventName
    data: dict[str, object]
