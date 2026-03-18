import streamlit as st
import pandas as pd

from src.detector import detect_address
from src.risk import assess_risk
from src.advisor import get_ai_recommendation
from src.bestchange_api import (
    SUPPORTED_USDT_NETWORKS,
    resolve_scope,
    get_source_currency_options,
    get_offers_for_pair,
)

st.set_page_config(
    page_title="Crypto Network Guard",
    page_icon="🧭",
    layout="centered"
)

st.markdown(
    """
    <style>
    .ai-card {
        border: 1px solid #e6e6e6;
        border-radius: 16px;
        padding: 20px 20px 16px 20px;
        background: #fafafa;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .ai-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .ai-text {
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 12px;
    }
    .ai-pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 10px;
        background: #eef2ff;
    }
    .soft-box {
        border: 1px solid #e8e8e8;
        border-radius: 14px;
        padding: 14px;
        background: #fcfcfc;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- HEADER ---------------- #

st.title("🧭 Crypto Network Guard")
st.caption(
    "Decision-support prototype: detect address format, assess transfer risk, generate an LLM explanation, and show BestChange offers for supported BTC/USDT scenarios."
)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:
    st.header("Settings")

    recipient_type = st.radio(
        "Recipient type",
        ["Personal wallet", "Exchange"],
        index=0,
        help=(
            "Personal wallet = the recipient controls the private key.\n\n"
            "Exchange = custodial deposit address. Wrong network selection may require support and may fail."
        ),
    )

    st.markdown("---")

    st.info(
        "⚠ For 0x addresses, the correct chain cannot be inferred from the address alone."
    )

# ---------------- ADDRESS INPUT ---------------- #

st.subheader("1️⃣ Paste destination address")

address = st.text_input(
    "Address",
    placeholder="e.g., 0x..., T..., bc1..., 1..., 3...",
    help=(
        "The app detects ADDRESS FORMAT only (Bitcoin / Tron / EVM / Solana / BEP-2).\n\n"
        "It does not verify balances or query on-chain data."
    ),
)

if not address.strip():
    st.info("Paste an address to start.")
    st.stop()

# ---------------- DETECTION ---------------- #

det = detect_address(address)

st.subheader("2️⃣ Address detection")

if det.kind == "unknown":
    st.error(det.note or "Unknown address format.")
    st.stop()
else:
    st.success(det.note or "Address format detected.")
    st.write("**Compatible network(s):**")
    st.write(", ".join(det.likely_networks))

# ---------------- NETWORK SELECTION ---------------- #

st.subheader("3️⃣ Select sending network")

network_options = [
    "",
    "Ethereum (ERC-20)",
    "BNB Smart Chain (BEP-20)",
    "TRON (TRC-20)",
    "Polygon",
    "Arbitrum",
    "Optimism",
    "Base",
    "Avalanche C-Chain",
    "Solana",
    "Bitcoin",
    "BNB Beacon Chain (BEP-2)",
]

chosen_network = st.selectbox(
    "Network you plan to use",
    network_options,
    index=0,
    help=(
        "Choose the blockchain network you will use to send funds.\n\n"
        "For EVM (0x...) addresses, the format alone does not determine the correct chain."
    ),
)

# ---------------- RISK ANALYSIS ---------------- #

risk = assess_risk(det, chosen_network, recipient_type)

st.subheader("4️⃣ Risk assessment")

if risk.level == "low":
    st.success("🟢 LOW RISK")
elif risk.level == "medium":
    st.warning("🟡 MEDIUM RISK")
else:
    st.error("🔴 HIGH RISK")

with st.expander("Why?"):
    for r in risk.reasons:
        st.write(f"- {r}")

st.info(risk.recommended_action)

# ---------------- AI ASSISTANT ---------------- #

st.subheader("5️⃣ AI assistant recommendation")

purpose = None
inferred_token = ""
token_supported = False

if not chosen_network:
    st.info("Select a sending network to unlock the AI assistant.")
else:
    scope = resolve_scope(chosen_network)

    if scope["supported"] and scope["token"] == "BTC":
        inferred_token = "BTC"
        token_supported = True
    elif scope["supported"] and scope["token"] == "USDT":
        inferred_token = "USDT"
        token_supported = True
    else:
        inferred_token = "Unsupported for token recommendation"
        token_supported = False

    if token_supported:
        st.markdown(
            f"""
            <div class="soft-box">
                <b>Prototype token interpretation:</b> {inferred_token}<br>
                <span style="font-size:0.95rem;">
                This is a prototype rule, not real token detection from the address.
                The app only generates token-level recommendations for:
                <b>BTC on Bitcoin network</b> and <b>USDT on selected supported transfer networks</b>.
                Networks such as Solana or BEP-2 are ignored for token recommendation purposes.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="soft-box">
                <b>Prototype token interpretation:</b> Not supported<br>
                <span style="font-size:0.95rem;">
                This prototype only provides token-level recommendations for <b>BTC</b> and <b>USDT</b>.
                Since the selected network is <b>{chosen_network}</b>, the AI assistant will not produce a token recommendation.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    purpose = st.selectbox(
        "Select transfer goal",
        ["Investing", "Transfer", "Savings"],
        index=1,
        help="This does not change the risk score. It changes how the LLM explains the scenario and how BestChange offers are sorted.",
    )

    generate_clicked = st.button("Generate AI recommendation", use_container_width=True)

    if generate_clicked:
        context = {
            "inferred_token": inferred_token,
            "token_supported": token_supported,
            "purpose": purpose,
            "chosen_network": chosen_network,
            "recipient_type": recipient_type,
            "address_kind": det.kind,
            "compatible_networks": det.likely_networks,
            "risk_level": risk.level,
            "risk_reasons": risk.reasons,
            "recommended_action_from_risk_module": risk.recommended_action,
        }

        with st.spinner("Generating recommendation..."):
            ai = get_ai_recommendation(context)

        headline = ai.get("headline", "").strip()
        message = ai.get("message", "").strip()
        warning = ai.get("warning", "").strip()
        suggested_action = ai.get("suggested_action", "").strip()

        badge_text = inferred_token if token_supported else "No token recommendation"

        st.markdown(
            f"""
            <div class="ai-card">
                <div class="ai-pill">Recommendation scope: {badge_text}</div>
                <div class="ai-pill">Goal: {purpose}</div>
                <div class="ai-pill">Network: {chosen_network}</div>
                <div class="ai-title">{headline or "AI recommendation"}</div>
                <div class="ai-text">{message or "No AI recommendation available."}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if warning:
            st.warning(warning)

        if suggested_action:
            st.info(suggested_action)
    else:
        st.info("Choose a goal and click the button to generate the LLM recommendation.")

# ---------------- BESTCHANGE OFFERS ---------------- #

st.subheader("6️⃣ BestChange market offers")

if not chosen_network:
    st.info("Select a network first to unlock BestChange offers.")
else:
    scope = resolve_scope(chosen_network)

    if not scope["supported"]:
        st.info(
            "BestChange suggestions are only shown for BTC on Bitcoin and USDT on the supported transfer networks."
        )
    elif purpose is None:
        st.info("Select a transfer goal above first.")
    else:
        st.markdown(
            f"""
            <div class="soft-box">
                <b>Offer scope:</b> {scope["token"]} on {chosen_network}<br>
                <span style="font-size:0.95rem;">
                Sorting rule in this prototype:
                <b>Transfer → descending rankrate</b>,
                <b>Savings / Investing → ascending rankrate</b>.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            source_data = get_source_currency_options(chosen_network)

            if not source_data["supported"] or not source_data["source_options"]:
                st.warning(
                    "Could not load available purchase directions for this target currency from BestChange."
                )
            else:
                source_options = source_data["source_options"]
                source_labels = [option["label"] for option in source_options]

                default_index = 0
                prev_label = st.session_state.get("selected_source_label")
                if prev_label in source_labels:
                    default_index = source_labels.index(prev_label)

                selected_label = st.selectbox(
                    "Buy with",
                    source_labels,
                    index=default_index,
                    key="selected_source_label",
                    help="This is the source currency used to obtain the prototype-selected BTC/USDT target.",
                )

                selected_source = next(
                    option for option in source_options if option["label"] == selected_label
                )

                load_offers_clicked = st.button("Load BestChange offers", use_container_width=True)

                if load_offers_clicked:
                    with st.spinner("Loading BestChange offers..."):
                        offers = get_offers_for_pair(
                            from_currency_id=selected_source["id"],
                            to_currency_id=source_data["target_currency"]["id"],
                            goal=purpose,
                            lang="en",
                            top_n=10,
                        )

                    if not offers:
                        st.warning("No offers found for the selected direction.")
                    else:
                        offers_df = pd.DataFrame(
                            [
                                {
                                    "Changer": offer["changer_name"],
                                    "Rank rate": offer["rankrate"],
                                    "Rate": offer["rate"],
                                    "Reserve": offer["reserve"],
                                    "Min": offer["inmin"],
                                    "Max": offer["inmax"],
                                    "Rating": offer["rating"],
                                    "Positive reviews": offer["reviews_positive"],
                                    "Active": "Yes" if offer["active"] else "No",
                                    "Marks": ", ".join(offer["marks"]) if offer["marks"] else "",
                                    "Open": offer["changer_url"],
                                }
                                for offer in offers
                            ]
                        )

                        st.dataframe(
                            offers_df,
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.caption(
                            "BestChange offers are sorted using the prototype's custom goal-based rule, not necessarily the monitor's native UI ordering."
                        )
                else:
                    st.info("Choose the source currency and click the button to load offers.")
        except Exception as e:
            st.error(f"BestChange API error: {e}")

# ---------------- EDUCATIONAL BLOCK ---------------- #

st.markdown("---")

with st.expander("📘 What does this tool actually check?"):
    st.write(
        "This prototype detects address FORMAT only.\n\n"
        "- 0x... → EVM-style (shared across Ethereum, BSC, Polygon, Arbitrum, Base, etc.)\n"
        "- T... → TRON\n"
        "- 1..., 3..., bc1... → Bitcoin\n"
        "- bnb... → BNB Beacon Chain (BEP-2)\n"
        "- Base58 32–44 chars → Solana-like\n\n"
        "It does not query the blockchain, verify token balances, or check whether a specific exchange supports a deposit."
    )

with st.expander("📘 How does the AI block work now?"):
    st.write(
        "The AI block only produces token-level recommendations for two prototype cases:\n"
        "- BTC on Bitcoin network\n"
        "- USDT on selected supported transfer networks\n\n"
        "All other ecosystems, such as Solana or BEP-2, are ignored for token recommendation purposes. "
        "In those cases, the system can still explain transfer risk, but it will not pretend to infer a supported token recommendation."
    )

with st.expander("📘 How does the BestChange block work?"):
    st.write(
        "The BestChange block uses the official BestChange API v2.\n\n"
        "It first resolves the target recommendation scope (BTC or USDT), then loads all available source currencies "
        "that can be exchanged into that target. After the user chooses the source currency, it loads the exchanger list "
        "for that pair and sorts it with a custom prototype rule:\n"
        "- Transfer → descending rankrate\n"
        "- Savings / Investing → ascending rankrate"
    )

st.page_link(
    "pages/2_How_it_works.py",
    label="📘 Learn more: How networks & addresses work",
    icon="📘",
)

st.markdown("---")
st.caption(
    "Educational prototype. Always verify the deposit network shown by the recipient platform before sending funds."
)