#!/usr/bin/env node
/**
 * PumpPortal Sell Script
 * Sells tokens via PumpPortal's Local Transaction API
 */

const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58').default;
const fs = require('fs');

// Configuration
const PRIVATE_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/jupiter_private_key.txt', 'utf8').trim();
const PUBLIC_KEY = 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L';
const RPC_ENDPOINT = 'https://api.mainnet-beta.solana.com';

// Token addresses to sell
const TOKENS = {
  ELON: { mint: '2akXpuyFXAVN5YofZpZMfBp2Vxognpmv9NooBMuHpump', amount: 8519.615032 },
  BlackWhale: { mint: '8y45AJzCUBSZL1UDFQRzCKovQBLQFudBrpPeg5yNpump', amount: 24415.653794 },
  Wojakcoin: { mint: 'J7PhYH81MtneKPJLAw6Rp4Y1aFqYmDfe42RvycE6pump', amount: 43010 },
  Luna: { mint: '4mBsTx1x93ek11Lv4T3kdTrHE6SzqXW19m1rvPsHpump', amount: 157505 },
  BANKR: { mint: '4BmaxxckzuAnFZANYP8uZ4MQUBLoKBHxbx1xbZSDbank', amount: 11720.37 }
};

async function sellToken(tokenName, mint, amount) {
  console.log(`\n--- Selling ${tokenName} ---`);
  console.log(`Mint: ${mint}`);
  console.log(`Amount: ${amount}`);
  
  try {
    // Get transaction from PumpPortal
    const response = await fetch('https://pumpportal.fun/api/trade-local', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        publicKey: PUBLIC_KEY,
        action: 'sell',
        mint: mint,
        amount: Math.floor(amount).toString(), // Sell whole tokens
        denominatedInSol: 'false',
        slippage: '15', // 15% slippage for low liquidity tokens
        priorityFee: '0.001',
        pool: 'auto'
      })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error: ${response.status} - ${errorText}`);
      return false;
    }
    
    const txData = await response.arrayBuffer();
    console.log(`Got transaction data (${txData.byteLength} bytes)`);
    
    // Decode and sign transaction
    const keypair = Keypair.fromSecretKey(bs58.decode(PRIVATE_KEY));
    const tx = VersionedTransaction.deserialize(new Uint8Array(txData));
    tx.sign([keypair]);
    
    // Send transaction
    const connection = new Connection(RPC_ENDPOINT, 'confirmed');
    const signature = await connection.sendTransaction(tx, {
      skipPreflight: true,
      maxRetries: 3
    });
    
    console.log(`✅ Transaction sent: https://solscan.io/tx/${signature}`);
    
    // Wait for confirmation
    const confirmation = await connection.confirmTransaction(signature, 'confirmed');
    if (confirmation.value.err) {
      console.error(`❌ Transaction failed: ${JSON.stringify(confirmation.value.err)}`);
      return false;
    }
    
    console.log(`✅ ${tokenName} sold successfully!`);
    return true;
  } catch (error) {
    console.error(`❌ Error selling ${tokenName}: ${error.message}`);
    return false;
  }
}

async function main() {
  const tokenToSell = process.argv[2];
  
  if (tokenToSell && TOKENS[tokenToSell]) {
    // Sell specific token
    const { mint, amount } = TOKENS[tokenToSell];
    await sellToken(tokenToSell, mint, amount);
  } else if (tokenToSell === 'all') {
    // Sell all tokens
    console.log('Selling all tokens...');
    for (const [name, { mint, amount }] of Object.entries(TOKENS)) {
      await sellToken(name, mint, amount);
      await new Promise(r => setTimeout(r, 2000)); // Wait 2s between trades
    }
  } else {
    console.log('Usage: node pumpportal-sell.js <tokenName|all>');
    console.log('Available tokens:', Object.keys(TOKENS).join(', '));
  }
}

main().catch(console.error);
