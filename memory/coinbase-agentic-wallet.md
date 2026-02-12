# Coinbase Agentic Wallet Setup

**Date:** Feb 11, 2026
**Status:** ⏳ Needs Josh's manual help for portal login

## What Happened
- Coinbase launched Agentic Wallets today (announced by Brian Armstrong)
- Tried to sign up/login at portal.cdp.coinbase.com with jcubellagent@gmail.com
- Account exists (password prompt appeared), but password JCAgent123!!! may have been wrong
- Coinbase login has aggressive anti-bot detection that keeps crashing browser tabs
- Cannot complete login via automated browser

## What Josh Needs to Do
1. Go to https://portal.cdp.coinbase.com
2. Log in with jcubellagent@gmail.com (may need to reset password if JCAgent123!!! doesn't work)
3. Create a new project (e.g., "Jane Agent")
4. Generate API keys (CDP API Key ID + Secret)
5. Save them to `.secrets/coinbase_agentic_wallet.txt`

## AgentKit Setup (once we have API keys)
From docs: https://docs.cdp.coinbase.com/agent-kit/getting-started/quickstart

```bash
npm create onchain-agent@latest
```

Options to select:
- Framework: LangChain or Vercel AI SDK
- Network: Base (Coinbase's L2)
- Wallet: CDP Smart Wallets or CDP Server Wallets

The .env-local file will need:
- CDP_API_KEY_ID
- CDP_API_KEY_SECRET

## Agentic Wallet Features (from today's launch)
- Pre-configured skills: authenticate, fund, send, trade, earn
- Session caps (max spend per session)
- Transaction size controls
- Enclave isolation (private keys never exposed to LLM)
- Works with any AI framework (LangChain, Eliza, Vercel AI SDK, etc.)
- Multi-network: EVM + Solana

## Links
- Docs: https://docs.cdp.coinbase.com/agent-kit/welcome
- GitHub: https://github.com/coinbase/agentkit
- Portal: https://portal.cdp.coinbase.com
- Discord: https://discord.com/invite/cdp
