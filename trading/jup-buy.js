const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58').default;
const fs = require('fs');

const PRIVATE_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/jupiter_private_key.txt', 'utf8').trim();

async function buy() {
  // Get quote
  const quoteUrl = 'https://lite-api.jup.ag/swap/v1/quote?' + new URLSearchParams({
    inputMint: 'So11111111111111111111111111111111111111112', // SOL
    outputMint: '8Jx8AAHj86wbQgUTjGuj6GTTL5Ps3cqxKRTvpaJApump', // PENGUIN
    amount: (0.45 * 1e9).toString(), // 0.45 SOL in lamports
    slippageBps: '1500' // 15%
  });
  
  console.log('Getting quote...');
  const quoteRes = await fetch(quoteUrl);
  const quote = await quoteRes.json();
  
  if (quote.error) {
    console.error('Quote error:', quote.error);
    return;
  }
  console.log('Quote:', quote.outAmount, 'PENGUIN');
  
  // Get swap transaction
  const swapRes = await fetch('https://lite-api.jup.ag/swap/v1/swap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quoteResponse: quote,
      userPublicKey: 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L',
      wrapAndUnwrapSol: true
    })
  });
  
  const swapData = await swapRes.json();
  if (swapData.error) {
    console.error('Swap error:', swapData.error);
    return;
  }
  
  console.log('Got swap transaction');
  
  // Sign and send
  const keypair = Keypair.fromSecretKey(bs58.decode(PRIVATE_KEY));
  const txBuf = Buffer.from(swapData.swapTransaction, 'base64');
  const tx = VersionedTransaction.deserialize(txBuf);
  tx.sign([keypair]);
  
  const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
  const sig = await connection.sendTransaction(tx, { skipPreflight: true, maxRetries: 3 });
  console.log('Tx:', 'https://solscan.io/tx/' + sig);
  
  const conf = await connection.confirmTransaction(sig, 'confirmed');
  console.log('Result:', conf.value.err ? 'FAILED' : 'SUCCESS!');
}
buy().catch(console.error);
