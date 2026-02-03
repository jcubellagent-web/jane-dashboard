#!/usr/bin/env node
/**
 * Derive Solana keypair from seed phrase and save private key
 */

const { Keypair } = require('@solana/web3.js');
const bip39 = require('bip39');
const { derivePath } = require('ed25519-hd-key');
const fs = require('fs');
const path = require('path');

const SECRETS_DIR = path.join(process.env.HOME, '.openclaw/workspace/.secrets');
const SEED_FILE = path.join(SECRETS_DIR, 'phantom_wallet.txt');
const KEY_FILE = path.join(SECRETS_DIR, 'solana_private_key.json');

// Base58 encode function
function base58Encode(buffer) {
  const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  let num = BigInt('0x' + Buffer.from(buffer).toString('hex'));
  let encoded = '';
  while (num > 0n) {
    encoded = ALPHABET[Number(num % 58n)] + encoded;
    num = num / 58n;
  }
  // Add leading zeros
  for (let i = 0; i < buffer.length && buffer[i] === 0; i++) {
    encoded = '1' + encoded;
  }
  return encoded;
}

async function main() {
  // Read seed phrase
  const seedPhrase = fs.readFileSync(SEED_FILE, 'utf-8').trim();
  console.log('Loaded seed phrase');

  // Convert to seed
  const seed = await bip39.mnemonicToSeed(seedPhrase);
  
  const expectedAddress = 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L';
  
  // Try many derivation paths
  const paths = [
    "m/44'/501'/0'/0'",
    "m/44'/501'/0'",
    "m/44'/501'",
    "m/44'/501'/0'/0'/0'",
  ];
  
  // Also try with account indices 0-10
  for (let i = 0; i <= 10; i++) {
    paths.push(`m/44'/501'/${i}'/0'`);
    paths.push(`m/44'/501'/0'/${i}'`);
  }
  
  console.log('Expected address:', expectedAddress);
  console.log('Trying derivation paths...\n');
  
  for (const derivationPath of paths) {
    try {
      const derivedSeed = derivePath(derivationPath, seed.toString('hex')).key;
      const keypair = Keypair.fromSeed(derivedSeed);
      const address = keypair.publicKey.toString();
      
      if (address === expectedAddress) {
        console.log(`✅ MATCH FOUND!`);
        console.log(`   Path: ${derivationPath}`);
        console.log(`   Address: ${address}`);
        
        // Save as JSON array (Solana CLI format)
        const secretKeyArray = Array.from(keypair.secretKey);
        fs.writeFileSync(KEY_FILE, JSON.stringify(secretKeyArray));
        console.log(`\nPrivate key saved to: ${KEY_FILE}`);
        return keypair;
      }
    } catch (e) {
      // Skip invalid paths
    }
  }
  
  // If no match, try raw seed (no derivation)
  console.log('Trying raw seed (first 32 bytes)...');
  const rawKeypair = Keypair.fromSeed(seed.slice(0, 32));
  console.log('Raw seed address:', rawKeypair.publicKey.toString());
  
  if (rawKeypair.publicKey.toString() === expectedAddress) {
    console.log('✅ MATCH with raw seed!');
    const secretKeyArray = Array.from(rawKeypair.secretKey);
    fs.writeFileSync(KEY_FILE, JSON.stringify(secretKeyArray));
    console.log(`Private key saved to: ${KEY_FILE}`);
    return rawKeypair;
  }
  
  console.log('\n❌ Could not find matching derivation path.');
  console.log('The seed phrase may be for a different wallet.');
  
  // Save the first derived key anyway for testing
  const derivedSeed = derivePath("m/44'/501'/0'/0'", seed.toString('hex')).key;
  const keypair = Keypair.fromSeed(derivedSeed);
  const secretKeyArray = Array.from(keypair.secretKey);
  fs.writeFileSync(KEY_FILE, JSON.stringify(secretKeyArray));
  console.log(`\nSaved default derivation key (${keypair.publicKey.toString()}) to: ${KEY_FILE}`);
}

main().catch(console.error);
