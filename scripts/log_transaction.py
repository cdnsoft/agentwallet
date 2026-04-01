#!/usr/bin/env python3
"""
log_transaction.py — append a transaction to treasury.json and commit to git.

Usage:
    python3 log_transaction.py <amount> <asset> <network> <purpose> [tx_hash]

Example:
    python3 log_transaction.py 0.02 USDC Base "GateSkip captcha solve" 0xabc123...
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_workspace(script_path: Path) -> Path:
    """Walk up from script location to find treasury.json, or use TREASURY_WORKSPACE env."""
    import os
    env_ws = os.environ.get("TREASURY_WORKSPACE")
    if env_ws:
        return Path(env_ws)
    # scripts/ → treasury-log/ → projects/ → workspace/
    return script_path.parent.parent.parent.parent


def main():
    if len(sys.argv) < 5:
        print("Usage: log_transaction.py <amount> <asset> <network> <purpose> [tx_hash]")
        print('Example: log_transaction.py 0.02 USDC Base "GateSkip captcha solve" 0xabc...')
        sys.exit(1)

    amount  = sys.argv[1]
    asset   = sys.argv[2]
    network = sys.argv[3]
    purpose = sys.argv[4]
    tx_hash = sys.argv[5] if len(sys.argv) > 5 else "pending"

    workspace = find_workspace(Path(__file__).resolve())
    treasury  = workspace / "treasury.json"

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
