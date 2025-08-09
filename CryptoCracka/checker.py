import asyncio
import secrets
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import aiohttp

RPC_URL = "http://127.0.0.1:8545"
OUTPUT_FILE = "found_wallets.txt"
MAX_ADDRESSES_PER_SEED = 30
BATCH_SIZE = 100  # seeds per batch
DISPLAY_DELAY = 0.1  # seconds between printing lines

mnemo = Mnemonic("english")

def generate_seed_phrase():
    entropy = secrets.token_bytes(16)
    return mnemo.to_mnemonic(entropy)

def derive_eth_address_from_seed(seed_phrase, account_index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    addr_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(account_index)
    return addr_ctx.PublicKey().ToAddress()

async def check_seed(session, seed_phrase):
    addresses = [derive_eth_address_from_seed(seed_phrase, i) for i in range(MAX_ADDRESSES_PER_SEED)]
    batch_request = [
        {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [addr, "latest"], "id": idx}
        for idx, addr in enumerate(addresses)
    ]

    try:
        async with session.post(RPC_URL, json=batch_request) as resp:
            results = await resp.json()
    except Exception as e:
        return f"RPC error: {e}"

    for idx, result in enumerate(results):
        if "result" in result:
            balance_wei = int(result["result"], 16)
            if balance_wei > 0:
                balance_eth = balance_wei / 1e18
                with open(OUTPUT_FILE, "a") as f:
                    f.write(f"Seed: {seed_phrase} | Address[{idx}]: {addresses[idx]} | Balance: {balance_eth} ETH\n")
                return f"[FOUND FUNDS] {seed_phrase} ({balance_eth} ETH)"
    return f"{seed_phrase} - NO FUNDS"

async def main():
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        count = 0
        while True:
            tasks = [check_seed(session, generate_seed_phrase()) for _ in range(BATCH_SIZE)]
            results = await asyncio.gather(*tasks)
            count += BATCH_SIZE

            for line in results:
                if line:
                    print(line)
                    await asyncio.sleep(DISPLAY_DELAY)  # Slow down output

            if count % 100 == 0:
                print(f"--- Checked {count} seeds so far ---")

            await asyncio.sleep(0.05)  # small pause between batches

if __name__ == "__main__":
    asyncio.run(main())
