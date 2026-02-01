#!/usr/bin/env python3
"""
Drake Maye Hunt EP.6 - SMOOTH VERSION
Single-pass processing for seamless playback
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep6_new"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/bb4cb1e3-c0f2-4eaa-8cd4-8ab51e8da7fa.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP6_SMOOTH_FINAL.mp4"

# Text overlays - TIMING FIXED to appear AFTER card reveals
# Original 38s video -> 30s (1.27x speed)
# Card reveal order: Mo Alie-Cox → Jalen Carter → DeVonta Smith → Anthony Richardson
# NOW WITH FLOOR PRICES from Panini Blockchain marketplace!
TEXT_OVERLAYS = [
    # Title (0-5s) - during pack intro
    (0, 5, "DRAKE MAYE HUNT EP.6", 50, 32, (255,255,255)),
    (0, 5, "2024 Panini Select", 95, 22, (255,215,0)),
    
    # Card 1: Mo Alie-Cox - reveals ~12s, show text 13-16s
    (13, 16, "Mo Alie-Cox 2/218", 380, 26, (255,255,255)),
    (13, 16, "FLOOR: $1", 430, 22, (100,255,100)),
    
    # Card 2: Jalen Carter - reveals ~17s, show text 18-21s
    (18, 21, "Jalen Carter 69/397", 380, 26, (255,255,255)),
    (18, 21, "FLOOR: $1", 430, 22, (100,255,100)),
    
    # Card 3: DeVonta Smith RARE - reveals ~22s, show text 23-26s
    (23, 26, "DeVonta Smith 84/199", 370, 26, (255,215,0)),
    (23, 26, "RARE - FLOOR: $2", 420, 22, (255,215,0)),
    
    # Card 4: Anthony Richardson ULTRA RARE - reveals ~27s, show text 27.5-30s
    (27, 30, "Anthony Richardson 7/49", 350, 30, (255,140,0)),
    (27, 30, "ULTRA RARE - FLOOR: $18", 405, 26, (255,0,0)),
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
    
    # Draw stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.6 - SMOOTH VERSION")
    print("=" * 50)
    
    # 1. Create smooth base video - single speed change, no choppy cuts
    print("\n1. Creating smooth base video (single-pass)...")
    
    base = f"{WORK_DIR}/smooth_base.mp4"
    
    # Gentle 1.27x speed to get 38s -> 30s, using high quality encoding
    # Using minterpolate for smoother motion
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex',
        '[0:v]setpts=0.79*PTS[v];[0:a]atempo=1.27[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', 
        '-preset', 'slow',  # Better quality
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
        '-movflags', '+faststart',  # Better streaming
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr[-300:]}")
        return
    
    # 4. Cleanup
    print("\n4. Cleanup...")
    for pf, _, _, _ in png_data:
        os.remove(pf) if os.path.exists(pf) else None
    os.remove(base) if os.path.exists(base) else None
    
    if os.path.exists(OUTPUT):
        sz = os.path.getsize(OUTPUT) / (1024*1024)
        # Get final duration
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                           '-of', 'default=noprint_wrappers=1:nokey=1', OUTPUT],
                          capture_output=True, text=True)
        final_dur = float(r.stdout.strip())
        
        print(f"\n{'='*50}")
        print(f"SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {sz:.1f} MB | Duration: {final_dur:.1f}s")
        print(f"{'='*50}")
    else:
        print("FAILED!")

if __name__ == "__main__":
    main()
