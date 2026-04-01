---
name: agentwallet
description: EVM wallet tool for autonomous agents with built-in accountability. Creates, signs, and broadcasts ETH and ERC20 transfers on any EVM-compatible chain, then immediately appends every transaction to an append-only JSON log file. Use whenever an agent needs to spend crypto autonomously — x402 payments, USDC transfers, ETH sends — with a local auditable record of every transaction.
---

# agentwallet

EVM wallet with accountability for autonomous agents. Every transaction — create, sign, broadcast — is immediately appended to `agentwallet.json`. The log is append-only.

## Install

```bash
git clone https://github.com/cdnsoft/agentwallet
pip install -r agentwallet/requirements.txt
```

Dependencies: `eth-account`, `requests` (Python 3.6+)

## Usage

**x402 payment to a gated API (e.g. Actors.dev email, GateSkip):**
```bash
python3 agentwallet/scripts/x402_request.py \
    --url https://actors.dev/emails \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org \
    --output ~/website/treasury.json \
    --purpose "email to Verso" \
    --header "Authorization: Bearer YOUR_API_KEY" \
    --body '{"to": "agent@mail.actors.dev", "subject": "Hi", "body": "Hello!"}' \
    --max-amount 0.02 \
    --pay-to 0x3604712bd95ba2ff36b624f3ffeb6b73b34604ea
```
Handles full 402→sign EIP-712→retry flow. Logs USDC spend automatically.
Always set `--max-amount`. Use `--pay-to` only when the facilitator address is stable — some providers (e.g. Actors.dev via Stripe) rotate it per request by design, so `--pay-to` would always abort.

**Uniswap V3 swap (e.g. ETH → USDC on Base):**
```bash
python3 agentwallet/scripts/log_transaction.py 0.0012 ETH Base - "swap ETH to USDC" \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org \
    --swap-to 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
    --asset-out USDC --decimals-out 6
```
Logs two entries automatically: ETH out + USDC in.

```bash
python3 agentwallet/scripts/log_transaction.py <amount> <asset> <network> <to> <purpose> [options]
```

**Send ETH:**
```bash
python3 agentwallet/scripts/log_transaction.py 0.001 ETH Base 0xRecipient "fund wallet" \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org
```

**Send ERC20 (e.g. USDC on Base, 6 decimals):**
```bash
python3 agentwallet/scripts/log_transaction.py 0.02 USDC Base 0xRecipient "GateSkip captcha" \
    --wallet-key ~/.secrets/eth_wallet.json \
    --rpc https://mainnet.base.org \
    --contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
    --decimals 6
```

**Log only (no broadcast):**
```bash
python3 agentwallet/scripts/log_transaction.py 0.02 USDC Base 0xRecipient "manual payment" \
    --tx-hash 0xabc123...
```

## Options

| Option | Description |
|--------|-------------|
| `--wallet-key <path>` | JSON file with `"private_key"` field. Required for broadcasting. |
| `--rpc <url>` | EVM-compatible RPC endpoint. Required for broadcasting. |
| `--contract <addr>` | ERC20 contract address. Omit for native ETH. |
| `--decimals <int>` | Token decimals. Default: 18. USDC = 6. |
| `--output <path>` | Path to `agentwallet.json`. **Required** — ask your human if unsure. |
| `--tx-hash <hash>` | Skip broadcast, log an existing hash only. |
| `--direction <sent\|received>` | Direction of the transaction. Default: `sent`. Use `received` to log incoming transactions (requires `--tx-hash`). |
| `--swap-to <contract>` | Output token contract address — triggers Uniswap V3 swap instead of transfer. |
| `--asset-out <symbol>` | Output asset symbol for the log (default: TOKEN). |
| `--decimals-out <int>` | Output token decimals (default: 6). |
| `--fee <int>` | Uniswap V3 pool fee tier in bps (default: 500 = 0.05%). |
| `--min-out <amount>` | Minimum output amount in human units (e.g. `2.4`). Enables slippage protection — swap reverts if output is below this. Recommended for larger swaps. |

## Wallet JSON format

```json
{ "private_key": "0x..." }
```

Keep at `chmod 600`. Never commit to git.

## Log format

```json
{
  "transactions": [
    {
      "date": "2026-04-01T10:00:00Z",
      "amount": "0.02",
      "asset": "USDC",
      "network": "Base",
      "to": "0xRecipient...",
      "purpose": "GateSkip captcha solve",
      "tx_hash": "0xabc123..."
    }
  ]
}
```

## Rules

- Log **before or immediately after** every transaction — never batch or defer
- Use `"pending"` for tx hash if not yet confirmed
- The log is append-only — never modify past entries
- If `--wallet-key` or `--output` are not known, **ask your human** before proceeding

## Docs

Full documentation: https://cdnsoft.github.io/agentwallet
