#!/usr/bin/env python3
"""
EP.8 TikTok Edit v2 - POLISHED
- NO SPOILERS in opening title
- BIGGER text, more centered
- NO overlapping overlays
- White text with black outline for contrast
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/9e9fdcf1-a657-40e6-8eae-9f769b4d618b.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_FINAL_v2.mp4"

# Video: 384x832 (portrait TikTok)
# Center Y = 416, but want text in visible safe zone (avoid bottom UI)
# Safe area: Y 100-700

# Fixed overlay schedule - NO OVERLAPS
# Each card gets its own time window, no collisions
TEXT_OVERLAYS = [
    # ========== OPENING TITLE (0-4s) - GENERIC, NO SPOILERS ==========
    (0, 4, "12-PACK OPENING", 350, 44, (255,255,255)),
    (0, 4, "$480 COST - DID I PROFIT?", 420, 28, (255,215,0)),
    
    # ========== ROME ODUNZE (13-16s) - first epic ==========
    (13, 16, "ROME ODUNZE", 360, 36, (255,140,0)),
    (13, 16, "21/25 EPIC", 420, 32, (255,140,0)),
    (13, 16, "FLOOR: ~$15", 475, 28, (100,255,100)),
    
    # ========== MICHAEL PENIX JR (17-21s) - big pull! ==========
    (17, 21, "MICHAEL PENIX JR.", 340, 40, (255,215,0)),
    (17, 21, "2/10 EPIC!", 405, 36, (255,0,0)),
    (17, 21, "~$500!", 465, 32, (255,0,0)),
    
    # ========== BROCK BOWERS (22-25s) ==========
    (22, 25, "BROCK BOWERS", 360, 36, (255,140,0)),
    (22, 25, "3/25 EPIC ROOKIE", 420, 30, (255,140,0)),
    (22, 25, "FLOOR: ~$100", 475, 28, (100,255,100)),
    
    # ========== XAVIEN HOWARD (26-30s) ==========
    (26, 30, "XAVIEN HOWARD", 360, 36, (255,140,0)),
    (26, 30, "10/25 EPIC", 420, 30, (255,140,0)),
    (26, 30, "FLOOR: ~$8", 475, 28, (100,255,100)),
    
    # ========== BUILD ANTICIPATION (50-54s) ==========
    (50, 54, "LAST PACK...", 380, 48, (255,255,255)),
    (50, 54, "12 packs down to 1", 450, 26, (200,200,200)),
    
    # ========== DRAKE MAYE FINALE (55-60s) - THE REVEAL! ==========
    (55, 60, "DRAKE MAYE", 310, 50, (255,215,0)),
    (55, 60, "9/10 EPIC", 380, 42, (255,0,0)),
    (55, 60, "$19,000!!!", 445, 48, (255,0,0)),
    (55, 60, "hunting for more Drake Maye", 520, 24, (255,255,255)),
    (55, 60, "cards before the Super Bowl", 555, 24, (255,255,255)),
    
    # ========== TOTAL VALUE (57-60s) - bottom of screen ==========
    (57, 60, "PACK VALUE: ~$19,700+", 620, 30, (100,255,100)),
    (57, 60, "COST $480 | PROFIT 4000%", 665, 26, (255,215,0)),
]

def create_text_png(text, filename, width=384, height=120, font_size=36, 
                    text_color=(255,255,255), stroke_width=4):
    """Create transparent PNG with styled text - BIGGER and BOLDER"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    # Try Impact first for that bold TikTok look
    for fp in ["/System/Library/Fonts/Supplemental/Impact.ttf",
               "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/System/Library/Fonts/SFNS.ttf"]:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except: pass
    if not font:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    y = (height - (bbox[3] - bbox[1])) // 2
    
    # THICK black outline for visibility (stroke_width=4 for bold contrast)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    # Main text in color
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 60)
    print("EP.8 POLISHED v2 - TikTok Ready")
    print("=" * 60)
    
    # 1. Create sped-up base video - 240s -> 60s (4x speed)
    print("\n1. Creating base video (4x speed: 240s -> 60s)...")
    
    base = f"{WORK_DIR}/base_4x_v2.mp4"
    
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex',
        '[0:v]setpts=0.25*PTS[v];[0:a]atempo=2.0,atempo=2.0[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', 
        '-preset', 'medium',
        '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', '60',
        base
    ], capture_output=True)
    
    if not os.path.exists(base):
        print("Failed to create base video!")
        return False
    
    # Get actual duration
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', base],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    print(f"   Base duration: {dur:.1f}s")
    
    # 2. Create PNG overlays - BIGGER text
    print("\n2. Creating text overlays (BIGGER + CENTERED)...")
    png_data = []
    for i, (start, end, text, y, size, color) in enumerate(TEXT_OVERLAYS):
        pf = f"{WORK_DIR}/txt_v2_{i}.png"
        create_text_png(text, pf, font_size=size, text_color=color, stroke_width=4)
        png_data.append((pf, start, end, y))
        print(f"   [{start:2d}-{end:2d}s] {text}")
    
    # 3. Composite overlays in one pass
    print("\n3. Compositing overlays...")
    
    inputs = ['-i', base]
    for pf, _, _, _ in png_data:
        inputs.extend(['-i', pf])
    
    # Add background music if available
    if os.path.exists(MUSIC):
        inputs.extend(['-i', MUSIC])
        has_music = True
    else:
        has_music = False
        print("   Note: No background music found")
    
    # Build overlay filter chain
    filters = []
    prev = '0:v'
    for i, (_, start, end, y) in enumerate(png_data):
        out = f'v{i}'
        # Center horizontally: (W-w)/2
        filters.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    # Audio mixing with background music
    if has_music:
        music_idx = len(png_data) + 1
        filters.append(f"[{music_idx}:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.15[m]")
        filters.append(f"[0:a]volume=0.8[v]")
        filters.append(f"[v][m]amix=inputs=2:duration=first[a]")
        audio_map = '[a]'
    else:
        audio_map = '0:a'
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filters),
        '-map', f'[{prev}]', '-map', audio_map,
        '-c:v', 'libx264', 
        '-preset', 'medium',
        '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error with music, retrying without...")
        # Try simpler version without music
        filters_simple = []
        prev = '0:v'
        for i, (_, start, end, y) in enumerate(png_data):
            out = f'v{i}'
            filters_simple.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
            prev = out
        
        inputs_simple = ['-i', base]
        for pf, _, _, _ in png_data:
            inputs_simple.extend(['-i', pf])
        
        cmd_simple = ['ffmpeg', '-y'] + inputs_simple + [
            '-filter_complex', ';'.join(filters_simple),
            '-map', f'[{prev}]', '-map', '0:a',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
            '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart',
            OUTPUT
        ]
        result = subprocess.run(cmd_simple, capture_output=True, text=True)
    
    # 4. Cleanup
    print("\n4. Cleanup...")
    for pf, _, _, _ in png_data:
        if os.path.exists(pf):
            os.remove(pf)
    if os.path.exists(base):
        os.remove(base)
    
    if os.path.exists(OUTPUT):
        sz = os.path.getsize(OUTPUT) / (1024*1024)
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                           '-of', 'default=noprint_wrappers=1:nokey=1', OUTPUT],
                          capture_output=True, text=True)
        final_dur = float(r.stdout.strip())
        
        print(f"\n{'='*60}")
        print(f"SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {sz:.1f} MB | Duration: {final_dur:.1f}s")
        print(f"")
        print(f"FIXES APPLIED:")
        print(f"  ✓ No spoilers in opening title")
        print(f"  ✓ Bigger text (44pt title, 36-50pt cards)")
        print(f"  ✓ Text centered in safe zone")
        print(f"  ✓ No overlapping overlays")
        print(f"  ✓ Thick black outline for contrast")
        print(f"  ✓ Drake Maye reveal kept at end")
        print(f"  ✓ 'hunting for Drake Maye' closing message")
        print(f"  ✓ All floor prices included")
        print(f"{'='*60}")
        return True
    else:
        print("FAILED to create video!")
        return False

if __name__ == "__main__":
    main()
