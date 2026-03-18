import os
import json
import re
import cohere
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in .env")

co = cohere.ClientV2(api_key)


def _extract_json(text: str) -> dict:
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced_match:
        candidate = fenced_match.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace_match:
        candidate = brace_match.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return {
        "headline": "AI response",
        "message": text,
        "warning": "",
        "suggested_action": ""
    }


def get_ai_recommendation(context: dict) -> dict:
    inferred_token = context.get("inferred_token", "")
    token_supported = context.get("token_supported", False)
    purpose = context.get("purpose", "")
    chosen_network = context.get("chosen_network", "")
    risk_level = context.get("risk_level", "")
    recipient_type = context.get("recipient_type", "")
    address_kind = context.get("address_kind", "")
    compatible_networks = context.get("compatible_networks", [])
    risk_reasons = context.get("risk_reasons", [])
    recommended_action = context.get("recommended_action_from_risk_module", "")

    if not token_supported:
        return {
            "headline": "No token recommendation available",
            "message": (
                f"This prototype only provides token-level recommendations for BTC and USDT scenarios. "
                f"The selected network, {chosen_network}, falls outside that recommendation scope. "
                f"For this case, the prototype focuses only on transfer safety: whether the address format matches the selected network, "
                f"whether the scenario is ambiguous, and whether the transfer would be riskier for a personal wallet or an exchange. "
                f"It therefore does not attempt to describe this transfer as an investment or stablecoin-oriented case."
            ),
            "warning": (
                "A missing token recommendation does not mean the transfer is safe. "
                "You should still rely on the risk block above and verify that the recipient expects this exact network."
            ),
            "suggested_action": recommended_action or "Verify network compatibility before sending."
        }

    prompt = f"""
You are an assistant inside a crypto transfer safety prototype.

Your role is to explain the prototype's logic in a detailed, clear, and practical way.
You are not a general financial advisor.
You must explain how THIS PROTOTYPE interprets the scenario.

Context:
{json.dumps({
    "inferred_token": inferred_token,
    "purpose": purpose,
    "chosen_network": chosen_network,
    "recipient_type": recipient_type,
    "address_kind": address_kind,
    "compatible_networks": compatible_networks,
    "risk_level": risk_level,
    "risk_reasons": risk_reasons,
    "recommended_action_from_risk_module": recommended_action
}, indent=2)}

Core prototype rules:
1. This prototype only supports token-level recommendation logic for BTC and USDT.
2. If the selected network is Bitcoin, the prototype interprets the scenario as BTC-oriented.
3. BTC is the only investment-oriented crypto asset in this prototype.
4. The reason is that Bitcoin has the largest market capitalization and often leads broader crypto market trends.
5. If the selected network is one of the supported USDT transfer networks, the prototype interprets the scenario as USDT-oriented.
6. In this prototype, USDT is treated as a fiat-like utility asset mainly for transfer or temporary parking of value.
7. USDT must not be framed as an investment recommendation.
8. The answer must reflect the selected goal:
   - Investing
   - Transfer
   - Savings
9. If risk level is medium or high, explain the risk clearly and strongly.
10. If the address is EVM-like, mention that 0x addresses can be reused across multiple compatible chains.
11. If the recipient type is Exchange, make the warning stricter.
12. Keep the tone educational and moderately detailed.
13. Do not use hype language.
14. Return VALID JSON only.
15. Use exactly these keys:
headline
message
warning
suggested_action

Writing requirements:
- headline: short and specific
- message: 4 to 7 sentences
- warning: 1 to 3 sentences
- suggested_action: 1 to 2 practical sentences

Behavior examples:
- BTC + Investing -> explain that BTC is the prototype's main investment-oriented asset because of market cap and market leadership
- BTC + Transfer -> explain that BTC is still interpreted as investment-oriented in this prototype, even if the user goal is transfer
- USDT + Transfer -> explain that USDT is treated as a transfer-oriented, fiat-like utility asset
- USDT + Investing -> explain clearly that this prototype does not treat USDT as an investment asset

Return only JSON.
"""

    response = co.chat(
        model="command-a-03-2025",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.35
    )

    text = response.message.content[0].text.strip()
    parsed = _extract_json(text)

    return {
        "headline": str(parsed.get("headline", "")).strip(),
        "message": str(parsed.get("message", "")).strip(),
        "warning": str(parsed.get("warning", "")).strip(),
        "suggested_action": str(parsed.get("suggested_action", "")).strip(),
    }