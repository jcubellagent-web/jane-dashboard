#!/usr/bin/env python3
"""
Drake Maye Hunt EP.7 - EPIC PURPLE PACK! 🔥
Jared Goff 9/25 EPIC pull!
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep7_new"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/530f46b7-a8b4-4d5e-af85-82645fa22bf8.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP7_EPIC_PACK.mp4"

# Original 37s → 30s (1.23x speed)
# Reveal order: Aaron Rodgers → Michael Penix Jr → Quinyon Mitchell → Jared Goff EPIC
# TIMING: Text appears 1 second AFTER card is fully visible!

TEXT_OVERLAYS = [
    # Title (0-5s) - EMPHASIZE THE EPIC PACK!
    (0, 5, "DRAKE MAYE HUNT EP.7", 50, 32, (255,255,255)),
    (0, 5, "⚡ EPIC PURPLE PACK ⚡", 95, 24, (180,100,255)),  # Purple for Epic!
    
    # Card 1: Michael Penix Jr - first card, reveals ~10s, text at 12-15s
    (12, 15, "Michael Penix Jr 377/397", 380, 24, (255,255,255)),
    (12, 15, "FLOOR: $2", 420, 20, (100,255,100)),
    
    # Card 2: Aaron Rodgers - reveals ~13s, text at 14-17s  
    (15, 18, "Aaron Rodgers 54/218", 380, 24, (255,255,255)),
    (15, 18, "FLOOR: $2", 420, 20, (100,255,100)),
    
    # Card 3: Quinyon Mitchell RARE - reveals ~19s, text at 20-23s
    (20, 23, "Quinyon Mitchell 49/99", 370, 26, (255,215,0)),
    (20, 23, "RARE - FLOOR: $4", 415, 22, (255,215,0)),
    
    # Card 4: JARED GOFF EPIC - THE BIG FINALE! reveals ~26s, text at 26-30s
    (26, 30, "JARED GOFF 9/25", 340, 32, (180,100,255)),  # Purple for Epic!
    (26, 30, "⚡ EPIC - FLOOR: $9 ⚡", 395, 28, (255,100,255)),  # Bright purple
    
    # Pack value at end (show during Goff reveal)
    (27, 30, "PACK VALUE: ~$17", 460, 20, (100,255,100)),
]

def create_text_png(text, filename, width=384, height=80, font_size=28, 
                    text_color=(255,255,255), stroke_width=3):
    """Create transparent PNG with styled text using Pillow"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
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
    
    # Draw stroke (black outline)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.7 - EPIC PURPLE PACK! 🔥")
    print("=" * 50)
    
    # 1. Create smooth base video - single speed change
    print("\n1. Creating smooth base video (single-pass 1.23x)...")
    
    base = f"{WORK_DIR}/smooth_base.mp4"
    
    # 37s → 30s = 1.233x speed, setpts = 0.81
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex',
        '[0:v]setpts=0.81*PTS[v];[0:a]atempo=1.23[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', 
        '-preset', 'slow',
        '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', '30',
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
    
    # 3. Composite overlays + music in one pass
    print("\n3. Compositing (high quality)...")
    
    inputs = ['-i', base]
    for pf, _, _, _ in png_data:
        inputs.extend(['-i', pf])
    inputs.extend(['-i', MUSIC])
    
    # Build overlay filter chain
    filters = []
    prev = '0:v'
    for i, (_, start, end, y) in enumerate(png_data):
        out = f'v{i}'
        filters.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    # Audio mixing
    music_idx = len(png_data) + 1
    filters.append(f"[{music_idx}:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.2[m]")
    filters.append(f"[0:a]volume=1.0[v]")
    filters.append(f"[v][m]amix=inputs=2:duration=first[a]")
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filters),
        '-map', f'[{prev}]', '-map', '[a]',
        '-c:v', 'libx264', 
        '-preset', 'slow',
        '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr[-500:]}")
        return
    
    # 4. Cleanup
    print("\n4. Cleanup...")
    for pf, _, _, _ in png_data:
        os.remove(pf) if os.path.exists(pf) else None
    os.remove(base) if os.path.exists(base) else None
    
    if os.path.exists(OUTPUT):
        sz = os.path.getsize(OUTPUT) / (1024*1024)
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                           '-of', 'default=noprint_wrappers=1:nokey=1', OUTPUT],
                          capture_output=True, text=True)
        final_dur = float(r.stdout.strip())
        
        print(f"\n{'='*50}")
        print(f"SUCCESS! 🔥")
        print(f"Output: {OUTPUT}")
        print(f"Size: {sz:.1f} MB | Duration: {final_dur:.1f}s")
        print(f"{'='*50}")
    else:
        print("FAILED!")

if __name__ == "__main__":
    main()
