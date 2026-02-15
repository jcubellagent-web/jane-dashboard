# ClawnX Evaluation

**Date:** 2026-02-14  
**Status:** Not Found / Does Not Exist  
**Time Spent:** ~8 minutes  

## Summary

**ClawnX does not exist as a publicly available package or repository.** After extensive searching across npm, GitHub, and web searches, no toolkit called "ClawnX" could be found.

## Search Attempts

1. **npm registry:** No packages matching "clawnx", "clawnX", or "clawn"
2. **GitHub search:** No repositories matching "ClawnX" or "clawnx"
3. **GitHub code search:** No README or code files mentioning ClawnX
4. **Web search:** Only found:
   - `clawn.ch` - A token launch platform for AI agents (not a Twitter SDK)
   - `clawenbot/clawnet` - A LinkedIn-like professional network for AI agents (not Twitter-related)
5. **MCP Registry:** No ClawnX listed among MCP servers
6. **Tweet source:** The referenced tweet (https://x.com/Clawnch_Bot/status/2022659943942222314) could not be accessed via web fetch (requires login)

## Possible Explanations

1. **Not yet released:** ClawnX might be in private development and not yet publicly available
2. **Different name:** The toolkit might exist under a different name than "ClawnX"
3. **Misidentified source:** The tweet might have been about a different tool or concept
4. **Very new:** Package might be so new it hasn't been indexed yet (unlikely given our search methods)

## Alternative X/Twitter Tools Found

During the search, I discovered several existing X/Twitter automation tools for AI agents:

### 1. **Infatoshi/x-mcp** ⭐ RECOMMENDED
- **Repo:** https://github.com/Infatoshi/x-mcp
- **Type:** MCP server for official X API
- **Features:** Post tweets, reply, quote, delete, search, read timeline, get mentions, like, retweet, upload media, analytics
- **Installation:** `npm install` + build, requires 5 X API credentials
- **API Requirements:** 
  - Consumer Key (API Key)
  - Secret Key (API Secret)
  - Bearer Token
  - Access Token
  - Access Token Secret
- **Permissions needed:** Read + Write (must be enabled in X Developer Portal)
- **Free tier compatibility:** ⚠️ **UNKNOWN** - Requires full API access, may not work with free tier posting-only access
- **Pros:**
  - Clean MCP interface
  - Works with Claude Code directly
  - Accepts tweet URLs or IDs
  - Full media upload support
  - Natural language interface
- **Cons:**
  - Requires paid X API access (likely)
  - More complex setup than browser automation
  - Need to manage 5 separate credentials

### 2. **nirholas/XActions**
- **Repo:** https://github.com/nirholas/XActions
- **Type:** Browser automation toolkit (no API needed)
- **Features:** MCP server, CLI, Node.js library, browser scripts
- **API Requirements:** None - works via browser automation
- **Free tier compatibility:** ✅ **YES** - No API needed at all
- **Pros:**
  - No API fees or access needed
  - MCP server included
  - CLI and SDK options
  - Open source, MIT license
- **Cons:**
  - Requires browser automation (similar to our current approach)
  - May not be more reliable than our custom solution

### 3. **ryanmac/agent-twitter-client-mcp**
- **Repo:** https://github.com/ryanmac/agent-twitter-client-mcp
- **Type:** MCP server using ElizaOS agent-twitter-client
- **Features:** Twitter integration without direct API access
- **Free tier compatibility:** ⚠️ **UNKNOWN** - Unclear how it works without API

## Evaluation vs Our Current Approach

### Our Current Setup
- ✅ Free tier API (post only)
- ✅ Browser automation (Playwright + CDP)
- ✅ Custom image upload hack (scripts/x-image-inject.js)
- ✅ Browser lock system for serialization
- ❌ Complex, fragile, requires browser maintenance
- ❌ Single-threaded (one browser task at a time)

### Would ClawnX (if it existed) be better?
**Cannot evaluate - ClawnX does not exist.**

### Would Infatoshi/x-mcp be better?
- **Likely NO for our use case:**
  - Requires full X API access (not just free tier)
  - Free tier only allows creating tweets, not reading/searching
  - x-mcp expects read/write/search permissions
  - More complex credential management
  - Probably won't work with our limited free tier access

### Would XActions be better?
- **Probably NO:**
  - Still uses browser automation (same underlying approach as us)
  - May not handle our specific image injection workflow
  - Our custom solution is already tailored to our needs
  - Adds another dependency layer

## Recommendation

**Keep our current browser-based approach for now.**

### Reasons:
1. **ClawnX doesn't exist** - cannot evaluate the promised solution
2. **Free tier limitations** - Official X API free tier only allows posting, not reading/searching
3. **MCP alternatives require more API access** - Infatoshi/x-mcp needs full API permissions we don't have
4. **Browser alternatives are similar** - XActions is also browser-based, not fundamentally different
5. **Our solution works** - Current setup successfully posts with images via browser automation
6. **Custom tailored** - Our x-image-inject.js is specifically designed for our workflow

### Future Considerations:
- If ClawnX becomes available, re-evaluate
- If we upgrade to paid X API ($200/month for Basic tier), Infatoshi/x-mcp becomes viable
- Monitor for simpler official API wrappers that support free tier
- Consider contributing to open source X API projects

## Cost Analysis

**Current approach:** $0 (browser automation + free tier API)  
**Infatoshi/x-mcp:** $200+/month (requires X API Basic tier minimum)  
**XActions:** $0 (browser automation, no API)  

**Verdict:** Stick with current approach unless we're willing to pay for X API access.

## Action Items

- [x] Search for ClawnX - NOT FOUND
- [x] Document alternatives
- [x] Evaluate compatibility with free tier
- [ ] Monitor for ClawnX release (if it ever happens)
- [ ] Re-evaluate if we upgrade X API tier

## References

- Infatoshi/x-mcp: https://github.com/Infatoshi/x-mcp
- XActions: https://github.com/nirholas/XActions
- Our current scripts: `scripts/x-image-inject.js`, browser lock system
- X API pricing: https://developer.x.com/en/portal/products/
