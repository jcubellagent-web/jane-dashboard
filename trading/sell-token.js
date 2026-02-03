#!/usr/bin/env node
const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const fs = require('fs');
const path = require('path');

const SOL_MINT = 'So11111111111111111111111111111111111111112';
const JUPITER_LITE_API = 'https://lite-api.jup.ag';
const RPC_URL = 'https://api.mainnet-beta.solana.com';
const KEY_FILE = path.join(process.env.HOME, '.openclaw/workspace/.secrets/jupiter_private_key.txt');

function base58Decode(str) {
  const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  const ALPHABET_MAP = {};
  for (let i = 0; i < ALPHABET.length; i++) ALPHABET_MAP[ALPHABET[i]] = BigInt(i);
  let num = 0n;
  for (const char of str) num = num * 58n + ALPHABET_MAP[char];
  const bytes = [];
  while (num > 0n) { bytes.unshift(Number(num % 256n)); num = num / 256n; }
  for (let i = 0; i < str.length && str[i] === '1'; i++) bytes.unshift(0);
  return new Uint8Array(bytes);
}

function loadWallet() {
  const privateKeyBase58 = fs.readFileSync(KEY_FILE, 'utf-8').trim();
  return Keypair.fromSecretKey(base58Decode(privateKeyBase58));
}

async function sellToken(tokenMint, amount, wallet) {
  console.log(`\n💰 Selling ${amount} tokens -> SOL`);
  console.log(`Token: ${tokenMint.slice(0,8)}...`);

  // Get quote (token -> SOL)
  const quoteUrl = `${JUPITER_LITE_API}/swap/v1/quote?` + new URLSearchParams({
    inputMint: tokenMint,
    outputMint: SOL_MINT,
    amount: amount.toString(),
    slippageBps: '100',
  });
  
  console.log('📡 Getting quote...');
  const quoteRes = await fetch(quoteUrl);
  const quote = await quoteRes.json();
  
  if (quote.error) throw new Error(quote.error);
  
  const solOut = parseInt(quote.outAmount) / 1e9;
  console.log(`📋 Will receive: ~${solOut.toFixed(4)} SOL`);

  // Get swap transaction
  console.log('📝 Building transaction...');
  const swapRes = await fetch(`${JUPITER_LITE_API}/swap/v1/swap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quoteResponse: quote,
      userPublicKey: wallet.publicKey.toString(),
      wrapAndUnwrapSol: true,
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: 'auto',
    }),
  });
  const swapData = await swapRes.json();
  
  if (!swapData.swapTransaction) throw new Error(JSON.stringify(swapData));

  // Sign
  console.log('✍️  Signing...');
  const tx = VersionedTransaction.deserialize(Buffer.from(swapData.swapTransaction, 'base64'));
  tx.sign([wallet]);

  // Send
  console.log('🚀 Sending...');
  const connection = new Connection(RPC_URL, 'confirmed');
  const txid = await connection.sendRawTransaction(tx.serialize(), { skipPreflight: true, maxRetries: 2 });
  
  console.log(`📤 TX: https://solscan.io/tx/${txid}`);
  
  // Confirm
  console.log('⏳ Confirming...');
  const conf = await connection.confirmTransaction(txid, 'confirmed');
  
  if (conf.value.err) {
    console.log('❌ Failed:', conf.value.err);
    return { status: 'Failed', signature: txid };
  }
  
  console.log(`\n✅ Sold! Received ~${solOut.toFixed(4)} SOL`);
  return { status: 'Success', signature: txid, solReceived: solOut };
}

async function main() {
  const [tokenMint, amount] = process.argv.slice(2);
  if (!tokenMint || !amount) {
    console.log('Usage: node sell-token.js <TOKEN_MINT> <AMOUNT>');
    process.exit(1);
  }
  const wallet = loadWallet();
  console.log(`🔑 Wallet: ${wallet.publicKey.toString()}`);
  await sellToken(tokenMint, amount, wallet);
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
