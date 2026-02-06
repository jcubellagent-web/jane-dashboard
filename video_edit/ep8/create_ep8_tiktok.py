#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - 12 PACK OPENING 
TikTok Edit - Condensed to 60 seconds with floor prices
EPIC FINALE: Drake Maye 9/10 valued at $19,000!
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/9e9fdcf1-a657-40e6-8eae-9f769b4d618b.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_DRAKE_MAYE_HUNT_FINAL.mp4"

# Video is 240s -> 60s = 4x speed factor
# So original timestamps / 4 = final timestamps
SPEED_FACTOR = 4.0  # 240s / 60s

# EPIC PULLS with floor prices from Panini Blockchain marketplace
# Original timestamp -> Sped up timestamp (divide by 4)
# Xavien Howard: 105s -> 26s
# Brock Bowers: 90s -> 22s
# Michael Penix Jr: 65s -> 16s
# Rome Odunze: 55s -> 14s
# Drake Maye: 235s -> 59s (FINALE!)

# Card reveals discovered in video (original timestamps):
# Pack 1: ~25-40s (first reveals)
# Pack 2: ~50-70s (includes epics: Rome Odunze 21/25, Grover Stewart 11/25, Michael Penix 2/10!)
# Pack 3: ~75-95s (Brock Bowers 3/25)
# Pack 4: ~100-120s (Xavien Howard 10/25)
# Pack 5-11: Various reveals
# Pack 12: ~230-240s (DRAKE MAYE 9/10 FINALE!)

TEXT_OVERLAYS = [
    # Title (0-4s) - during pack intro
    (0, 4, "DRAKE MAYE HUNT EP.8", 50, 32, (255,255,255)),
    (0, 4, "12-Pack Opening - $480 Cost", 95, 20, (255,215,0)),
    
    # Rome Odunze EPIC 21/25 - at ~14s (55/4)
    (13, 17, "Rome Odunze 21/25", 350, 28, (255,140,0)),
    (13, 17, "EPIC - FLOOR: ~$15", 400, 24, (255,0,100)),
    
    # Michael Penix Jr. EPIC 2/10 - at ~16s (65/4)  
    (16, 21, "MICHAEL PENIX JR 2/10", 330, 32, (255,215,0)),
    (16, 21, "EPIC PULL - ~$500!", 385, 28, (255,0,0)),
    
    # Brock Bowers EPIC 3/25 - at ~22s (90/4)
    (21, 26, "Brock Bowers 3/25", 350, 28, (255,140,0)),
    (21, 26, "EPIC ROOKIE TE - ~$100", 400, 24, (255,0,100)),
    
    # Xavien Howard EPIC 10/25 - at ~26s (105/4)
    (25, 30, "Xavien Howard 10/25", 350, 28, (255,140,0)),
    (25, 30, "EPIC - FLOOR: ~$8", 400, 24, (100,255,100)),
    
    # Build anticipation for finale
    (50, 54, "LAST PACK...", 200, 36, (255,255,255)),
    (50, 54, "12 packs down to 1", 260, 22, (200,200,200)),
    
    # DRAKE MAYE FINALE - at ~59s (235/4)
    (55, 60, "DRAKE MAYE 9/10", 300, 40, (255,215,0)),
    (55, 60, "EPIC - $19,000!!!", 360, 34, (255,0,0)),
    (55, 60, "hunting for more Drake Maye", 420, 20, (255,255,255)),
    (55, 60, "cards before the Super Bowl", 450, 20, (255,255,255)),
    
    # Total value outro (last 3 seconds)
    (57, 60, "PACK VALUE: ~$19,700+", 500, 26, (100,255,100)),
    (57, 60, "COST: $480 | PROFIT: 4000%!", 540, 22, (255,215,0)),
]

def create_text_png(text, filename, width=384, height=100, font_size=28, 
                    text_color=(255,255,255), stroke_width=3):
    """Create transparent PNG with styled text using Pillow"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/System/Library/Fonts/Supplemental/Impact.ttf",
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
    
    # Draw stroke/outline for visibility
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 60)
    print("DRAKE MAYE HUNT EP.8 - 12 PACK OPENING")
    print("TikTok Edit with Floor Prices")
    print("=" * 60)
    
    # 1. Create sped-up base video - 240s -> 60s (4x speed)
    print("\n1. Creating base video (4x speed: 240s -> 60s)...")
    
    base = f"{WORK_DIR}/base_4x.mp4"
    
    # Use setpts for video speed and atempo for audio
    # 4x speed = setpts=0.25*PTS, but atempo max is 2x so chain two
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
        return
    
    # Get actual duration
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', base],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    print(f"   Base duration: {dur:.1f}s")
    
    # 2. Create PNG overlays
    print("\n2. Creating text overlays...")
    png_data = []
    for i, (start, end, text, y, size, color) in enumerate(TEXT_OVERLAYS):
        pf = f"{WORK_DIR}/txt_{i}.png"
        create_text_png(text, pf, font_size=size, text_color=color)
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
        filters.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    # Audio mixing
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
        print(f"Error: {result.stderr[-500:]}")
        # Try simpler version without music
        print("\n   Retrying without music mixing...")
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
        print(f"EPIC PULLS:")
        print(f"  - Michael Penix Jr. 2/10 EPIC: ~$500")
        print(f"  - Rome Odunze 21/25 EPIC: ~$15")
        print(f"  - Brock Bowers 3/25 EPIC: ~$100")
        print(f"  - Xavien Howard 10/25 EPIC: ~$8")
        print(f"  - DRAKE MAYE 9/10 EPIC: $19,000!!!")
        print(f"")
        print(f"TOTAL PACK VALUE: ~$19,700+")
        print(f"PACK COST: $480 (12 x $40)")
        print(f"PROFIT: ~4000%!")
        print(f"{'='*60}")
        return True
    else:
        print("FAILED to create video!")
        return False

if __name__ == "__main__":
    main()
