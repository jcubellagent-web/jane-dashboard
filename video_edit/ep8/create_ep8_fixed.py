#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - FIXED TIMING
Correct reveal order: Tip Reiman → Howie Long → Dre Greenlaw → Marquise Brown
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/drake_maye_hunt_ep8_FIXED.mp4"

# CORRECTED TIMING - verified from actual sped-up video frames
# Reveal times in sped-up video: ~11s, ~20s, ~24s, ~27s
# Text appears 1-2 seconds AFTER reveal

TEXT_OVERLAYS = [
    # Title (0-5s)
    (0, 5, "DRAKE MAYE HUNT EP.8", 50, 36, (255,255,255)),
    (0, 5, "PATS TO THE SUPER BOWL", 100, 24, (255,215,0)),
    
    # Card 1: TIP REIMAN - reveals ~11s, text 12-15s
    (12, 15, "Tip Reiman 210/218", 680, 28, (255,255,255)),
    (12, 15, "UNCOMMON - FLOOR: $1", 730, 22, (100,255,100)),
    
    # Card 2: HOWIE LONG - reveals ~20s, text 21-24s  
    (21, 24, "Howie Long 185/397", 680, 28, (255,255,255)),
    (21, 24, "UNCOMMON - FLOOR: $1", 730, 22, (100,255,100)),
    
    # Card 3: DRE GREENLAW ULTRA RARE - reveals ~24s, text 25-27s
    (25, 27, "Dre Greenlaw 13/49", 660, 32, (255,140,0)),
    (25, 27, "ULTRA RARE - FLOOR: $7", 720, 26, (255,50,50)),
    
    # Card 4: MARQUISE BROWN EPIC - reveals ~27s, text 28-30s
    (28, 30, "Marquise Brown 3/10", 640, 34, (200,50,255)),
    (28, 30, "EPIC - FLOOR: $15", 700, 28, (200,50,255)),
    
    # Pack total at end
    (29, 30, "PACK VALUE: $24", 780, 26, (100,255,100)),
]

def create_text_png(text, filename, width=384, height=80, font_size=28, 
                    text_color=(255,255,255), stroke_width=3):
    """Create transparent PNG with styled text"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
               "/System/Library/Fonts/SFNS.ttf",
               "/System/Library/Fonts/Helvetica.ttc"]:
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
    
    # Stroke for visibility
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - FIXED TIMING")
    print("=" * 50)
    print("\nCORRECT reveal order:")
    print("  1. Tip Reiman (~11s) → text 12-15s")
    print("  2. Howie Long (~20s) → text 21-24s")
    print("  3. Dre Greenlaw UR (~24s) → text 25-27s")
    print("  4. Marquise Brown Epic (~27s) → text 28-30s")
    
    # 1. Create base video
    print("\n1. Creating base video (38s → 30s)...")
    base = f"{WORK_DIR}/base.mp4"
    
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex',
        '[0:v]setpts=0.79*PTS[v];[0:a]atempo=1.27[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', '30', base
    ], capture_output=True)
    
    if not os.path.exists(base):
        print("Failed to create base!")
        return
    
    # Get duration
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', base],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    print(f"   Duration: {dur:.1f}s")
    
    # 2. Create PNGs
    print("\n2. Creating text overlays...")
    png_data = []
    for i, (start, end, text, y, size, color) in enumerate(TEXT_OVERLAYS):
        pf = f"{WORK_DIR}/txt_{i}.png"
        create_text_png(text, pf, font_size=size, text_color=color)
        png_data.append((pf, start, end, y))
        print(f"   [{start:2d}-{end:2d}s] {text}")
    
    # 3. Composite
    print("\n3. Compositing...")
    inputs = ['-i', base]
    for pf, _, _, _ in png_data:
        inputs.extend(['-i', pf])
    inputs.extend(['-i', MUSIC])
    
    filters = []
    prev = '0:v'
    for i, (_, start, end, y) in enumerate(png_data):
        out = f'v{i}'
        filters.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    music_idx = len(png_data) + 1
    filters.append(f"[{music_idx}:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.2[m]")
    filters.append(f"[0:a]volume=1.0[v]")
    filters.append(f"[v][m]amix=inputs=2:duration=first[a]")
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filters),
        '-map', f'[{prev}]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr[-500:]}")
        import shutil
        shutil.copy(base, OUTPUT)
    
    # 4. Cleanup
    print("\n4. Cleanup...")
    for pf, _, _, _ in png_data:
        if os.path.exists(pf): os.remove(pf)
    if os.path.exists(base): os.remove(base)
    
    if os.path.exists(OUTPUT):
        sz = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {sz:.1f} MB")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
