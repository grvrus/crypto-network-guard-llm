import streamlit as st

st.set_page_config(page_title="How it works", page_icon="📘", layout="centered")

st.title("📘 How it works")
st.caption("Why the same address format can map to multiple networks and how to reduce mistakes.")

st.header("1) We detect the address *format*, not the token")
st.write(
    "The prototype checks the **format** of the destination address and proposes compatible network(s). "
    "It does not verify balances or check on-chain data."
)

st.header("2) Address formats we detect")
with st.expander("Bitcoin"):
    st.write("- Starts with **bc1** (Bech32) or **1** / **3** (legacy formats).")
    st.write("- If you pick a non-Bitcoin network, it's almost certainly wrong.")

with st.expander("TRON (TRC-20)"):
    st.write("- Typically starts with **T** and is Base58-like.")
    st.write("- If you pick Ethereum/BSC/etc. for a TRON address, you'll likely get an invalid-address error.")

with st.expander("EVM networks (Ethereum / BSC / Polygon / Arbitrum / Optimism / Base / Avalanche C-Chain...)"):
    st.write("- Addresses start with **0x** + 40 hex characters.")
    st.write(
        "- **Important:** the address alone cannot tell which chain is correct, because many networks share the same format."
    )

with st.expander("Solana"):
    st.write("- Base58-like public keys, usually **32–44** characters.")
    st.write("- If you pick a non-Solana network, it's likely wrong.")

st.header("3) Why do 0x addresses cause confusion?")
st.write(
    "Many chains are **EVM-compatible** and reuse Ethereum’s address system. "
    "That means the same private key produces the same 0x address across many networks. "
    "Balances are separate per network, so sending via the wrong chain can make funds 'invisible' to the recipient."
)

st.header("4) Why 'Exchange' is riskier than 'Personal wallet'")
st.write(
    "- **Personal wallet (non-custodial):** the recipient usually controls the private key and can switch networks.\n"
    "- **Exchange (custodial):** the user does not control the deposit address key; recovery may require support and may fail."
)

st.header("5) Safety checklist")
st.write("Before sending:")
st.write("- Confirm the **network shown by the recipient** (especially for 0x addresses).")
st.write("- Consider a **small test transfer** first.")
st.write("- Make sure you have gas on the chosen network (ETH/BNB/MATIC/etc.).")

st.info("This page is educational content for the prototype demo.")