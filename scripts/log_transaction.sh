#!/bin/bash
# log_transaction.sh — append a transaction to treasury.md and commit
# Usage: log_transaction.sh "<amount> <asset>" "<network>" "<purpose>" "<tx_hash>"
# Example: log_transaction.sh "0.02 USDC" "Base" "GateSkip captcha solve" "0xabc123..."

set -e

AMOUNT="$1"
NETWORK="$2"
PURPOSE="$3"
TX_HASH="${4:-pending}"
DATE=$(date -u +%Y-%m-%d)

# Find workspace root (look for treasury.md)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="${TREASURY_WORKSPACE:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
TREASURY="$WORKSPACE/treasury.md"

if [ -z "$AMOUNT" ] || [ -z "$NETWORK" ] || [ -z "$PURPOSE" ]; then
  echo "Usage: log_transaction.sh <amount> <network> <purpose> [tx_hash]"
  echo "Example: log_transaction.sh \"0.02 USDC\" \"Base\" \"GateSkip captcha solve\" \"0xabc...\""
  exit 1
fi

if [ ! -f "$TREASURY" ]; then
  echo "❌ treasury.md not found at $TREASURY"
  echo "Create it first with a header row."
  exit 1
fi

echo "| $DATE | $AMOUNT | $NETWORK | $PURPOSE | $TX_HASH |" >> "$TREASURY"

cd "$WORKSPACE"
git add treasury.md
git commit -m "treasury: $PURPOSE ($AMOUNT on $NETWORK)"
git push

echo "✅ Logged: $AMOUNT on $NETWORK — $PURPOSE"
