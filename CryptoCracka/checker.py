import secrets
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from web3 import Web3
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes


RPC_URL = "http://127.0.0.1:8545"  # Change if needed
OUTPUT_FILE = "found_wallets.txt"
MAX_ADDRESSES_PER_SEED = 30
MAX_WORKERS = 50        # Number of threads
MAX_PENDING = 1000      # Max active concurrent tasks


mnemo = Mnemonic("english")


def generate_seed_phrase():
    entropy = secrets.token_bytes(16)  # 128 bits entropy = 12 words
    return mnemo.to_mnemonic(entropy)


def derive_eth_address_from_seed(seed_phrase, account_index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(account_index)
    return bip44_acc_ctx.PublicKey().ToAddress()


def check_balance(w3, address):
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print(f"Error checking {address}: {e}")
        return 0


def check_seed(w3, seed_phrase):
    try:
        found_funds = False
        for idx in range(MAX_ADDRESSES_PER_SEED):
            address = derive_eth_address_from_seed(seed_phrase, idx)
            balance = check_balance(w3, address)
            if balance > 0:
                found_funds = True
                with open(OUTPUT_FILE, "a") as f:
                    f.write(f"Seed: {seed_phrase} | Address[{idx}]: {address} | Balance: {balance} ETH\n")
                print(f"[FOUND FUNDS] Seed: {seed_phrase} | Address[{idx}]: {address} | Balance: {balance} ETH")
                # Optional: continue checking or break if you only want first found
                # break
        if not found_funds:
            print(f"{seed_phrase} - NO FUNDS")
        return found_funds
    except Exception as e:
        print(f"Error in check_seed for {seed_phrase[:20]}...: {e}")
        return False


def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Failed to connect to Ethereum node.")
        return
    print("Connected to Ethereum node")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = set()
        count = 0
        while True:
            # Wait if too many active tasks
            if len(futures) >= MAX_PENDING:
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                futures -= done

            # Submit new seed check task
            seed = generate_seed_phrase()
            future = executor.submit(check_seed, w3, seed)
            futures.add(future)
            count += 1

            if count % 100 == 0:
                print(f"Checked {count} seeds... Active tasks: {len(futures)}")


if __name__ == "__main__":
    main()
