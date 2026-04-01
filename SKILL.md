---
name: treasury-log
description: Log financial transactions (x402 payments, crypto swaps, on-chain actions) to a public treasury.md file and commit to git. Use whenever an agent spends money autonomously — x402 API calls, USDC payments, ETH swaps, or any blockchain transaction. Ensures financial transparency by making every autonomous spend auditable. Use log_transaction.sh to record each tx immediately after it occurs.
---

# Treasury Log

Structural financial transparency for autonomous agents. Every transaction gets logged to `treasury.md`, committed, and pushed. The log is append-only and public.

## Setup

Requires a `treasury.md` file in the workspace root with this header:

```markdown
# Treasury Log

| Date | Amount | Network | Purpose | Tx Hash |
|------|--------|---------|---------|---------|
```

## Log a Transaction

```bash
scripts/treasury-log/log_transaction.sh "<amount> <asset>" "<network>" "<purpose>" "<tx_hash>"
```

Examples:
```bash
scripts/treasury-log/log_transaction.sh "0.001 ETH" "Base" "Swap ETH→USDC via Uniswap" "0xabc123..."
scripts/treasury-log/log_transaction.sh "0.02 USDC" "Base" "GateSkip FunCaptcha solve" "0xdef456..."
scripts/treasury-log/log_transaction.sh "0.02 USDC" "Base" "Actors.dev email to non-owner" "pending"
```

## Rules

- Log **before or immediately after** every transaction — never batch or defer
- Use `"pending"` for tx hash if not yet confirmed, update when known
- The `treasury.md` file is the source of truth — keep it append-only
- After logging, git commit + push happens automatically
