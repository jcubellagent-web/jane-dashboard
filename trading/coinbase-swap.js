#!/usr/bin/env node
const { CdpClient } = require('@coinbase/cdp-sdk');
const fs = require('fs');
const path = require('path');

const SECRETS = path.join(process.env.HOME, '.openclaw/workspace/.secrets');

async function main() {
  const [,, outputMint, solAmountStr] = process.argv;
  if (!outputMint || !solAmountStr) {
    console.error('Usage: node coinbase-swap.js <outputMint> <solAmount>');
    process.exit(1);
  }
  
  const solAmount = parseFloat(solAmountStr);
  const lamports = Math.floor(solAmount * 1e9);
  
  const keyFile = fs.readFileSync(path.join(SECRETS, 'coinbase_cdp_api_key.txt'), 'utf8').trim();
  const apiKeyId = keyFile.match(/API Key ID: (.+)/)?.[1]?.trim();
  let apiKeySecret = keyFile.match(/Secret: (.+)/)?.[1]?.trim();
  const walletSecret = keyFile.match(/Wallet Secret: (.+)/)?.[1]?.trim();
  
  console.log(`Swapping ${solAmount} SOL for ${outputMint.slice(0,8)}...`);
  
  const cdp = new CdpClient({ apiKeyId, apiKeySecret, walletSecret });
  const account = await cdp.solana.getOrCreateAccount({ name: 'Jane-SOL' });
  console.log(`Wallet: ${account.address}`);
  
  // Get Jupiter quote
  const SOL_MINT = 'So11111111111111111111111111111111111111112';
  const quoteUrl = `https://lite-api.jup.ag/swap/v1/quote?inputMint=${SOL_MINT}&outputMint=${outputMint}&amount=${lamports}&slippageBps=100`;
  
  const quoteRes = await fetch(quoteUrl);
  const quote = await quoteRes.json();
  
  if (quote.error) {
    console.error('Quote error:', quote.error);
    process.exit(1);
  }
  
  const outAmount = quote.outAmount;
  console.log(`Quote: ${solAmount} SOL → ${outAmount} tokens (slippage: 1%)`);
  
  // Get swap transaction
  const swapRes = await fetch('https://lite-api.jup.ag/swap/v1/swap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quoteResponse: quote,
      userPublicKey: account.address,
      wrapAndUnwrapSol: true,
    })
  });
  const swapData = await swapRes.json();
  
  if (swapData.error) {
    console.error('Swap error:', swapData.error);
    process.exit(1);
  }
  
  // Sign via CDP
  console.log('Signing transaction via CDP...');
  const signed = await cdp.solana.signTransaction({
    address: account.address,
    transaction: swapData.swapTransaction,
  });
  
  console.log('Sending transaction...');
  const result = await cdp.solana.sendTransaction({
    address: account.address,
    transaction: signed.signedTransaction || signed.transaction || signed,
    network: 'solana',
  });
  
  console.log(`✅ Transaction sent!`);
  const sig = result.transactionHash || result.signature || result.txSignature || JSON.stringify(result);
  console.log(`TX: ${sig}`);
  console.log(`Explorer: https://solscan.io/tx/${sig}`);
}

main().catch(e => {
  console.error('Error:', e.message || e);
  process.exit(1);
});
