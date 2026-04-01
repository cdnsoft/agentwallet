#!/usr/bin/env python3
"""
log_transaction.py — create, sign, broadcast an EVM transaction and log it to agentwallet.json.

Usage:
    python3 log_transaction.py <amount> <asset> <network> <to> <purpose> \\
        --wallet-key <path>   \\
        --rpc <url>           \\
        [--contract <addr>]   \\
        [--output <path>]     \\
        [--tx-hash <hash>]    \\
        [--decimals <int>]

Arguments:
    amount      numeric amount to send (e.g. 0.02)
    asset       asset symbol (e.g. ETH, USDC)
    network     network name for the log (e.g. Base, Ethereum)
    to          recipient address (0x...)
    purpose     description of the transaction

Options:
    --wallet-key <path>   path to JSON file with "private_key" field
    --rpc <url>           EVM-compatible RPC endpoint
    --contract <addr>     ERC20 contract address (omit for native ETH transfer)
    --output <path>       path to agentwallet.json (required — ask your human if unsure)
    --tx-hash <hash>      skip tx creation and just log an existing hash
    --decimals <int>      ERC20 token decimals (default: 18; USDC = 6)

Examples:
    # Native ETH transfer
    python3 log_transaction.py 0.001 ETH Base 0xRecipient "fund wallet" \\
        --wallet-key ~/.secrets/eth_wallet.json \\
        --rpc https://mainnet.base.org

    # USDC transfer (ERC20, 6 decimals)
    python3 log_transaction.py 0.02 USDC Base 0xRecipient "GateSkip captcha" \\
        --wallet-key ~/.secrets/eth_wallet.json \\
        --rpc https://mainnet.base.org \\
        --contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \\
        --decimals 6

    # Log existing tx without broadcasting
    python3 log_transaction.py 0.02 USDC Base 0xRecipient "manual payment" \\
        --tx-hash 0xabc123... \\
        --output /path/to/agentwallet.json
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from eth_account import Account
from eth_account.signers.local import LocalAccount


# ── ERC20 transfer ABI (minimal) ──────────────────────────────────────────────
ERC20_TRANSFER_ABI = [
    {
        "name": "transfer",
        "type": "function",
        "inputs": [
            {"name": "to",    "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
    }
]


def parse_args(argv):
    args = argv[1:]
    opts = {}

    flags = ["--wallet-key", "--rpc", "--contract", "--output", "--tx-hash", "--decimals"]
    positional = []

    i = 0
    while i < len(args):
        if args[i] in flags:
            if i + 1 >= len(args):
                print(f"Error: {args[i]} requires a value")
                sys.exit(1)
            opts[args[i].lstrip("-").replace("-", "_")] = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if len(positional) < 5:
        print(__doc__)
        sys.exit(1)

    opts["amount"]  = positional[0]
    opts["asset"]   = positional[1]
    opts["network"] = positional[2]
    opts["to"]      = positional[3]
    opts["purpose"] = positional[4]
    return opts


def rpc_call(rpc_url: str, method: str, params: list):
    resp = requests.post(rpc_url, json={
        "jsonrpc": "2.0", "id": 1,
        "method": method, "params": params,
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def get_chain_id(rpc_url: str) -> int:
    return int(rpc_call(rpc_url, "eth_chainId", []), 16)


def get_nonce(rpc_url: str, address: str) -> int:
    return int(rpc_call(rpc_url, "eth_getTransactionCount", [address, "latest"]), 16)


def get_gas_price(rpc_url: str) -> int:
    return int(rpc_call(rpc_url, "eth_gasPrice", []), 16)


def estimate_gas(rpc_url: str, tx: dict) -> int:
    return int(rpc_call(rpc_url, "eth_estimateGas", [tx]), 16)


def send_raw(rpc_url: str, raw_tx: str) -> str:
    return rpc_call(rpc_url, "eth_sendRawTransaction", [raw_tx])


def encode_erc20_transfer(to: str, amount_int: int) -> bytes:
    """Encode ERC20 transfer(address,uint256) calldata manually."""
    # Function selector: keccak256("transfer(address,uint256)")[:4]
    selector = bytes.fromhex("a9059cbb")
    # ABI encode: address (padded to 32 bytes) + uint256 (padded to 32 bytes)
    addr_padded = bytes.fromhex(to[2:].zfill(64))
    amount_padded = amount_int.to_bytes(32, "big")
    return selector + addr_padded + amount_padded





def log_to_wallet(log_path: Path, entry: dict):
    if not log_path.exists():
        log_path.write_text(json.dumps({"transactions": []}, indent=2))
    data = json.loads(log_path.read_text())
    data["transactions"].append(entry)
    log_path.write_text(json.dumps(data, indent=2))
    print(f"✅ Logged to {log_path}")


def main():
    opts = parse_args(sys.argv)

    amount  = opts["amount"]
    asset   = opts["asset"]
    network = opts["network"]
    to      = opts["to"]
    purpose = opts["purpose"]

    if "output" not in opts:
        print("⚠️  --output is required: path to your agentwallet.json log file.")
        print("    If you don't have one yet, ask your human where to store it.")
        print("    Example: --output ~/my-wallet/agentwallet.json")
        sys.exit(1)
    output_path = Path(opts["output"]).expanduser().resolve()

    tx_hash = opts.get("tx_hash")

    # If tx_hash provided, skip broadcasting — just log
    if tx_hash:
        entry = {
            "date":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "amount":  amount,
            "asset":   asset,
            "network": network,
            "to":      to,
            "purpose": purpose,
            "tx_hash": tx_hash,
        }
        log_to_wallet(output_path, entry)
        return

    # Require wallet + rpc for broadcasting
    if "wallet_key" not in opts:
        print("⚠️  --wallet-key is required: path to your wallet JSON file.")
        print("    Ask your human for the path to a wallet JSON with a 'private_key' field.")
        print("    Example: --wallet-key ~/.secrets/eth_wallet.json")
        sys.exit(1)
    if "rpc" not in opts:
        print("⚠️  --rpc is required: an EVM-compatible RPC endpoint URL.")
        print("    Ask your human for an RPC URL for the target network.")
        print("    Example: --rpc https://mainnet.base.org")
        sys.exit(1)

    # Load private key
    key_path = Path(opts["wallet_key"]).expanduser()
    key_data = json.loads(key_path.read_text())
    private_key = key_data.get("private_key") or key_data.get("privateKey")
    if not private_key:
        print(f"Error: no 'private_key' field found in {key_path}")
        sys.exit(1)

    account: LocalAccount = Account.from_key(private_key)
    rpc_url = opts["rpc"]
    decimals = int(opts.get("decimals", 18))
    amount_float = float(amount)
    amount_int = int(amount_float * (10 ** decimals))

    chain_id  = get_chain_id(rpc_url)
    nonce     = get_nonce(rpc_url, account.address)
    gas_price = get_gas_price(rpc_url)

    contract = opts.get("contract")

    if contract:
        # ERC20 transfer
        data = encode_erc20_transfer(to, amount_int)
        tx = {
            "from":     account.address,
            "to":       contract,
            "value":    0,
            "data":     "0x" + data.hex(),
            "nonce":    nonce,
            "chainId":  chain_id,
            "gasPrice": gas_price,
        }
    else:
        # Native ETH transfer (amount in wei, 18 decimals always)
        amount_wei = int(amount_float * 10**18)
        tx = {
            "from":     account.address,
            "to":       to,
            "value":    amount_wei,
            "data":     "0x",
            "nonce":    nonce,
            "chainId":  chain_id,
            "gasPrice": gas_price,
        }

    gas = estimate_gas(rpc_url, {k: hex(v) if isinstance(v, int) else v for k, v in tx.items() if k != "from"})
    tx["gas"] = int(gas * 1.2)  # 20% buffer

    signed = account.sign_transaction(tx)
    raw_hex = "0x" + signed.raw_transaction.hex()

    print(f"Broadcasting {amount} {asset} → {to} on {network}...")
    tx_hash = send_raw(rpc_url, raw_hex)
    print(f"Tx hash: {tx_hash}")

    entry = {
        "date":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "amount":  amount,
        "asset":   asset,
        "network": network,
        "to":      to,
        "purpose": purpose,
        "tx_hash": tx_hash,
    }
    log_to_wallet(output_path, entry)


if __name__ == "__main__":
    main()
