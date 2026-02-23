from dataclasses import dataclass
from typing import List


@dataclass
class RiskResult:
    level: str  # "low", "medium", "high"
    reasons: List[str]
    recommended_action: str


def assess_risk(det, chosen_network: str, recipient_type: str) -> RiskResult:

    if not chosen_network:
        return RiskResult(
            level="medium",
            reasons=["No network selected yet."],
            recommended_action="Select the network you plan to use."
        )

    reasons = []

    # -------- FORMAT MISMATCH = HIGH -------- #

    if det.kind == "bitcoin" and chosen_network != "Bitcoin":
        return RiskResult(
            level="high",
            reasons=["Bitcoin address used with non-Bitcoin network."],
            recommended_action="Select Bitcoin network."
        )

    if det.kind == "tron" and chosen_network != "TRON (TRC-20)":
        return RiskResult(
            level="high",
            reasons=["TRON address used with non-TRON network."],
            recommended_action="Select TRON (TRC-20) network."
        )

    if det.kind == "solana" and chosen_network != "Solana":
        return RiskResult(
            level="high",
            reasons=["Solana address used with non-Solana network."],
            recommended_action="Select Solana network."
        )

    # EVM case
    if det.kind == "evm":

        # If user selected Bitcoin or Solana or Tron → HIGH
        if chosen_network in ["Bitcoin", "Solana", "TRON (TRC-20)"]:
            return RiskResult(
                level="high",
                reasons=[
                    "EVM (0x...) address cannot receive funds via this network."
                ],
                recommended_action="Select a compatible EVM network."
            )

        # Compatible EVM network
        if recipient_type == "Exchange":
            return RiskResult(
                level="high",
                reasons=[
                    "EVM address detected (0x...).",
                    "Exchanges are custodial.",
                    "Wrong network may require manual recovery or may fail."
                ],
                recommended_action="Verify the deposit network shown by the exchange."
            )
        else:
            return RiskResult(
                level="medium",
                reasons=[
                    "EVM address detected (0x...).",
                    "This format is shared across multiple EVM networks.",
                    "Correct chain depends on what the recipient expects."
                ],
                recommended_action="Confirm the expected network with the recipient."
            )

    # -------- PERFECT MATCH -------- #

    return RiskResult(
        level="low",
        reasons=["Address format matches selected network."],
        recommended_action="Proceed carefully and consider a small test transfer."
    )