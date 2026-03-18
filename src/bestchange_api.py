import os
from functools import lru_cache
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BESTCHANGE_API_KEY = os.getenv("BESTCHANGE_API_KEY")
BESTCHANGE_BASE_URL = "https://bestchange.app/v2"

SESSION = requests.Session()
SESSION.headers.update(
    {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "CryptoNetworkGuard/1.0",
        "Connection": "keep-alive",
    }
)

SUPPORTED_USDT_NETWORKS = [
    "Ethereum (ERC-20)",
    "BNB Smart Chain (BEP-20)",
    "TRON (TRC-20)",
    "Polygon",
    "Arbitrum",
    "Optimism",
    "Base",
    "Avalanche C-Chain",
]


def _require_api_key() -> str:
    if not BESTCHANGE_API_KEY:
        raise ValueError("BESTCHANGE_API_KEY not found in .env")
    return BESTCHANGE_API_KEY


def _get_json(path: str) -> Dict:
    api_key = _require_api_key()
    url = f"{BESTCHANGE_BASE_URL}/{api_key}{path}"
    response = SESSION.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def _as_text(currency: Dict) -> str:
    return " ".join(
        [
            str(currency.get("name", "")),
            str(currency.get("urlname", "")),
            str(currency.get("viewname", "")),
            str(currency.get("code", "")),
        ]
    ).lower()


@lru_cache(maxsize=4)
def get_currencies(lang: str = "en") -> List[Dict]:
    data = _get_json(f"/currencies/{lang}")
    return data.get("currencies", [])


@lru_cache(maxsize=4)
def get_changers(lang: str = "en") -> List[Dict]:
    data = _get_json(f"/changers/{lang}")
    return data.get("changers", [])


def _find_first_currency(currencies: List[Dict], predicates: List) -> Optional[Dict]:
    for currency in currencies:
        text = _as_text(currency)
        if all(predicate(text, currency) for predicate in predicates):
            return currency
    return None


def resolve_scope(chosen_network: str) -> Optional[Dict]:
    if chosen_network == "Bitcoin":
        return {
            "token": "BTC",
            "network": "Bitcoin",
            "supported": True,
        }

    if chosen_network in SUPPORTED_USDT_NETWORKS:
        return {
            "token": "USDT",
            "network": chosen_network,
            "supported": True,
        }

    return {
        "token": None,
        "network": chosen_network,
        "supported": False,
    }


def resolve_target_currency(chosen_network: str, lang: str = "en") -> Optional[Dict]:
    currencies = get_currencies(lang=lang)
    scope = resolve_scope(chosen_network)

    if not scope or not scope["supported"]:
        return None

    if scope["token"] == "BTC":
        btc = _find_first_currency(
            currencies,
            [
                lambda text, c: c.get("code", "").upper() == "BTC"
                or c.get("viewname", "").upper() == "BTC"
                or "bitcoin" in text
            ],
        )
        return btc

    if scope["token"] == "USDT":
        network_rules = {
            "Ethereum (ERC-20)": ["usdt", "erc20"],
            "BNB Smart Chain (BEP-20)": ["usdt", "bep20"],
            "TRON (TRC-20)": ["usdt", "trc20"],
            "Polygon": ["usdt", "polygon"],
            "Arbitrum": ["usdt", "arbitrum"],
            "Optimism": ["usdt", "optimism"],
            "Base": ["usdt", "base"],
            "Avalanche C-Chain": ["usdt", "avalanche"],
        }

        required_keywords = network_rules.get(chosen_network, [])
        usdt_currency = _find_first_currency(
            currencies,
            [
                lambda text, c: "usdt" in text,
                lambda text, c: all(keyword in text for keyword in required_keywords),
            ],
        )

        return usdt_currency

    return None


def get_source_currency_options(chosen_network: str, lang: str = "en") -> Dict:
    target_currency = resolve_target_currency(chosen_network, lang=lang)

    if target_currency is None:
        return {
            "supported": False,
            "target_currency": None,
            "source_options": [],
            "message": "No supported target currency could be resolved for this network.",
        }

    target_id = target_currency["id"]
    presences_data = _get_json(f"/presences/0-{target_id}")
    presences = presences_data.get("presences", [])
    currencies = get_currencies(lang=lang)

    currency_by_id = {currency["id"]: currency for currency in currencies}
    source_options = []

    for item in presences:
        pair = str(item.get("pair", ""))
        parts = pair.split("-")
        if len(parts) < 2:
            continue

        try:
            from_id = int(parts[0])
            to_id = int(parts[1])
        except ValueError:
            continue

        if to_id != target_id:
            continue

        source_currency = currency_by_id.get(from_id)
        if not source_currency:
            continue

        source_options.append(
            {
                "id": source_currency["id"],
                "label": f'{source_currency.get("viewname", source_currency.get("name", "Unknown"))} ({source_currency.get("code", "")})',
                "name": source_currency.get("name", ""),
                "code": source_currency.get("code", ""),
                "best": item.get("best"),
                "count": item.get("count"),
            }
        )

    source_options = sorted(
        source_options,
        key=lambda x: (-int(x["count"]) if x["count"] is not None else 0, x["label"])
    )

    return {
        "supported": True,
        "target_currency": target_currency,
        "source_options": source_options,
        "message": "",
    }


def _parse_pair_rates(rates_payload: Dict) -> List[Dict]:
    rates_obj = rates_payload.get("rates", {})
    if not rates_obj:
        return []

    first_key = next(iter(rates_obj.keys()), None)
    if first_key is None:
        return []

    return rates_obj.get(first_key, [])


def get_offers_for_pair(
    from_currency_id: int,
    to_currency_id: int,
    goal: str,
    lang: str = "en",
    top_n: int = 10,
) -> List[Dict]:
    rates_payload = _get_json(f"/rates/{from_currency_id}-{to_currency_id}")
    raw_rates = _parse_pair_rates(rates_payload)
    changers = get_changers(lang=lang)
    changer_by_id = {changer["id"]: changer for changer in changers}

    offers = []

    for item in raw_rates:
        changer_id = item.get("changer")
        changer = changer_by_id.get(changer_id, {})

        try:
            rankrate = float(item["rankrate"]) if item.get("rankrate") is not None else None
        except Exception:
            rankrate = None

        try:
            rate = float(item["rate"]) if item.get("rate") is not None else None
        except Exception:
            rate = None

        try:
            reserve = float(item["reserve"]) if item.get("reserve") is not None else None
        except Exception:
            reserve = None

        try:
            inmin = float(item["inmin"]) if item.get("inmin") is not None else None
        except Exception:
            inmin = None

        try:
            inmax = float(item["inmax"]) if item.get("inmax") is not None else None
        except Exception:
            inmax = None

        offers.append(
            {
                "changer_id": changer_id,
                "changer_name": changer.get("name", f"Changer {changer_id}"),
                "changer_url": changer.get("urls", {}).get(lang, ""),
                "changer_page": changer.get("pages", {}).get(lang, ""),
                "active": changer.get("active", False),
                "rating": changer.get("rating"),
                "reviews_positive": changer.get("reviews", {}).get("positive", 0),
                "reviews_neutral": changer.get("reviews", {}).get("neutral", 0),
                "reviews_closed": changer.get("reviews", {}).get("closed", 0),
                "reviews_claim": changer.get("reviews", {}).get("claim", 0),
                "rate": rate,
                "rankrate": rankrate,
                "reserve": reserve,
                "inmin": inmin,
                "inmax": inmax,
                "marks": item.get("marks", []),
            }
        )

    if goal == "Transfer":
        offers = sorted(
            offers,
            key=lambda x: (x["rankrate"] is None, -(x["rankrate"] if x["rankrate"] is not None else 0.0)),
        )
    else:
        offers = sorted(
            offers,
            key=lambda x: (x["rankrate"] is None, x["rankrate"] if x["rankrate"] is not None else float("inf")),
        )

    return offers[:top_n]