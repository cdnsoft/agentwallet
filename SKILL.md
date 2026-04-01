---
name: treasury-log
description: Log financial transactions (x402 payments, crypto swaps, on-chain actions) to a public treasury.json file and commit to git. Use whenever an agent spends money autonomously — x402 API calls, USDC payments, ETH swaps, or any blockchain transaction. Ensures financial transparency by making every autonomous spend auditable. Use log_transaction.sh to record each tx immediately after it occurs.
---

# Treasury Log

Structural financial transparency for autonomous agents. Every transaction gets logged to `treasury.json`, committed, and pushed. The log is append-only and public.

## Setup

Requires a `treasury.json` file in the workspace root:

```json
{"transactions":[]}
```

The script creates it automatically if missing.

## Log a Transaction

```bash
python3 scripts/treasury-log/log_transaction.py <amount> <asset> <network> <purpose> [tx_hash]
```

Examples:
```bash
python3 scripts/treasury-log/log_transaction.py 0.001 ETH Base "Swap ETH→USDC via Uniswap" 0xabc123...
python3 scripts/treasury-log/log_transaction.py 0.02 USDC Base "GateSkip FunCaptcha solve" 0xdef456...
python3 scripts/treasury-log/log_transaction.py 0.02 USDC Base "Actors.dev email to non-owner" pending
```

No external dependencies — stdlib only. Requires Python 3.6+ and git.

Output format in `treasury.json`:
```json
{
  "transactions": [
    {
      "date": "2026-04-01T10:00:00Z",
      "amount": "0.02",
      "asset": "USDC",
      "network": "Base",
      "purpose": "GateSkip FunCaptcha solve",
      "tx_hash": "0xdef456..."
    }
  ]
}
```

## Rules

- Log **before or immediately after** every transaction — never batch or defer
- Use `"pending"` for tx hash if not yet confirmed, update when known
- `treasury.json` is append-only — never modify past entries
- After logging, git commit + push happens automatically
