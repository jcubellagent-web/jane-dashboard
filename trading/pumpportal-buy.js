#!/usr/bin/env node
/**
 * PumpPortal Buy Script
 * Buys tokens via PumpPortal's Local Transaction API
 */

const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58').default;
const fs = require('fs');

// Configuration
const PRIVATE_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/jupiter_private_key.txt', 'utf8').trim();
const PUBLIC_KEY = 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L';
const RPC_ENDPOINT = 'https://api.mainnet-beta.solana.com';

async function buyToken(mint, solAmount) {
  console.log(`\n--- Buying with ${solAmount} SOL ---`);
  console.log(`Mint: ${mint}`);
  
  try {
    // Get transaction from PumpPortal
    const response = await fetch('https://pumpportal.fun/api/trade-local', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        publicKey: PUBLIC_KEY,
        action: 'buy',
        mint: mint,
        amount: solAmount.toString(),
        denominatedInSol: 'true', // Amount is in SOL
        slippage: '15',
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
    
    console.log(`✅ Purchase successful!`);
    return true;
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    return false;
  }
}

const mint = process.argv[2] || '8Jx8AAHj86wbQgUTjGuj6GTTL5Ps3cqxKRTvpaJApump'; // PENGUIN
const solAmount = parseFloat(process.argv[3]) || 0.45; // Leave some for fees

buyToken(mint, solAmount);
