# Pack Opening Video Workflow

## Drake Maye Hunt Series - @degencollector TikTok

**SUCCESSFULLY POSTED: EP.6 on Feb 1, 2026**

---

### TL;DR - The Winning Formula

1. **Watch raw video first** → map exact card reveal timestamps
2. **Fetch floor prices** from Panini marketplace (MANDATORY)
3. **Text appears 1 second AFTER card reveals** (never spoil the reveal!)
4. **Single-pass 1.27x speed** for smooth 30s video (not segment splicing)
5. **Caption hook**: "watch to the end to see if I profit on the $X pack!"
6. **Upload → delete old drafts → notify Josh to post**

---

### Complete Process

#### 1. Receive Raw Video
- Josh sends raw pack opening video via WhatsApp
- Save to workspace (lands in `~/.openclaw/media/inbound/`)
- Note: Raw videos are typically 35-40 seconds

#### 2. Analyze Video Timing (CRITICAL STEP)
**Extract frames to map EXACT card reveal moments:**
```bash
# Extract frames every 2-3 seconds from original video
ffmpeg -i source.mp4 -vf "fps=0.5" orig_%02ds.png
```

**Watch for these visual cues:**
- Pack unopened (cards face-down)
- Individual card flip animation starts
- Card FULLY VISIBLE (player name readable) ← This is the reveal moment
- Card moves to collection view

**Document timing like this:**
```
Original (38s) → Sped-up (30s at 1.27x)
- Mo Alie-Cox reveals at 15s → ~12s sped up
- Jalen Carter reveals at 21s → ~17s sped up  
- DeVonta Smith reveals at 28s → ~22s sped up
- Anthony Richardson reveals at 34s → ~27s sped up
```

#### 3. Get Floor Prices from Panini Blockchain
**THIS IS MANDATORY FOR EVERY VIDEO**

**URL Pattern:**
```
https://nft.paniniamerica.net/marketplace/nfts.html?card_view_type=club&sortBy=price_asc&list_type=listed&sport=Football&product_name=PLAYER%20NAME
```

**Tip:** Sort by `price_asc` to see floor price first.

**Rarity Price Guide (rough estimates):**
- Common (#/799+) → $1-2
- Uncommon (#/200-500) → $1-3
- Rare (#/99-199) → $2-10
- Ultra Rare (#/49) → $10-50+
- Epic (#/10-25) → $20-100+
- Legendary (#/1-5) → $100-1000+

#### 4. Create Video Script

**Golden Rule: Text appears 1 SECOND AFTER the card is fully visible**
- If card reveals at 12s, text shows at 13s
- This prevents spoiling the reveal!

**TEXT_OVERLAYS Template:**
```python
TEXT_OVERLAYS = [
    # Title (first 5 seconds during pack intro)
    (0, 5, "DRAKE MAYE HUNT EP.X", 50, 32, (255,255,255)),
    (0, 5, "2024 Panini Select", 95, 22, (255,215,0)),
    
    # Each card: (start_sec, end_sec, text, y_position, font_size, color_rgb)
    # start = reveal_time + 1, end = start + 3
    
    # Common/Uncommon cards - white text
    (13, 16, "Player Name serial", 380, 26, (255,255,255)),
    (13, 16, "FLOOR: $X", 430, 22, (100,255,100)),
    
    # Rare cards - gold text
    (23, 26, "Player Name serial", 370, 26, (255,215,0)),
    (23, 26, "RARE - FLOOR: $X", 420, 22, (255,215,0)),
    
    # Ultra Rare - orange/red for emphasis
    (27, 30, "Player Name serial", 350, 30, (255,140,0)),
    (27, 30, "ULTRA RARE - FLOOR: $X", 405, 26, (255,0,0)),
]
```

**Color Palette:**
- White: `(255,255,255)` - Standard cards
- Gold: `(255,215,0)` - Rare cards
- Orange: `(255,140,0)` - Ultra Rare title
- Red: `(255,0,0)` - Ultra Rare emphasis
- Green: `(100,255,100)` - Floor prices (always green!)

#### 5. Video Processing

**Key Settings for Smooth Playback:**
```python
# Single-pass speed adjustment (38s → 30s = 1.27x)
# DO NOT splice segments - causes choppiness!
subprocess.run([
    'ffmpeg', '-y', '-i', SOURCE,
    '-filter_complex',
    '[0:v]setpts=0.79*PTS[v];[0:a]atempo=1.27[a]',
    '-map', '[v]', '-map', '[a]',
    '-c:v', 'libx264', 
    '-preset', 'slow',  # Better quality
    '-crf', '18',       # High quality
    '-t', '30',
    output
])
```

**Text Rendering:** Use Pillow (PIL), not ImageMagick
- ImageMagick often lacks Freetype font support on macOS
- Pillow renders text reliably with system fonts

#### 6. Verify Timing Before Upload
```bash
# Extract frames from the OUTPUT video to verify
ffmpeg -i EP6_SMOOTH_FINAL.mp4 -vf "select='eq(n\,390)+eq(n\,420)+eq(n\,510)'" -vsync vfr verify_%02d.png
```
Check that:
- Text does NOT appear while card is face-down
- Text shows AFTER the card flip completes
- Floor prices are legible (green on dark background)

#### 7. Upload & Caption

**Caption Formula:**
```
DRAKE MAYE HUNT EP.X - watch to the end to see if I profit on the $XX pack!

#drakemaye #panininfts #nftcollector #footballcards #packopening 
#[featured_player] #paniniblockchain #sportscards #nfl #patriots
```

**Why this works:**
- "watch to the end" = engagement hook (TikTok rewards watch time)
- "$XX pack" = sets stakes without revealing outcome
- Don't put pack value in caption - let viewers discover it!

#### 8. Cleanup
- Delete all old drafts from TikTok (keep only latest version)
- Delete intermediate files from workspace:
  ```bash
  trash *.png concat_list.txt overlays.ass  # temp files
  # Keep: final video + working script for reference
  ```

---

### Lessons Learned

| Issue | Solution |
|-------|----------|
| Text appears before card reveals (spoiler!) | Time text to start 1 second AFTER card is fully visible |
| Video looks choppy | Use single-pass speed adjustment, not segment splicing |
| Text not rendering | Use Pillow instead of ImageMagick |
| Caption kills suspense | Use "watch to the end" hook, don't reveal pack value |
| Too many drafts | Delete old versions before notifying Josh |

---

### File Structure
```
~/.openclaw/workspace/video_edit/
├── PACK_OPENING_WORKFLOW.md  (this file)
├── background_music.mp3
├── ep5_new/
├── ep6_new/
│   ├── EP6_SMOOTH_FINAL.mp4  (posted!)
│   └── create_ep6_smooth.py  (reference script)
└── ep7_new/  (future)
```

---

### Episode History

| EP | Date Posted | Pack Cost | Pack Value | Highlight Card | Notes |
|----|-------------|-----------|------------|----------------|-------|
| 6  | Feb 1, 2026 | $60 | ~$22 | Anthony Richardson 7/49 UR ($18) | First with floor prices! |

---

*Last updated: February 1, 2026 - After EP.6 posted successfully*
