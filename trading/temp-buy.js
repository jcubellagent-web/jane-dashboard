const { Keypair, VersionedTransaction, Connection } = require('@solana/web3.js');
const bs58 = require('bs58').default;
const fs = require('fs');

const PRIVATE_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/jupiter_private_key.txt', 'utf8').trim();
const PUBLIC_KEY = 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L';

async function buy() {
  const response = await fetch('https://pumpportal.fun/api/trade-local', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      publicKey: PUBLIC_KEY,
      action: 'buy',
      mint: '8Jx8AAHj86wbQgUTjGuj6GTTL5Ps3cqxKRTvpaJApump',
      amount: '0.4',
      denominatedInSol: 'true',
      slippage: '50', // Very high slippage
      priorityFee: '0.005',
      pool: 'pump' // Explicitly use pump.fun
    })
  });
  
  if (!response.ok) {
    console.error('API Error:', await response.text());
    return;
  }
  
  const txData = await response.arrayBuffer();
  console.log('Got tx data');
  
  const keypair = Keypair.fromSecretKey(bs58.decode(PRIVATE_KEY));
  const tx = VersionedTransaction.deserialize(new Uint8Array(txData));
  tx.sign([keypair]);
  
  const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
  const sig = await connection.sendTransaction(tx, { skipPreflight: true });
  console.log('Tx:', 'https://solscan.io/tx/' + sig);
  
  const conf = await connection.confirmTransaction(sig, 'confirmed');
  console.log('Result:', conf.value.err ? 'FAILED: ' + JSON.stringify(conf.value.err) : 'SUCCESS!');
}
buy();
