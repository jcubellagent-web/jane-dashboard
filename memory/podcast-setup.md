# Podcast Transcript Monitoring Setup

## Overview
Automated system to fetch and summarize podcast transcripts from YouTube using auto-generated captions (free).

**Setup Date:** February 14, 2026  
**Tool:** yt-dlp (installed via Homebrew)  
**Location:** `/Users/jc_agent/.openclaw/workspace/`

---

## Monitored Podcasts

### 1. All-In Podcast
- **Channel ID:** UCESLZhusAkFfsNsApnjF_Cg
- **Handle:** @allin
- **URL:** https://www.youtube.com/@allin
- **Hosts:** Chamath Palihapitiya, Jason Calacanis, David Sacks, David Friedberg
- **Publishing Schedule:** Weekly (typically Thursdays)
- **Topics:** Tech, markets, politics, AI, crypto, venture capital
- **Average Length:** ~90 minutes (~13,000 words)

### 2. Anthony Pompliano (The Pomp Podcast)
- **Channel ID:** UCevXpeL8cNyAnww-NqJ4m2w
- **Handle:** @AnthonyPompliano
- **URL:** https://www.youtube.com/@AnthonyPompliano
- **Host:** Anthony Pompliano
- **Publishing Schedule:** Daily (weekdays)
- **Topics:** Bitcoin, crypto, markets, investing, business
- **Average Length:** ~20-30 minutes (~4,000-6,000 words)

### 3. Unchained Podcast
- **Channel ID:** UCWiiMnsnw5Isc2PP1to9nNw
- **Handle:** @unchained (search: "Unchained Podcast Laura Shin")
- **URL:** Search-based discovery
- **Host:** Laura Shin
- **Publishing Schedule:** Weekly (Tuesdays)
- **Topics:** Crypto, DeFi, blockchain, regulation
- **Average Length:** ~45-60 minutes

### 4. This Week in Startups
- **Channel ID:** UC1UbgWkb41KrhF824U6t6uQ
- **Handle:** @thisweekinstartups
- **URL:** https://www.youtube.com/@thisweekinstartups
- **Host:** Jason Calacanis
- **Publishing Schedule:** Multiple times per week
- **Topics:** Startups, venture capital, tech news, founder interviews
- **Average Length:** ~45-90 minutes

### 5. The Daily (New York Times)
- **Channel ID:** UCkdnY2hNC0sdlVXPtWuNQ8g
- **Handle:** @thedaily (search: "The Daily NYT podcast")
- **URL:** Search-based discovery
- **Host:** Various NYT journalists
- **Publishing Schedule:** Daily (weekdays)
- **Topics:** News, politics, current events
- **Average Length:** ~20-30 minutes

---

## Scripts

### 1. Fetch Script: `scripts/fetch-podcast-transcripts.sh`

**Purpose:** Downloads the latest episode transcript for each podcast using YouTube auto-captions.

**Usage:**
```bash
bash scripts/fetch-podcast-transcripts.sh
```

**What it does:**
1. For each podcast, finds the latest video from their channel
2. Downloads English auto-generated captions (VTT format)
3. Cleans the captions (removes timestamps, formatting, duplicates)
4. Saves to `podcast-transcripts/YYYY-MM-DD-podcast-name.txt`
5. Adds metadata header (title, date, video link)

**Output Location:** `/Users/jc_agent/.openclaw/workspace/podcast-transcripts/`

**Output Format:**
```
===================================
Podcast: all-in
Title: Episode Title Here
Date: 2026-02-13
Video: https://youtube.com/watch?v=VIDEO_ID
===================================

Transcript text here...
```

### 2. Summary Script: `scripts/summarize-podcasts.sh`

**Purpose:** Extracts key topics and quotes from recent transcripts relevant to: AI, enterprise SaaS, crypto, markets, startups.

**Usage:**
```bash
bash scripts/summarize-podcasts.sh [days_back]

# Examples:
bash scripts/summarize-podcasts.sh 7   # Last 7 days (default)
bash scripts/summarize-podcasts.sh 30  # Last 30 days
```

**What it does:**
1. Scans transcript files from the last N days
2. Extracts sections containing keywords related to:
   - AI/ML (GPT, Claude, OpenAI, etc.)
   - Crypto (Bitcoin, Ethereum, DeFi, etc.)
   - Markets (IPO, M&A, funding, etc.)
   - Startups (venture, seed, founders, etc.)
3. Generates a markdown summary file

**Output:** `podcast-summary-YYYY-MM-DD.md`

**Keyword Categories:**
- **AI:** AI, artificial intelligence, machine learning, LLM, GPT, Claude, OpenAI, Anthropic
- **SaaS:** SaaS, enterprise software, B2B, cloud
- **Crypto:** crypto, bitcoin, ethereum, blockchain, defi, web3, NFT, token
- **Markets:** market, stock, equity, trading, valuation, IPO, M&A, acquisition
- **Startups:** startup, venture, funding, raise, seed, series, exit

---

## Workflow

### Daily Usage (Recommended)
```bash
# 1. Fetch latest episodes (run once per day)
bash scripts/fetch-podcast-transcripts.sh

# 2. Generate summary of recent content
bash scripts/summarize-podcasts.sh 7

# 3. Review summary file
cat podcast-summary-$(date +%Y-%m-%d).md
```

### Integration with Daily Threads / Newsletter
The summary output can be used to:
- Source talking points for daily X threads
- Find quotes for newsletter content
- Track emerging trends in AI/crypto/startups
- Identify topics for deep dives

---

## Limitations & Notes

### Known Limitations
1. **Auto-caption quality:** YouTube auto-captions are ~85-95% accurate; may contain errors
2. **Missing captions:** Some episodes may not have auto-captions enabled
3. **Rate limiting:** YouTube may throttle if fetching too frequently (respect their limits)
4. **Timing:** Transcripts only available after YouTube processes them (typically within hours of upload)

### Bash Version Compatibility
- Script uses Bash 3.2 compatible syntax (macOS default)
- Associative arrays NOT used (not available in Bash 3.2)
- Uses parallel arrays instead

### Dependencies
- **yt-dlp:** Installed via Homebrew (`brew install yt-dlp`)
- **Standard Unix tools:** sed, awk, grep, find
- **Deno:** Auto-installed by yt-dlp as dependency

### Troubleshooting

**Problem:** "Could not download auto-captions"
- **Solution:** Check if the video has captions enabled; try a different episode

**Problem:** "Channel not found"
- **Solution:** Verify the channel handle/ID is correct; some channels may have changed

**Problem:** Script hangs
- **Solution:** YouTube might be slow; increase timeout or check network connection

**Problem:** Empty transcript file
- **Solution:** The cleaning function may have filtered too aggressively; check raw VTT file

---

## Future Enhancements

### Potential Improvements
1. **Cron automation:** Schedule daily fetch (e.g., 6 AM daily)
2. **Deduplication:** Skip episodes already fetched
3. **Quality scoring:** Rate transcript quality and flag low-quality ones
4. **Topic extraction:** Use LLM to extract structured topics/insights
5. **Multi-language:** Support non-English podcasts
6. **RSS fallback:** For podcasts without good captions, fetch show notes from RSS
7. **Web search integration:** Cross-reference topics with news/research

### Integration Ideas
- **Pre-brief generation:** Auto-include in morning briefing
- **Thread generation:** Auto-generate draft X threads from key quotes
- **Newsletter sections:** "This week in podcasts" automated section
- **Trend tracking:** Track keyword frequency over time

---

## Testing Results

### Test Run: February 14, 2026
- **Podcasts tested:** All-In, Pomp
- **Success rate:** 2/2 (100%)
- **All-In transcript:** 13,513 words, 2026-02-13 episode
- **Pomp transcript:** 4,195 words, 2026-02-14 episode
- **Processing time:** ~46 seconds for 2 podcasts
- **Summary generation:** Successful, extracted AI, crypto, market, and startup topics

### Files Generated
```
podcast-transcripts/2026-02-13-all-in.txt (72KB)
podcast-transcripts/2026-02-14-pomp.txt (22KB)
podcast-summary-2026-02-14.md
```

---

## Maintenance

### Regular Tasks
- **Weekly:** Review transcript quality, verify all podcasts are fetching correctly
- **Monthly:** Check for channel handle/ID changes
- **Quarterly:** Update keyword lists based on emerging topics

### Update Channel Info
If a podcast changes its handle or you want to add/remove podcasts, edit:
```bash
scripts/fetch-podcast-transcripts.sh
```

Look for these arrays (lines 17-19):
```bash
PODCAST_NAMES=("all-in" "pomp" "unchained" "twis" "the-daily")
PODCAST_CHANNELS=("UCESLZhusAkFfsNsApnjF_Cg" ...)
PODCAST_HANDLES=("@allin" "@AnthonyPompliano" ...)
```

---

## Related Files
- **Transcripts:** `/Users/jc_agent/.openclaw/workspace/podcast-transcripts/`
- **Summaries:** `/Users/jc_agent/.openclaw/workspace/podcast-summary-*.md`
- **Scripts:** `/Users/jc_agent/.openclaw/workspace/scripts/`
  - `fetch-podcast-transcripts.sh`
  - `summarize-podcasts.sh`
  - `test-podcast-fetch.sh` (test version, 2 podcasts only)

---

**Last Updated:** February 14, 2026  
**Status:** ✅ Operational (tested successfully)
