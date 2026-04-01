#!/usr/bin/env python3
"""
log_transaction.py — append a transaction to treasury.json and commit to git.

Usage:
    python3 log_transaction.py <amount> <asset> <network> <purpose> [tx_hash] [--output <path>]

Arguments:
    amount   — numeric amount (e.g. 0.02)
    asset    — asset symbol (e.g. USDC, ETH)
    network  — network name (e.g. Base, Bitcoin)
    purpose  — description of the transaction
    tx_hash  — transaction hash or "pending" (default: pending)

Options:
    --output <path>  — path to treasury.json (default: treasury.json in workspace root)

Example:
    python3 log_transaction.py 0.02 USDC Base "GateSkip captcha solve" 0xabc123...
    python3 log_transaction.py 0.02 USDC Base "GateSkip captcha solve" 0xabc... --output /path/to/treasury.json
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_workspace(script_path: Path) -> Path:
    """Walk up from script location to find workspace root, or use TREASURY_WORKSPACE env."""
    import os
    env_ws = os.environ.get("TREASURY_WORKSPACE")
    if env_ws:
        return Path(env_ws)
    # scripts/ → treasury-log/ → projects/ → workspace/
    return script_path.parent.parent.parent.parent


def main():
    args = sys.argv[1:]

    # Extract --output flag
    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 >= len(args):
            print("Error: --output requires a path argument")
            sys.exit(1)
        output_path = Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if len(args) < 4:
        print("Usage: log_transaction.py <amount> <asset> <network> <purpose> [tx_hash] [--output <path>]")
        print('Example: log_transaction.py 0.02 USDC Base "GateSkip captcha solve" 0xabc...')
        sys.exit(1)

    amount  = args[0]
    asset   = args[1]
    network = args[2]
    purpose = args[3]
    tx_hash = args[4] if len(args) > 4 else "pending"

    workspace = find_workspace(Path(__file__).resolve())
    treasury  = output_path.resolve() if output_path else workspace / "treasury.json"

    # Create treasury.json if missing
    if not treasury.exists():
        treasury.write_text(json.dumps({"transactions": []}, indent=2))

    data = json.loads(treasury.read_text())

    entry = {
        "date":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "amount":  amount,
        "asset":   asset,
        "network": network,
        "purpose": purpose,
        "tx_hash": tx_hash,
    }

    data["transactions"].append(entry)
    treasury.write_text(json.dumps(data, indent=2))

    # Git commit and push
    subprocess.run(["git", "add", "treasury.json"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"treasury: {purpose} ({amount} {asset} on {network})"],
        cwd=workspace, check=True,
    )
    subprocess.run(["git", "push"], cwd=workspace, check=True)

    print(f"✅ Logged: {amount} {asset} on {network} — {purpose}")


if __name__ == "__main__":
    main()
