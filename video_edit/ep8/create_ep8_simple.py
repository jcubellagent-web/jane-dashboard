#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - SIMPLE VERSION
Only show pack summary at the END to avoid spoilers
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/drake_maye_hunt_ep8_SIMPLE.mp4"

# Simple approach: Title at start, results at end ONLY
# No spoilers during reveals

TEXT_OVERLAYS = [
    # Title (0-4s)
    (0, 4, "DRAKE MAYE HUNT EP.8", 50, 36, (255,255,255)),
    (0, 4, "PATS TO THE SUPER BOWL", 100, 24, (255,215,0)),
    
    # Pack results at very end (28-30s) - ALL cards revealed by then
    (28, 30, "ULTRA RARE + EPIC PACK!", 600, 28, (255,140,0)),
    (28, 30, "Dre Greenlaw 13/49 - $7", 660, 24, (255,50,50)),
    (28, 30, "Marquise Brown 3/10 - $15", 710, 24, (200,50,255)),
    (28, 30, "PACK VALUE: $24", 770, 28, (100,255,100)),
]

def create_text_png(text, filename, width=400, height=70, font_size=28, 
                    text_color=(255,255,255), stroke_width=3):
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
    
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - SIMPLE (NO SPOILERS)")
    print("=" * 50)
    
    base = f"{WORK_DIR}/base.mp4"
    
    print("\n1. Creating base video...")
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.79*PTS[v];[0:a]atempo=1.27[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k', '-t', '30', base
    ], capture_output=True)
    
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', base],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    
    print("\n2. Creating overlays...")
    png_data = []
    for i, (start, end, text, y, size, color) in enumerate(TEXT_OVERLAYS):
        pf = f"{WORK_DIR}/txt_{i}.png"
        create_text_png(text, pf, font_size=size, text_color=color)
        png_data.append((pf, start, end, y))
        print(f"   [{start:2d}-{end:2d}s] {text}")
    
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
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
        OUTPUT
    ]
    
    subprocess.run(cmd, capture_output=True, text=True)
    
    for pf, _, _, _ in png_data:
        if os.path.exists(pf): os.remove(pf)
    if os.path.exists(base): os.remove(base)
    
    if os.path.exists(OUTPUT):
        sz = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {sz:.1f} MB")
        print("Title at start, results at end only - NO SPOILERS!")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
