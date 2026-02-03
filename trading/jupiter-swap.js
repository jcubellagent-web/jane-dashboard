#!/usr/bin/env node
/**
 * Jupiter Lite API Swap Script
 * Usage: node jupiter-swap.js <outputMint> <solAmount>
 * Example: node jupiter-swap.js 4BmaxxckzuAnFZANYP8uZ4MQUBLoKBHxbx1xbZSDbank 0.1
 */

const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const fs = require('fs');
const path = require('path');

// Constants
const SOL_MINT = 'So11111111111111111111111111111111111111112';
const LAMPORTS_PER_SOL = 1_000_000_000;
const JUPITER_LITE_API = 'https://lite-api.jup.ag';
const RPC_URL = 'https://api.mainnet-beta.solana.com';
const KEY_FILE = path.join(process.env.HOME, '.openclaw/workspace/.secrets/jupiter_private_key.txt');

// Base58 decode
function base58Decode(str) {
  const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  const ALPHABET_MAP = {};
  for (let i = 0; i < ALPHABET.length; i++) {
    ALPHABET_MAP[ALPHABET[i]] = BigInt(i);
  }
  
  let num = 0n;
  for (const char of str) {
    num = num * 58n + ALPHABET_MAP[char];
  }
  
  const bytes = [];
  while (num > 0n) {
    bytes.unshift(Number(num % 256n));
    num = num / 256n;
  }
  
  for (let i = 0; i < str.length && str[i] === '1'; i++) {
    bytes.unshift(0);
  }
  
  return new Uint8Array(bytes);
}

function loadWallet() {
  const privateKeyBase58 = fs.readFileSync(KEY_FILE, 'utf-8').trim();
  const secretKey = base58Decode(privateKeyBase58);
  return Keypair.fromSecretKey(secretKey);
}

async function getQuote(inputMint, outputMint, amount) {
  const url = `${JUPITER_LITE_API}/swap/v1/quote?` + new URLSearchParams({
    inputMint,
    outputMint,
    amount: amount.toString(),
    slippageBps: '100', // 1% slippage for memecoins
  });

  console.log('📡 Getting quote from Jupiter Lite API...');
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get quote: ${error}`);
  }
  
  return response.json();
}

async function getSwapTransaction(quoteResponse, userPublicKey) {
  console.log('📝 Building swap transaction...');
  
  const response = await fetch(`${JUPITER_LITE_API}/swap/v1/swap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quoteResponse,
      userPublicKey: userPublicKey.toString(),
      wrapAndUnwrapSol: true,
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: 'auto',
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get swap transaction: ${error}`);
  }

  return response.json();
}

async function swap(outputMint, solAmount, wallet) {
  const lamports = Math.floor(solAmount * LAMPORTS_PER_SOL);
  const walletAddress = wallet.publicKey.toString();
  
  console.log(`\n💱 Swapping ${solAmount} SOL -> ${outputMint.slice(0,8)}...`);
  console.log(`👛 Wallet: ${walletAddress}`);
  console.log(`💰 Amount: ${lamports} lamports\n`);

  // Step 1: Get quote
  const quoteResponse = await getQuote(SOL_MINT, outputMint, lamports);
  
  console.log('📋 Quote received:');
  console.log(`   Input: ${quoteResponse.inAmount} lamports (${quoteResponse.inAmount / LAMPORTS_PER_SOL} SOL)`);
  console.log(`   Output: ${quoteResponse.outAmount} tokens`);
  console.log(`   Slippage: ${quoteResponse.slippageBps} bps`);
  console.log(`   Price Impact: ${quoteResponse.priceImpactPct}%`);

  // Step 2: Get swap transaction
  const swapResponse = await getSwapTransaction(quoteResponse, wallet.publicKey);
  
  if (!swapResponse.swapTransaction) {
    console.log('Swap response:', JSON.stringify(swapResponse, null, 2));
    throw new Error('No swap transaction in response');
  }

  // Step 3: Sign transaction
  console.log('✍️  Signing transaction...');
  const swapTransactionBuf = Buffer.from(swapResponse.swapTransaction, 'base64');
  const transaction = VersionedTransaction.deserialize(swapTransactionBuf);
  transaction.sign([wallet]);

  // Step 4: Send transaction
  console.log('🚀 Sending transaction...');
  const connection = new Connection(RPC_URL, 'confirmed');
  
  const rawTransaction = transaction.serialize();
  const txid = await connection.sendRawTransaction(rawTransaction, {
    skipPreflight: true,
    maxRetries: 2,
  });

  console.log(`📤 Transaction sent: ${txid}`);
  console.log(`🔗 https://solscan.io/tx/${txid}`);

  // Step 5: Confirm transaction
  console.log('⏳ Waiting for confirmation...');
  const confirmation = await connection.confirmTransaction(txid, 'confirmed');

  if (confirmation.value.err) {
    console.log(`\n❌ Transaction failed:`, confirmation.value.err);
    return { status: 'Failed', signature: txid, error: confirmation.value.err };
  }

  console.log(`\n✅ Swap successful!`);
  console.log(`📦 Expected output: ${quoteResponse.outAmount} tokens`);
  
  return { 
    status: 'Success', 
    signature: txid, 
    outputAmount: quoteResponse.outAmount,
    outputMint,
  };
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Jupiter Lite API Swap');
    console.log('Usage: node jupiter-swap.js <outputMint> <solAmount>');
    console.log('Example: node jupiter-swap.js 4BmaxxckzuAnFZANYP8uZ4MQUBLoKBHxbx1xbZSDbank 0.1');
    process.exit(1);
  }

  const [outputMint, solAmount] = args;

  try {
    const wallet = loadWallet();
    console.log(`🔑 Loaded wallet: ${wallet.publicKey.toString()}`);
    
    const result = await swap(outputMint, parseFloat(solAmount), wallet);
    
    console.log('\n--- JSON OUTPUT ---');
    console.log(JSON.stringify(result, null, 2));
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
