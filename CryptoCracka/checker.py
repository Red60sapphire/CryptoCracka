import asyncio
import secrets
from web3 import AsyncHTTPProvider, AsyncWeb3
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import aiofiles

RPC_URL = "http://127.0.0.1:8545"  # Change if needed
OUTPUT_FILE = "found_wallets.txt"
MAX_ADDRESSES_PER_SEED = 30
MAX_CONCURRENT_SEEDS = 100  # concurrency limit

mnemo = Mnemonic("english")

def generate_seed_phrase():
    entropy = secrets.token_bytes(16)  # 128 bits entropy = 12 words
    return mnemo.to_mnemonic(entropy)

def derive_eth_address_from_seed(seed_phrase, account_index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(account_index)
    return bip44_acc_ctx.PublicKey().ToAddress()

async def check_balance(w3, address):
    try:
        balance_wei = await w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print(f"Error checking {address}: {e}")
        return 0

async def check_seed(w3, seed_phrase):
    found_funds = False
    for idx in range(MAX_ADDRESSES_PER_SEED):
        address = derive_eth_address_from_seed(seed_phrase, idx)
        balance = await check_balance(w3, address)
        if balance > 0:
            found_funds = True
            async with aiofiles.open(OUTPUT_FILE, "a") as f:
                await f.write(f"Seed: {seed_phrase} | Address[{idx}]: {address} | Balance: {balance} ETH\n")
            print(f"[FOUND FUNDS] Seed: {seed_phrase} | Address[{idx}]: {address} | Balance: {balance} ETH")
    if not found_funds:
        print(f"{seed_phrase} - NO FUNDS")
    return found_funds

async def main():
    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
    connected = await w3.is_connected()
    if not connected:
        print("Failed to connect to Ethereum node.")
        return
    print("Connected to Ethereum node")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SEEDS)
    count = 0

    async def worker():
        nonlocal count
        async with semaphore:
            seed = generate_seed_phrase()
            await check_seed(w3, seed)
            count += 1
            if count % 100 == 0:
                print(f"Checked {count} seeds...")

    tasks = set()
    while True:
        task = asyncio.create_task(worker())
        tasks.add(task)

        # Clean up done tasks to avoid memory leak
        done, pending = await asyncio.wait(tasks, timeout=0, return_when=asyncio.ALL_COMPLETED)
        tasks = pending

        # If too many tasks, wait for some to complete before adding more
        if len(tasks) >= MAX_CONCURRENT_SEEDS * 2:
            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())
