[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
# Ethereum Seed Phrase Balance Checker & Generator

A Python script that **generates random Ethereum seed phrases**, derives multiple addresses from each, and checks their balances by connecting to an Ethereum node. Any seed phrases with addresses holding ETH are saved to a file for review.

---

## Features

- Generates random 12-word BIP39 seed phrases (like MetaMask uses).  
- Derives up to 30 Ethereum addresses per seed using BIP44 standard.  
- Checks the ETH balance of each address via a local or remote Ethereum node.  
- Supports multithreaded checking to increase throughput.  
- Logs any found wallets with ETH balance to a text file (`found_wallets.txt`).  
- Prints status updates every 100 seeds checked.

---

## Requirements

- Python 3.7+  
- [web3.py](https://github.com/ethereum/web3.py)  
- [mnemonic](https://github.com/trezor/python-mnemonic)  
- [bip-utils](https://github.com/ebellocchia/bip_utils)  
- **An Ethereum node running and synced, such as [Geth (Go Ethereum)](https://geth.ethereum.org/)**

Install Python dependencies via pip:

```bash
pip install web3 mnemonic bip-utils
```
## Installation

Clone the repository:

```bash
git clone https://github.com/Red60sapphire/CryptoCracka
cd CryptoCracka
```

- **Run the `install.bat` file to set up everything!** 🚀

## Setting Up Geth (Ethereum Node)
To run a local Ethereum node, download and install Geth.

Start Geth with the HTTP RPC server enabled:

```bash
geth --http --http.addr 127.0.0.1 --http.port 8545 --http.api eth,net,web3
```
Make sure your node is fully synced to the latest Ethereum block to get accurate balances.

## Configuration

Configure the following variables at the top of `checker.py`:

| Variable               | Description                                | Default                     |
|------------------------|--------------------------------------------|-----------------------------|
| `RPC_URL`              | Ethereum node HTTP RPC endpoint            | `http://127.0.0.1:8545`     |
| `MAX_ADDRESSES_PER_SEED` | Number of addresses derived per seed phrase | `30`                        |
| `MAX_WORKERS`          | Number of concurrent threads               | `50`                        |
| `MAX_PENDING`          | Max number of active seed-check tasks      | `1000`                      |
| `OUTPUT_FILE`          | File to save found wallets                  | `found_wallets.txt`         |

---

## Usage

Run the script from your terminal or command line:

```bash
python checker.py
```

## Notes & Disclaimer
Extremely low probability: The chance of randomly finding a seed phrase with ETH is astronomically low.

For educational and research purposes only.

Requires access to an Ethereum node (local or remote).

Ensure your node is fully synced and reachable via the configured RPC_URL.

