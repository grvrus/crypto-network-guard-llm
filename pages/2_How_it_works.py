import streamlit as st

st.set_page_config(page_title="How it works", page_icon="📘", layout="centered")

st.title("📘 How it works")
st.caption(
    "Why address formats can be confusing, how the prototype estimates transfer risk, and how the AI + BestChange layers work."
)

st.header("1) We detect the address *format*, not the token")
st.write(
    "The prototype checks the **format** of the destination address and proposes compatible network(s). "
    "It does **not** detect the exact token being transferred, verify balances, or query live blockchain data."
)
st.write(
    "This distinction is important: one address can often receive multiple tokens, especially on EVM-compatible networks. "
    "So the prototype is mainly a **network-safety** and **decision-support** tool."
)

st.header("2) Address formats we detect")

with st.expander("Bitcoin"):
    st.write("- Starts with **bc1** (Bech32) or **1** / **3** (legacy formats).")
    st.write("- If you choose a non-Bitcoin network for a Bitcoin address, the transfer is very likely incorrect.")
    st.write("- In this prototype, Bitcoin is the only network that can trigger a **BTC-oriented recommendation scope**.")

with st.expander("TRON (TRC-20)"):
    st.write("- Typically starts with **T** and is Base58-like.")
    st.write("- If you choose Ethereum, Solana, Bitcoin, or another incompatible network, the address-network combination is likely invalid.")
    st.write("- TRON can still fall into a supported **USDT-oriented recommendation scope**, but that is a prototype rule, not token detection.")

with st.expander("EVM networks (Ethereum / BSC / Polygon / Arbitrum / Optimism / Base / Avalanche C-Chain...)"):
    st.write("- Addresses start with **0x** + 40 hex characters.")
    st.write(
        "- **Important:** the address alone cannot tell which chain is correct, because many EVM-compatible networks reuse the same address format."
    )
    st.write(
        "- This is why EVM addresses often produce **medium risk** rather than low risk: the format may be valid, but the exact expected chain is still ambiguous."
    )

with st.expander("Solana"):
    st.write("- Solana public keys are Base58-like, usually **32–44** characters.")
    st.write("- If you choose a non-Solana network, the risk is high.")
    st.write("- In this prototype, Solana is detected and checked for transfer safety, but it is **not included in the BTC/USDT recommendation scope**.")

with st.expander("BNB Beacon Chain (BEP-2)"):
    st.write("- BEP-2 addresses usually start with **bnb**.")
    st.write("- This is a specific legacy Binance-chain style format.")
    st.write("- In this prototype, it is checked for compatibility, but it is **not included in the BTC/USDT recommendation scope**.")

st.header("3) Why do 0x addresses cause confusion?")
st.write(
    "Many chains are **EVM-compatible** and reuse Ethereum’s address system. "
    "That means the same private key can generate the same **0x** address across multiple networks."
)
st.write(
    "However, balances still exist **separately per chain**. "
    "So sending funds on the wrong EVM network can make them appear missing or unsupported from the recipient's point of view."
)
st.write(
    "This is why the prototype separates two questions:\n"
    "- Is the address format technically compatible?\n"
    "- Is the selected network actually the one the recipient expects?"
)

st.header("4) Why 'Exchange' is riskier than 'Personal wallet'")
st.write(
    "- **Personal wallet (non-custodial):** the recipient usually controls the private key and may be able to switch networks or recover access more flexibly.\n"
    "- **Exchange (custodial):** the user does not control the deposit address key; a wrong network may require support intervention and recovery may fail."
)
st.write(
    "Because of that, the same address/network combination may be explained more cautiously when the recipient type is **Exchange**."
)

st.header("5) How the risk block works")
st.write(
    "The risk block is rule-based. It compares:\n"
    "- detected address kind\n"
    "- selected sending network\n"
    "- recipient type"
)

with st.expander("Low risk examples"):
    st.write("- Bitcoin address + Bitcoin network")
    st.write("- TRON address + TRON network")
    st.write("- Solana address + Solana network")
    st.write("- EVM address + valid EVM network in a less risky context")

with st.expander("Medium risk examples"):
    st.write("- EVM address + Ethereum / BSC / Polygon / Arbitrum / Base + personal wallet")
    st.write("- The format is compatible, but the exact expected chain may still be uncertain.")

with st.expander("High risk examples"):
    st.write("- Bitcoin address + Ethereum")
    st.write("- TRON address + Bitcoin")
    st.write("- Solana address + TRON")
    st.write("- EVM address + Bitcoin or Solana")
    st.write("- EVM address + exchange context with stronger ambiguity concerns")

st.header("6) What the AI block actually does")
st.write(
    "The AI block does **not** replace the risk model. "
    "Instead, it receives the structured result from the rule-based modules and turns it into a more readable explanation."
)
st.write(
    "The LLM receives context such as:\n"
    "- recommendation scope\n"
    "- selected goal\n"
    "- chosen network\n"
    "- recipient type\n"
    "- detected address kind\n"
    "- risk level\n"
    "- risk reasons\n"
    "- recommended action"
)

st.write(
    "Then it returns a structured answer with:\n"
    "- a headline\n"
    "- a message\n"
    "- a warning\n"
    "- a suggested next step"
)

st.header("7) What is the recommendation scope?")
st.write(
    "The prototype only supports **token-level recommendation logic** for two controlled cases:"
)

with st.expander("BTC-supported scope"):
    st.write("- Triggered when the selected network is **Bitcoin**.")
    st.write("- This is the only case where the prototype allows an **investment-oriented explanation**.")
    st.write(
        "- The internal logic is: Bitcoin is treated as the main investment-oriented crypto asset in this prototype "
        "because it has the largest market capitalization and often leads the broader market."
    )

with st.expander("USDT-supported scope"):
    st.write("- Triggered for selected supported transfer networks such as:")
    st.write("  - Ethereum (ERC-20)")
    st.write("  - BNB Smart Chain (BEP-20)")
    st.write("  - TRON (TRC-20)")
    st.write("  - Polygon")
    st.write("  - Arbitrum")
    st.write("  - Optimism")
    st.write("  - Base")
    st.write("  - Avalanche C-Chain")
    st.write(
        "- In this prototype, those cases are interpreted as **USDT-oriented transfer or utility scenarios**, "
        "not as investment recommendations."
    )

with st.expander("Unsupported scope"):
    st.write("- Solana")
    st.write("- BNB Beacon Chain (BEP-2)")
    st.write("- other unsupported ecosystems")
    st.write(
        "- In those cases, the prototype still evaluates transfer safety, but it **does not pretend to infer a supported BTC/USDT recommendation**."
    )

st.header("8) What do the goal options mean?")
st.write(
    "The goal selector in the AI block does **not** change technical risk. "
    "It only changes how the app explains the scenario."
)

with st.expander("Investing"):
    st.write("- Used when the user frames the transfer as an investment-related action.")
    st.write("- Example: sending BTC to a long-term wallet.")
    st.write("- This aligns best with the BTC-supported scope.")

with st.expander("Transfer"):
    st.write("- Used for a normal transfer use case.")
    st.write("- Example: sending funds to another wallet or to an exchange.")
    st.write("- The explanation focuses on practical network compatibility.")

with st.expander("Savings"):
    st.write("- Used for storing value rather than actively investing or simply moving funds.")
    st.write("- Example: parking stable value or moving assets to a storage wallet.")
    st.write("- In the prototype, this changes the wording of the explanation and the BestChange sorting behavior.")

st.header("9) How the BestChange block works")
st.write(
    "The prototype also integrates the official **BestChange API v2** for supported recommendation scopes."
)
st.write(
    "The BestChange flow is:\n"
    "1. Resolve whether the selected network belongs to BTC scope or USDT scope.\n"
    "2. Find the corresponding target currency in the BestChange API.\n"
    "3. Load possible source currencies that can be exchanged into that target.\n"
    "4. Let the user choose which source currency they want to buy with.\n"
    "5. Load exchanger offers for that pair.\n"
    "6. Sort the offers according to the selected goal."
)

with st.expander("BestChange sorting rule in this prototype"):
    st.write("- **Transfer** → sort by **descending rankrate**")
    st.write("- **Savings / Investing** → sort by **ascending rankrate**")
    st.write(
        "- This is a custom prototype rule used for decision support. "
        "It is not necessarily identical to the native ordering of the BestChange website interface."
    )

st.header("10) Safety checklist")
st.write("Before sending:")
st.write("- Confirm the **exact network shown by the recipient**.")
st.write("- For EVM-style addresses, do not assume that 0x means Ethereum only.")
st.write("- If sending to an exchange, verify deposit instructions carefully.")
st.write("- Consider a **small test transfer** first.")
st.write("- Make sure you have gas on the chosen network (ETH / BNB / MATIC / TRX / etc.).")

st.info(
    "This page is educational content for the prototype demo. "
    "The prototype helps interpret transfer scenarios, but it does not replace manual verification by the user."
)