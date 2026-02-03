#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - FINAL WORKING VERSION
Title at start, pack summary at end - NO SPOILERS
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_FINAL.mp4"

# Text overlays - NO SPOILERS during reveals
TEXT_OVERLAYS = [
    # Title (0-4s)
    (0, 4, "DRAKE MAYE HUNT EP.8", 50, 38, (255,255,255)),
    (0, 4, "PATS TO THE SUPER BOWL", 105, 26, (255,215,0)),
    
    # Pack summary at END (28-30s) - all cards revealed by then
    (28, 30, "ULTRA RARE + EPIC!", 580, 30, (255,140,0)),
    (28, 30, "Dre Greenlaw 13/49 - $7", 640, 26, (255,80,80)),
    (28, 30, "Marquise Brown 3/10 - $15", 695, 26, (200,100,255)),
    (28, 30, "PACK VALUE: $24", 760, 30, (100,255,100)),
]

def create_text_png(text, filename, width=400, height=60, font_size=28, text_color=(255,255,255)):
    """Create transparent PNG with text"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    y = (height - (bbox[3] - bbox[1])) // 2
    
    # Black stroke for visibility
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=(0,0,0,255))
    
    draw.text((x, y), text, font=font, fill=text_color + (255,))
    img.save(filename, 'PNG')
    return True

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - FINAL VERSION")
    print("=" * 50)
    
    # Step 1: Create sped-up base video
    print("\n1. Creating base video (38s -> 30s)...")
    base = f"{WORK_DIR}/base_final.mp4"
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.79*PTS[v];[0:a]atempo=1.27[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', '30', base
    ], capture_output=True, text=True)
    
    if not os.path.exists(base):
        print(f"FAILED to create base: {result.stderr[-300:]}")
        sys.exit(1)
    print(f"   Base created: {os.path.getsize(base)//1024}KB")
    
    # Step 2: Create PNG overlays
    print("\n2. Creating text overlays...")
    png_files = []
    for i, (start, end, text, y, size, color) in enumerate(TEXT_OVERLAYS):
        pf = f"{WORK_DIR}/overlay_{i}.png"
        create_text_png(text, pf, font_size=size, text_color=color)
        png_files.append((pf, start, end, y))
        print(f"   [{start:2d}-{end:2d}s] {text}")
    
    # Step 3: Composite overlays with music
    print("\n3. Compositing video + overlays + music...")
    
    # Build inputs
    inputs = ['-i', base]
    for pf, _, _, _ in png_files:
        inputs.extend(['-i', pf])
    inputs.extend(['-i', MUSIC])
    
    # Build filter chain
    filters = []
    prev = '0:v'
    for i, (_, start, end, y) in enumerate(png_files):
        out = f'v{i}'
        filters.append(f"[{prev}][{i+1}:v]overlay=(W-w)/2:{y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    # Audio: mix original + music
    music_idx = len(png_files) + 1
    filters.append(f"[{music_idx}:a]afade=t=in:d=1,afade=t=out:st=28:d=2,volume=0.15[m]")
    filters.append(f"[0:a]volume=1.0[orig]")
    filters.append(f"[orig][m]amix=inputs=2:duration=first[aout]")
    
    filter_str = ';'.join(filters)
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_str,
        '-map', f'[{prev}]',
        '-map', '[aout]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        '-t', '30',
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr[-500:]}")
        sys.exit(1)
    
    # Step 4: Cleanup
    print("\n4. Cleaning up...")
    for pf, _, _, _ in png_files:
        if os.path.exists(pf):
            os.remove(pf)
    if os.path.exists(base):
        os.remove(base)
    
    # Verify output
    if os.path.exists(OUTPUT):
        size_mb = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {size_mb:.1f} MB")
        print(f"{'='*50}")
        return OUTPUT
    else:
        print("FAILED - no output file!")
        sys.exit(1)

if __name__ == "__main__":
    main()
