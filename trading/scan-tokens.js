#!/usr/bin/env node
/**
 * Token Scanner — fetches trending Solana tokens from DexScreener + CoinGecko,
 * filters by mcap/volume/momentum, ranks them, outputs to scan-results.json
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const SECRETS_DIR = path.join(__dirname, '..', '.secrets');
const OUTPUT = path.join(__dirname, 'scan-results.json');
const TRADES_JSON = path.join(__dirname, '..', 'dashboard', 'trades.json');

let CG_KEY = '';
try { CG_KEY = fs.readFileSync(path.join(SECRETS_DIR, 'coingecko_api_key.txt'), 'utf8').trim(); } catch {}

const MIN_MCAP = 150000;
const MIN_VOL_24H = 50000;
const EXTRA_DD_THRESHOLD = 300000;

function fetch(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { headers: { 'User-Agent': 'JaneAgent/1.0', ...headers } }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch { resolve(null); }
      });
    });
    req.on('error', reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
  });
}

async function fetchDexScreenerTrending() {
  try {
    // DexScreener token profiles (boosted/trending)
    const data = await fetch('https://api.dexscreener.com/token-boosts/top/v1');
    if (!Array.isArray(data)) return [];
    // Filter Solana tokens
    const solTokens = data.filter(t => t.chainId === 'solana');
    // Get detailed pair data for each
    const results = [];
    const addresses = solTokens.map(t => t.tokenAddress).filter(Boolean).slice(0, 20);
    if (addresses.length) {
      const batched = await fetch(`https://api.dexscreener.com/tokens/v1/solana/${addresses.join(',')}`);
      if (Array.isArray(batched)) {
        for (const pair of batched) {
          if (!pair || !pair.baseToken) continue;
          results.push({
            token: pair.baseToken.symbol,
            name: pair.baseToken.name,
            address: pair.baseToken.address,
            chain: 'solana',
            mcap: pair.marketCap || pair.fdv || 0,
            volume24h: pair.volume?.h24 || 0,
            priceUsd: parseFloat(pair.priceUsd || 0),
            priceChange24h: pair.priceChange?.h24 || 0,
            priceChange1h: pair.priceChange?.h1 || 0,
            liquidity: pair.liquidity?.usd || 0,
            pairAddress: pair.pairAddress,
            dexId: pair.dexId,
            source: 'dexscreener'
          });
        }
      }
    }
    return results;
  } catch (e) {
    console.error('DexScreener error:', e.message);
    return [];
  }
}

async function fetchCoinGeckoTrending() {
  try {
    const headers = CG_KEY ? { 'x-cg-demo-api-key': CG_KEY } : {};
    const data = await fetch('https://api.coingecko.com/api/v3/search/trending', headers);
    if (!data || !data.coins) return [];
    const results = [];
    for (const entry of data.coins) {
      const coin = entry.item;
      // CoinGecko trending doesn't always have chain info; check platforms
      const isSolana = coin.platforms && (coin.platforms.solana || Object.keys(coin.platforms).some(k => k.toLowerCase().includes('solana')));
      if (!isSolana && coin.id) {
        // Try to fetch detail to check if it's on Solana
        continue; // Skip non-Solana for efficiency
      }
      const solAddr = coin.platforms?.solana || '';
      results.push({
        token: coin.symbol?.toUpperCase(),
        name: coin.name,
        address: solAddr,
        chain: 'solana',
        mcap: coin.data?.market_cap || coin.market_cap_rank || 0,
        priceUsd: parseFloat(coin.data?.price || 0),
        priceChange24h: parseFloat(coin.data?.price_change_percentage_24h?.usd || 0),
        volume24h: coin.data?.total_volume ? parseFloat(coin.data.total_volume.replace(/[$,]/g, '')) : 0,
        liquidity: 0,
        coingeckoId: coin.id,
        source: 'coingecko'
      });
    }
    return results;
  } catch (e) {
    console.error('CoinGecko error:', e.message);
    return [];
  }
}

async function checkHolderInfo(address) {
  // Use DexScreener pair data for liquidity info (holder distribution requires Helius/Birdeye)
  // Return basic flags
  const info = { holdersChecked: false, liquidityLocked: 'unknown', topHolderPct: null };
  try {
    // Check via DexScreener for liquidity
    const pairs = await fetch(`https://api.dexscreener.com/tokens/v1/solana/${address}`);
    if (Array.isArray(pairs) && pairs.length > 0) {
      const best = pairs[0];
      info.liquidity = best.liquidity?.usd || 0;
      info.holdersChecked = true;
      // Flag suspicious if liquidity < 10% of mcap
      const mcap = best.marketCap || best.fdv || 0;
      if (mcap > 0 && info.liquidity / mcap < 0.05) {
        info.liquidityWarning = true;
      }
    }
  } catch {}
  return info;
}

function scoreToken(t) {
  let score = 0;
  // Volume/mcap ratio (higher = more activity)
  if (t.mcap > 0) score += Math.min((t.volume24h / t.mcap) * 20, 30);
  // Price momentum
  if (t.priceChange24h > 0) score += Math.min(t.priceChange24h / 5, 20);
  if (t.priceChange1h > 0) score += Math.min(t.priceChange1h / 2, 15);
  // Liquidity
  if (t.liquidity > 100000) score += 10;
  else if (t.liquidity > 50000) score += 5;
  // Mcap sweet spot (150K-2M)
  if (t.mcap >= 150000 && t.mcap <= 2000000) score += 15;
  // Penalize low liquidity ratio
  if (t.liquidityWarning) score -= 15;
  return Math.round(score * 10) / 10;
}

async function main() {
  console.log('🔍 Scanning trending Solana tokens...');

  const [dexTokens, cgTokens] = await Promise.all([
    fetchDexScreenerTrending(),
    fetchCoinGeckoTrending()
  ]);

  console.log(`  DexScreener: ${dexTokens.length} tokens`);
  console.log(`  CoinGecko: ${cgTokens.length} tokens`);

  // Merge & deduplicate by address
  const seen = new Set();
  const all = [];
  for (const t of [...dexTokens, ...cgTokens]) {
    const key = t.address || t.token;
    if (seen.has(key)) continue;
    seen.add(key);
    all.push(t);
  }

  // Filter
  const filtered = all.filter(t =>
    t.mcap >= MIN_MCAP &&
    t.volume24h >= MIN_VOL_24H &&
    t.priceChange24h > 0
  );

  console.log(`  After filtering: ${filtered.length} tokens`);

  // Extra DD for small caps
  for (const t of filtered) {
    if (t.mcap < EXTRA_DD_THRESHOLD && t.address) {
      const info = await checkHolderInfo(t.address);
      Object.assign(t, info);
    }
  }

  // Score and rank
  const ranked = filtered.map(t => ({ ...t, score: scoreToken(t) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 15);

  const output = {
    scannedAt: new Date().toISOString(),
    totalScanned: all.length,
    totalFiltered: filtered.length,
    filters: { minMcap: MIN_MCAP, minVol24h: MIN_VOL_24H, priceChangePositive: true },
    shortlist: ranked
  };

  fs.writeFileSync(OUTPUT, JSON.stringify(output, null, 2));
  console.log(`✅ Wrote ${ranked.length} tokens to scan-results.json`);

  // Load rules from trades.json
  try {
    const trades = JSON.parse(fs.readFileSync(TRADES_JSON, 'utf8'));
    output.rules = trades.rules;
  } catch {}

  return output;
}

main().catch(e => { console.error('Scanner failed:', e); process.exit(1); });
