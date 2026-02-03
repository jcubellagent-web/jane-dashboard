# Jupiter Trading Skill

Fast memecoin trading via Jupiter Ultra API instead of browser automation.

## Why This is Better

| Method | Time per Trade | Reliability |
|--------|---------------|-------------|
| Browser automation | 60-90 seconds | ~80% (UI changes break it) |
| Jupiter Ultra API | 2-5 seconds | 99%+ (programmatic) |

## Jupiter Ultra API Flow

### Step 1: Get Order (Quote + Unsigned Transaction)
```bash
curl "https://api.jup.ag/ultra/v1/order?\
inputMint=So11111111111111111111111111111111111111112&\
outputMint=TOKEN_MINT_ADDRESS&\
amount=AMOUNT_IN_LAMPORTS&\
taker=WALLET_ADDRESS"
```

**Parameters:**
- `inputMint`: SOL = `So11111111111111111111111111111111111111112`
- `outputMint`: The token contract address (e.g., pump.fun address)
- `amount`: Amount in lamports (0.1 SOL = 100000000)
- `taker`: Your wallet public address

**Response includes:**
- `transaction`: Base64 unsigned transaction
- `requestId`: Use this in execute step

### Step 2: Sign Transaction
Requires programmatic signing with wallet private key (from seed phrase).

```javascript
import { VersionedTransaction } from '@solana/web3.js';

const transaction = VersionedTransaction.deserialize(
  Buffer.from(orderResponse.transaction, 'base64')
);
transaction.sign([wallet]);
const signedTransaction = Buffer.from(transaction.serialize()).toString('base64');
```

### Step 3: Execute Order
```bash
curl -X POST "https://api.jup.ag/ultra/v1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "signedTransaction": "BASE64_SIGNED_TX",
    "requestId": "REQUEST_ID_FROM_STEP_1"
  }'
```

Jupiter handles:
- Transaction broadcasting via their Beam infrastructure
- Priority fee optimization
- Slippage protection
- MEV protection
- Status polling

## Implementation Options

### Option A: Node.js Script (Recommended)
Create a script that:
1. Loads wallet from seed phrase
2. Calls Jupiter API
3. Signs locally
4. Executes

**Pros:** Full control, fast, scriptable
**Cons:** Requires storing seed phrase securely

### Option B: Solana CLI + Jupiter
Use `solana` CLI with a local keypair file.

### Option C: Keep Browser (Current)
Continue using browser automation but optimize:
- Pre-load Jupiter page
- Cache token addresses
- Use direct URLs where possible

## Key Addresses

**SOL Mint:** `So11111111111111111111111111111111111111112`
**USDC Mint:** `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`

## Wallet Info
- **Address:** `ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L`
- **Seed phrase:** `~/.openclaw/workspace/.secrets/phantom_wallet.txt`

## Rate Limits
Jupiter Ultra API has dynamic rate limits based on volume. No API key needed for basic usage.

## Quick Reference

**0.1 SOL swap to any token:**
```
amount=100000000 (lamports)
```

**Lamport conversion:**
- 1 SOL = 1,000,000,000 lamports
- 0.1 SOL = 100,000,000 lamports
- 0.01 SOL = 10,000,000 lamports

## TODO
- [ ] Write Node.js swap script
- [ ] Test with small amount
- [ ] Add to sub-agent toolkit
