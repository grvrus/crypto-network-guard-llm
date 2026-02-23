import re
from dataclasses import dataclass
from typing import List, Optional

# -------- Common alphabets --------
# Base58 alphabet excludes: 0, O, I, l
BASE58_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")

# -------- Address format patterns --------
EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")               # EVM (Ethereum-style)
BTC_BECH32_RE = re.compile(r"^(bc1)[0-9a-z]{11,71}$", re.IGNORECASE)
BTC_LEGACY_RE = re.compile(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$")

# BEP-2 (old Binance Chain) typical prefix
BEP2_RE = re.compile(r"^bnb[0-9a-z]{10,}$", re.IGNORECASE)

# Solana addresses are base58, usually 32–44 chars (public key)
SOLANA_LEN_MIN, SOLANA_LEN_MAX = 32, 44

# Tron addresses are Base58Check, commonly 34 chars and start with "T"
# In a prototype, be slightly tolerant in length.
TRON_LEN_MIN, TRON_LEN_MAX = 33, 36


@dataclass
class DetectionResult:
    address: str
    kind: str  # "tron", "bitcoin", "evm", "solana", "bep2", "unknown"
    likely_networks: List[str]
    is_ambiguous: bool
    note: Optional[str] = None


EVM_NETWORKS = [
    "Ethereum (ERC-20)",
    "BNB Smart Chain (BEP-20)",
    "Polygon",
    "Arbitrum",
    "Optimism",
    "Base",
    "Avalanche C-Chain",
]


def _is_base58(s: str) -> bool:
    return bool(BASE58_RE.match(s))


def detect_address(address_raw: str) -> DetectionResult:
    address = address_raw.strip()

    if not address:
        return DetectionResult(address="", kind="unknown", likely_networks=[], is_ambiguous=True)

    a = address  # alias

    # 1) Bitcoin: very recognizable prefixes
    if BTC_BECH32_RE.match(a) or BTC_LEGACY_RE.match(a):
        return DetectionResult(
            address=a,
            kind="bitcoin",
            likely_networks=["Bitcoin"],
            is_ambiguous=False,
            note="Bitcoin address detected (starts with 1, 3, or bc1...).",
        )

    # 2) BEP-2 (old Binance Chain)
    if BEP2_RE.match(a):
        return DetectionResult(
            address=a,
            kind="bep2",
            likely_networks=["BNB Beacon Chain (BEP-2)"],
            is_ambiguous=False,
            note="BEP-2 address detected (starts with bnb...).",
        )

    # 3) EVM: 0x + 40 hex
    if EVM_RE.match(a):
        return DetectionResult(
            address=a,
            kind="evm",
            likely_networks=EVM_NETWORKS,
            is_ambiguous=True,
            note="EVM-style address detected (0x + 40 hex). Exact chain cannot be inferred from the address alone.",
        )

    # 4) TRON: starts with T + base58 chars + length around 34
    # We check TRON *before* generic Solana-like base58 to avoid misclassifying Tron as Solana.
    if a.startswith("T") and _is_base58(a) and (TRON_LEN_MIN <= len(a) <= TRON_LEN_MAX):
        return DetectionResult(
            address=a,
            kind="tron",
            likely_networks=["TRON (TRC-20)"],
            is_ambiguous=False,
            note="TRON address likely detected (starts with T, base58, ~34 chars).",
        )

    # 5) Solana-like: base58 32–44, no special prefix
    if _is_base58(a) and (SOLANA_LEN_MIN <= len(a) <= SOLANA_LEN_MAX):
        return DetectionResult(
            address=a,
            kind="solana",
            likely_networks=["Solana"],
            is_ambiguous=False,
            note="Solana-like base58 address detected (32–44 chars).",
        )

    return DetectionResult(
        address=a,
        kind="unknown",
        likely_networks=[],
        is_ambiguous=True,
        note="Unrecognized address format.",
    )