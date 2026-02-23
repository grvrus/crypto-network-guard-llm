# Crypto Network Guard

Prototype Streamlit application that helps users avoid selecting the wrong blockchain network when sending crypto assets.

## What this project does

When sending tokens (for example USDT), users must choose a blockchain network such as Ethereum, TRON, BNB Smart Chain or Bitcoin.

Some networks share the same address format. In particular, EVM-compatible networks use addresses that start with `0x`.  
Because of this, the address itself does not always indicate which network should be selected.

This application:

- Detects the address format (Bitcoin, TRON, EVM, Solana)
- Shows compatible networks
- Lets the user select a sending network
- Evaluates the risk level (Low / Medium / High)
- Explains why a specific risk level was assigned

The application is rule-based and does not query blockchain data.

---

## Address formats supported

- Bitcoin (addresses starting with 1, 3 or bc1)
- TRON (addresses starting with T)
- EVM-compatible networks (0x + 40 hexadecimal characters)
- Solana-like base58 addresses (32–44 characters)

---

## EVM networks

EVM (Ethereum Virtual Machine) is the execution environment introduced by Ethereum.

Several blockchains reuse this model, including:

- Ethereum
- BNB Smart Chain
- Polygon
- Arbitrum
- Optimism
- Base
- Avalanche C-Chain

These networks share the same 0x address format and cryptographic key structure.  
However, each network has its own blockchain, balances and transaction fees.

The same private key generates the same 0x address across all EVM networks.  
Balances are separate per network.

---

## Custodial vs non-custodial risk

If funds are sent to a personal (non-custodial) wallet, the recipient controls the private key and can usually switch networks if necessary.

If funds are sent to an exchange (custodial address), the user does not control the private key.  
If the wrong network is selected, the exchange may not credit the deposit and recovery may require manual support.

---

## Risk logic

High risk:
- Address format does not match the selected network
- EVM address used with incompatible network
- Sending to exchange with EVM address

Medium risk:
- EVM address with personal wallet (network ambiguity)

Low risk:
- Address format matches the selected network

---

## Project structure

crypto-network-guard/

app.py  
requirements.txt  
README.md  

src/  
&nbsp;&nbsp;&nbsp;&nbsp;__init__.py  
&nbsp;&nbsp;&nbsp;&nbsp;detector.py  
&nbsp;&nbsp;&nbsp;&nbsp;risk.py  

pages/  
&nbsp;&nbsp;&nbsp;&nbsp;2_How_it_works.py  

---

## Run locally

Install dependencies:

pip install -r requirements.txt

Run:

streamlit run app.py

---

## Note

This is an educational prototype.  
Users should always verify the network specified by the recipient before sending funds.