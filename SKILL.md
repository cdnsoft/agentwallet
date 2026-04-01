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
python3 log_transaction.py <amount> <asset> <network> <to> <purpose> [options]
```

**Native ETH transfer:**
```bash
python3 log_transaction.py 0.001 ETH Base 0xRecipient "fund wallet" \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org
```

**ERC20 transfer (e.g. USDC, 6 decimals):**
```bash
python3 log_transaction.py 0.02 USDC Base 0xRecipient "GateSkip captcha" \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org \
    --contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
    --decimals 6
```

**Log only (no broadcast):**
```bash
python3 log_transaction.py 0.02 USDC Base 0xRecipient "manual payment" \
    --tx-hash 0xabc123... \
    --output /path/to/treasury.json
```

Options:
- `--wallet-key` — path to JSON file with `private_key` field
- `--rpc` — EVM RPC endpoint
- `--contract` — ERC20 contract address (omit for native ETH)
- `--decimals` — token decimals (default: 18; USDC = 6)
- `--output` — path to treasury.json (default: workspace root)
- `--tx-hash` — skip broadcast, log existing hash only

Dependencies (see `requirements.txt`):
```bash
pip install -r requirements.txt
```

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
