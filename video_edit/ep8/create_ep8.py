#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - Video Creator
Ultra Rare + Epic Pack!
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Paths
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
OUTPUT = os.path.join(WORK_DIR, "drake_maye_hunt_ep8.mp4")

# Video specs
ORIGINAL_DURATION = 38.4  # seconds
TARGET_DURATION = 30  # seconds
SPEED_FACTOR = ORIGINAL_DURATION / TARGET_DURATION  # 1.28x
PTS_FACTOR = 1 / SPEED_FACTOR  # 0.78

# Card reveals in ORIGINAL timing
# Format: (original_reveal_time, player, serial, rarity, floor_price)
CARDS = [
    (10, "Howie Long", "185/397", "UNCOMMON", 1),
    (14, "Dre Greenlaw", "13/49", "ULTRA RARE", 7),
    (22, "Tip Reiman", "210/218", "UNCOMMON", 1),
    (34, "Marquise Brown", "3/10", "EPIC", 15),
]

PACK_COST = 60
PACK_VALUE = sum(c[4] for c in CARDS)  # $24

def orig_to_sped(t):
    """Convert original timestamp to sped-up timestamp"""
    return t / SPEED_FACTOR

# Text overlays: (start, end, text, y_pos, font_size, color)
# Text appears 1 second AFTER reveal in sped-up time
TEXT_OVERLAYS = [
    # Title (first 5 seconds)
    (0, 5, "DRAKE MAYE HUNT EP.8", 50, 36, (255,255,255)),
    (0, 5, "🏈 PATS TO THE SUPER BOWL", 100, 24, (255,215,0)),
    
    # Card 1: Howie Long - reveals ~8s sped up, text at 9s
    (9, 12, "Howie Long 185/397", 380, 28, (255,255,255)),
    (9, 12, "UNCOMMON - FLOOR: $1", 420, 22, (100,255,100)),
    
    # Card 2: Dre Greenlaw ULTRA RARE - reveals ~11s, text at 12s
    (12, 16, "Dre Greenlaw 13/49", 360, 32, (255,140,0)),
    (12, 16, "🔥 ULTRA RARE - FLOOR: $7", 410, 26, (255,0,0)),
    
    # Card 3: Tip Reiman - reveals ~17s, text at 18s
    (18, 21, "Tip Reiman 210/218", 380, 28, (255,255,255)),
    (18, 21, "UNCOMMON - FLOOR: $1", 420, 22, (100,255,100)),
    
    # Card 4: Marquise Brown EPIC - reveals ~27s, text at 28s
    (27, 30, "Marquise Brown 3/10", 340, 34, (160,32,240)),
    (27, 30, "🔥🔥 EPIC - FLOOR: $15", 395, 28, (160,32,240)),
    
    # Pack total at end
    (28, 30, f"PACK VALUE: ${PACK_VALUE}", 460, 26, (100,255,100)),
    (28, 30, "NO DRAKE MAYE... THE HUNT CONTINUES!", 510, 20, (255,255,255)),
]

def create_text_overlay(text, font_size, color, width=1080, height=100):
    """Create a transparent PNG with text"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a bold font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text size and center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    
    # Draw text with shadow for visibility
    shadow_color = (0, 0, 0, 200)
    draw.text((x+2, 12), text, font=font, fill=shadow_color)
    draw.text((x, 10), text, font=font, fill=(*color, 255))
    
    return img

def main():
    os.chdir(WORK_DIR)
    
    print("🎬 Creating Drake Maye Hunt EP.8...")
    print(f"   Pack contents: Ultra Rare + Epic!")
    print(f"   Pack value: ${PACK_VALUE} vs ${PACK_COST} cost")
    
    # Step 1: Speed up video (single pass for smoothness)
    print("\n1️⃣ Speeding up video...")
    sped_up = os.path.join(WORK_DIR, "sped_up.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex',
        f'[0:v]setpts={PTS_FACTOR}*PTS[v];[0:a]atempo={SPEED_FACTOR}[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-t', '30',
        sped_up
    ], capture_output=True)
    
    # Step 2: Create text overlay PNGs
    print("2️⃣ Creating text overlays...")
    overlay_files = []
    for i, (start, end, text, y_pos, font_size, color) in enumerate(TEXT_OVERLAYS):
        img = create_text_overlay(text, font_size, color)
        png_path = os.path.join(WORK_DIR, f"overlay_{i:02d}.png")
        img.save(png_path)
        overlay_files.append((start, end, png_path, y_pos))
    
    # Step 3: Build FFmpeg filter for overlays
    print("3️⃣ Applying overlays...")
    
    # Build complex filter
    inputs = ['-i', sped_up]
    for _, _, png, _ in overlay_files:
        inputs.extend(['-i', png])
    
    filter_parts = []
    current = "[0:v]"
    
    for i, (start, end, _, y_pos) in enumerate(overlay_files):
        next_label = f"[v{i}]"
        # Center horizontally, position at y_pos
        filter_parts.append(
            f"{current}[{i+1}:v]overlay=(W-w)/2:{y_pos}:enable='between(t,{start},{end})'{next_label}"
        )
        current = next_label
    
    filter_complex = ";".join(filter_parts)
    
    # Final encode
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', current[1:-1],  # Remove brackets
        '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', '30',
        OUTPUT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg error: {result.stderr[:500]}")
        # Fallback: just output sped up version
        print("   Using sped-up version without overlays...")
        import shutil
        shutil.copy(sped_up, OUTPUT)
    
    print(f"\n✅ Video created: {OUTPUT}")
    print(f"   Duration: 30 seconds")
    print(f"   Cards: Ultra Rare Dre Greenlaw + Epic Marquise Brown")
    
    # Cleanup
    print("\n🧹 Cleaning up temp files...")
    for f in overlay_files:
        try:
            os.remove(f[2])
        except:
            pass
    try:
        os.remove(sped_up)
    except:
        pass
    
    return OUTPUT

if __name__ == "__main__":
    main()
