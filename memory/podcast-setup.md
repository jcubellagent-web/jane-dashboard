# Podcast Transcript Monitoring Setup

## Overview
Automated podcast transcript pipeline using yt-dlp to fetch auto-generated captions from YouTube podcasts. Transcripts are stored locally and summarized for key topics: AI, enterprise SaaS, crypto, markets, and startups.

## Architecture
- **Fetch Script:** `scripts/fetch-podcast-transcripts.sh` — Downloads latest episode transcripts
- **Summary Script:** `scripts/summarize-podcasts.sh` — Extracts key topics from recent transcripts
- **Storage:** `podcast-transcripts/YYYY-MM-DD-podcast-name.txt`
- **Tool:** yt-dlp (installed at `/opt/homebrew/bin/yt-dlp`)

## Configuration
- Fetches auto-generated English captions only (`--write-auto-sub --sub-lang en`)
- Skips video download (`--skip-download`)
- Converts subtitles to plain text (removes timestamps, deduplicates)
- Only fetches latest 1-2 episodes per channel

## Monitored Podcasts (14 Total)

### Original 5 Podcasts (Operational since Feb 2026)
1. **All-In Podcast** (@allin)
   - Channel ID: `UCESLZhusAkFfsNsApnjF_Cg`
   - Handle: `@allin`
   - Focus: Tech, markets, politics, venture
   - Frequency: Weekly (~13k words)
   - Status: ✅ Operational

2. **Anthony Pompliano** (@AnthonyPompliano)
   - Channel ID: `UCevXpeL8cNyAnww-NqJ4m2w`
   - Handle: `@AnthonyPompliano`
   - Focus: Crypto, markets, finance
   - Frequency: Daily (~4-6k words)
   - Status: ✅ Operational

3. **Unchained** (@unchained)
   - Channel ID: `UCWiiMnsnw5Isc2PP1to9nNw`
   - Handle: `@unchained`
   - Focus: Crypto deep dives (Laura Shin)
   - Frequency: Weekly
   - Status: ✅ Operational

4. **This Week in Startups** (@thisweekinstartups)
   - Channel ID: `UC1UbgWkb41KrhF824U6t6uQ`
   - Handle: `@thisweekinstartups`
   - Focus: Startups, venture, tech
   - Frequency: Multiple/week
   - Status: ✅ Operational

5. **The Daily (NYT)** (@thedaily)
   - Channel ID: `UCkdnY2hNC0sdlVXPtWuNQ8g`
   - Handle: `@thedaily`
   - Focus: News, current events
   - Frequency: Daily
   - Status: ✅ Operational

### New 9 Podcasts (Added Feb 14, 2026)

6. **Acquired** (@AcquiredFM)
   - Channel ID: `UCyFqFYfTW2VoIQKylJ04Rtw`
   - Handle: `@AcquiredFM`
   - Focus: Tech company histories, M&A deep dives
   - Frequency: Weekly (long-form, 2-4 hours)
   - Status: ✅ Tested & Operational

7. **BG2 Pod** (@Bg2Pod)
   - Channel ID: `UC-yRDvpR99LUc5l7i7jLzew`
   - Handle: `@Bg2Pod`
   - Focus: Venture/public markets crossover (Bill Gurley & Brad Gerstner)
   - Frequency: Weekly
   - Status: ✅ Operational

8. **20VC with Harry Stebbings** (@20VC)
   - Channel ID: `UCf0PBRjhf0rF8fWBIxTuoWA`
   - Handle: `@20VC`
   - Focus: VC insights, funding rounds, startup ecosystem
   - Frequency: Multiple/week
   - Status: ✅ Tested & Operational

9. **Bankless** (@Bankless)
   - Channel ID: `UCAl9Ld79qaZxp9JzEOwd3aA`
   - Handle: `@Bankless`
   - Focus: Crypto, DeFi deep dives
   - Frequency: Multiple/week
   - Status: ✅ Tested & Operational

10. **Hard Fork** (@hardfork)
    - Channel ID: `UCZcR2SVWaGWNlMqPxvQS3vw`
    - Handle: `@hardfork`
    - Focus: Mainstream tech, AI policy (NYT, Kevin Roose + Casey Newton)
    - Frequency: Weekly
    - Status: ✅ Operational

11. **Turpentine VC** (@TurpentineVC)
    - Channel ID: `UCIiUCv0yvVGx2XYU4IJ2CKg`
    - Handle: `@TurpentineVC`
    - Focus: AI-native podcast network (Erik Torenberg)
    - Frequency: Multiple shows/week
    - Status: ✅ Operational

12. **The Prof G Pod – Scott Galloway** (@TheProfGPod)
    - Channel ID: `UC1E1SVcVyU3ntWMSQEp38Yw`
    - Handle: `@TheProfGPod`
    - Focus: Markets, big tech hot takes, business strategy
    - Frequency: Multiple/week
    - Status: ✅ Operational

13. **Lenny's Podcast** (@LennysPodcast)
    - Channel ID: `UC6t1O76G0jYXOAoYCm153dA`
    - Handle: `@LennysPodcast`
    - Focus: Product, growth, SaaS
    - Frequency: Weekly
    - Status: ✅ Operational

14. **Bloomberg Podcasts - Odd Lots** (@BloombergPodcasts)
    - Channel ID: `UChF5O40UBqAc82I7-i5ig6A`
    - Handle: `@BloombergPodcasts`
    - Focus: Macro/markets (Bloomberg)
    - Frequency: Multiple/week
    - Note: Channel hosts multiple Bloomberg podcasts; Odd Lots is primary target
    - Status: ✅ Operational

### Podcasts Not Added (No YouTube Channel)
- **Stratechery / Dithering** (Ben Thompson) — Subscription-based audio only, no regular YouTube channel

## Daily Workflow

```bash
# Fetch latest episodes from all 14 podcasts
bash scripts/fetch-podcast-transcripts.sh

# Generate summary of last 7 days
bash scripts/summarize-podcasts.sh 7

# Or specify different time window (e.g., 3 days)
bash scripts/summarize-podcasts.sh 3
```

## Output Format

### Transcript Files
```
podcast-transcripts/
├── 2026-02-14-acquired.txt
├── 2026-02-14-20vc.txt
├── 2026-02-14-bankless.txt
└── ...
```

Each transcript file includes:
- Podcast metadata (name, title, date, YouTube link)
- Plain text transcript (timestamps removed, deduplicated)
- Word count typically 4k-15k depending on episode length

### Summary Files
```
podcast-summary-2026-02-14.md
```

Summaries extract:
- 🤖 AI Topics
- ₿ Crypto Topics
- 📈 Markets & Business
- 🚀 Startup Topics

## Topics Extracted

### Primary Focus Areas
- **AI:** LLMs, OpenAI, Anthropic, Claude, GPT, machine learning, AI policy
- **Enterprise SaaS:** B2B software, cloud platforms, software companies
- **Crypto:** Bitcoin, Ethereum, DeFi, web3, NFTs, blockchain, Solana
- **Markets:** Valuations, IPOs, M&A, acquisitions, stock market, trading
- **Startups:** Venture funding, seed/series rounds, exits, founder stories

### Use Cases
- Daily X (Twitter) thread content
- Newsletter material (AI Breakfast, market commentary)
- Pre-brief reports for Josh
- Investment idea sourcing
- Trend identification

## Technical Details

### yt-dlp Flags
```bash
--write-auto-sub        # Download auto-generated captions
--sub-lang en           # English only
--skip-download         # Don't download video
--convert-subs srt      # Convert to SRT format
--playlist-end 2        # Only fetch last 1-2 episodes
```

### Subtitle Cleaning Process
1. Remove WEBVTT/SRT headers
2. Strip timestamps
3. Remove HTML tags
4. Deduplicate repeated lines
5. Add spacing between sentences

### Storage & Performance
- Average transcript: 50-200KB
- 14 podcasts × 1 episode ≈ 1-3MB total
- Fetch time: ~2-5 minutes for all podcasts
- Summary generation: ~10-30 seconds

## Maintenance Notes

### Adding New Podcasts
1. Find YouTube channel ID: `yt-dlp --print channel_id "ytsearch:PODCAST NAME"`
2. Get handle: `yt-dlp --playlist-end 1 --dump-json "https://www.youtube.com/channel/CHANNEL_ID/videos" | jq -r .uploader_id`
3. Add to arrays in `fetch-podcast-transcripts.sh`:
   - `PODCAST_NAMES+=(short-name)`
   - `PODCAST_CHANNELS+=(CHANNEL_ID)`
   - `PODCAST_HANDLES+=(@handle)`
4. Test manually first
5. Update this documentation

### Removing Podcasts
- Comment out or remove entries from all 3 arrays in parallel

### Troubleshooting
- **No captions:** Some videos lack auto-captions; script will skip with warning
- **Rate limiting:** yt-dlp handles this automatically with retries
- **Channel changes:** If handle changes, update PODCAST_HANDLES array

## History
- **Feb 14, 2026:** Expanded from 5 to 14 podcasts (added 9 new sources)
- **Feb 2026:** Initial setup with 5 podcasts (All-In, Pomp, Unchained, TWiS, The Daily)

## Future Enhancements
- [ ] Cron job for daily auto-fetch
- [ ] Semantic search over transcript archive
- [ ] Cross-reference trending topics across podcasts
- [ ] Integration with daily X thread generator
- [ ] Alerting for major funding/M&A announcements mentioned
