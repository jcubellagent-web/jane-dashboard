# MEMORY.md - Long-Term Memory

_Distilled wisdom from daily experiences. Updated periodically._

---

## Trading

### First Memecoin Run (Feb 2026)
- **Result:** +$13.10 (+50.8%) across 3 positions
- **Lesson:** Taking profits works. WOJAK +52%, COPPERINU +131%, pippin -2%
- **Strategy validated:** "Moderately safe" tokens with strong community, 1-2 week holds

### Wallet
- Primary: `ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L`
- Jupiter wallet set to "never lock" - less friction for trading

---

## Integrations

### Sorare (Feb 2026)
- API authenticated, token valid until March 4, 2026
- GraphQL schema is complex - field names don't match documentation
- Key types: `NBACard`, `So5Lineup`, `So5Fixture`
- User slug: `jcubnft`, email: `jcubell16@gmail.com`

---

## Technical Lessons

### Jupiter API Trading (Feb 2026)
- **Lite API** (`lite-api.jup.ag`) - Free, no auth, use this
- **Main API** (`api.jup.ag`) - Requires API key from portal.jup.ag
- Registered with jcubellagent@gmail.com
- Script: `trading/jupiter-swap.js` - 3-5 sec vs 60-90 sec browser
- Jupiter wallet key ≠ Phantom seed phrase derivation

### Browser Automation
- Pixel-based automation unreliable (window sizes vary)
- Direct extension URLs work better: `chrome-extension://[id]/popup.html`
- Use CDP/browser control instead of simulating clicks

### Dashboard
- Layout presets via localStorage work well
- Separate mobile/desktop presets needed
- Sessions.json updated via heartbeat

---

## Josh Notes

- Prefers to be kept in the loop during long operations
- Heavy tasks should spawn sub-agents to keep main chat responsive
- First trading session together went well - trust established

---

_Last updated: 2026-02-02_
