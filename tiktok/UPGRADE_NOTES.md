# Video Upgrade Requirements (from Josh)

## Critical Avatar Fixes
1. **CIRCULAR frame** — crop mfer-9581.png into a circle (not square)
2. **Jaw-hinge mouth animation** — bottom half of mfer mouth opens/closes synced to voiceover audio
3. **BIGGER size** — at least 250-300px diameter, prominent in top-right

## Quality Improvements
1. Text padding: 80px+ margins on all sides
2. Scrolling/slide-in text animations (not just appearing)
3. Background ambient audio at ~15-20% volume
4. Bolder text with strong drop shadow/outline
5. Semi-transparent text background bars for readability

## Caption Fix (CRITICAL)
The upload script has been rewritten. Key changes:
- `type_caption()` uses `adb input text` with %s for spaces (NO keyevent combos)
- Hashtags now use TikTok's built-in Hashtag button (taps [42,715][289,799])
- No emojis in captions (adb can't type them — use text description instead)
- Previous bug: shift+keyevent doubled letters ("ppoovv" instead of "POV")
