import streamlit as st
from src.detector import detect_address
from src.risk import assess_risk

st.set_page_config(
    page_title="Crypto Network Guard",
    page_icon="🧭",
    layout="centered"
)

# ---------------- HEADER ---------------- #

st.title("🧭 Crypto Network Guard")
st.caption(
    "Decision-support prototype: detect address format and reduce the risk of choosing the wrong network."
)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:
    st.header("Settings")

    recipient_type = st.radio(
        "Recipient type",
        ["Personal wallet", "Exchange"],
        index=0,
        help=(
            "Personal wallet = user controls the private key.\n\n"
            "Exchange = custodial address. Wrong network may require support and may fail."
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
        "We detect the ADDRESS FORMAT (Bitcoin / Tron / EVM / Solana).\n\n"
        "We do NOT check balances or on-chain data."
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

# ---------------- EDUCATIONAL BLOCK ---------------- #

st.markdown("---")

with st.expander("📘 What does this tool actually check?"):
    st.write(
        "This prototype detects address FORMAT only.\n\n"
        "- 0x... → EVM-style (shared across Ethereum, BSC, Polygon, Arbitrum, etc.)\n"
        "- T... → TRON\n"
        "- 1..., 3..., bc1... → Bitcoin\n"
        "- Base58 32–44 chars → Solana-like\n\n"
        "It does not query the blockchain or verify balances."
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