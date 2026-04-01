#!/bin/bash
# log_transaction.sh — append a transaction to treasury.json and commit
# Usage: log_transaction.sh "<amount>" "<asset>" "<network>" "<purpose>" "<tx_hash>"
# Example: log_transaction.sh "0.02" "USDC" "Base" "GateSkip captcha solve" "0xabc123..."

set -e

AMOUNT="$1"
ASSET="$2"
NETWORK="$3"
PURPOSE="$4"
TX_HASH="${5:-pending}"
DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${TREASURY_WORKSPACE:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
TREASURY="$WORKSPACE/treasury.json"

if [ -z "$AMOUNT" ] || [ -z "$ASSET" ] || [ -z "$NETWORK" ] || [ -z "$PURPOSE" ]; then
  echo "Usage: log_transaction.sh <amount> <asset> <network> <purpose> [tx_hash]"
  echo "Example: log_transaction.sh \"0.02\" \"USDC\" \"Base\" \"GateSkip captcha solve\" \"0xabc...\""
  exit 1
fi

# Create treasury.json if it doesn't exist
if [ ! -f "$TREASURY" ]; then
  echo '{"transactions":[]}' > "$TREASURY"
fi

# Build new entry and append using python3
python3 - <<PYEOF
import json, sys

path = "$TREASURY"
with open(path, "r") as f:
    data = json.load(f)

entry = {
    "date": "$DATE",
    "amount": "$AMOUNT",
    "asset": "$ASSET",
    "network": "$NETWORK",
    "purpose": "$PURPOSE",
    "tx_hash": "$TX_HASH"
}

data["transactions"].append(entry)

with open(path, "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Logged: {entry['amount']} {entry['asset']} on {entry['network']} — {entry['purpose']}")
PYEOF

cd "$WORKSPACE"
git add treasury.json
git commit -m "treasury: $PURPOSE ($AMOUNT $ASSET on $NETWORK)"
git push
