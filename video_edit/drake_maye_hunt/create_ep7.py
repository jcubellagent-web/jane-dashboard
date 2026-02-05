#!/usr/bin/env python3
"""
Drake Maye Hunt EP.7 - Professional TikTok Edit
3 Packs with text overlays and EPIC callouts
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import glob

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt"
INPUT = f"{WORK_DIR}/3packs_only_raw.mp4"
FRAMES_DIR = f"{WORK_DIR}/frames"
OUTPUT_DIR = f"{WORK_DIR}/output_frames"
FINAL = f"{WORK_DIR}/EP7_FINAL.mp4"

# Video info: 50.6 seconds at ~55.7 fps after our cut
# Pack timings in the raw 55 second video:
# Pack 1: ~12-17s (Romeo Doubs 5/10 EPIC)
# Pack 2: ~30-35s (Dallas Turner 9/25 EPIC)  
# Pack 3: ~48-52s (Jimmy Graham etc)

# Card data with floor prices (estimated)
PACKS = [
    {
        "reveal_time": 17,  # seconds when 4/4 shown
        "cards": [
            {"name": "Theo Johnson", "serial": "41/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Stefon Diggs", "serial": "104/199", "rarity": "RARE", "floor": "$2"},
            {"name": "Romeo Doubs", "serial": "5/10", "rarity": "EPIC", "floor": "$15"},
            {"name": "Nakobe Dean", "serial": "63/218", "rarity": "UNCOMMON", "floor": "$1"},
        ],
        "highlight": "Romeo Doubs"
    },
    {
        "reveal_time": 35,
        "cards": [
            {"name": "Antonio Gibson", "serial": "350/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Antonio Gibson", "serial": "125/199", "rarity": "RARE", "floor": "$2"},
            {"name": "DeMarcus Ware", "serial": "20/99", "rarity": "RARE", "floor": "$3"},
            {"name": "Dallas Turner", "serial": "9/25", "rarity": "EPIC", "floor": "$12"},
        ],
        "highlight": "Dallas Turner"
    },
    {
        "reveal_time": 52,
        "cards": [
            {"name": "Jimmy Graham", "serial": "71/79", "rarity": "RARE", "floor": "$2"},
            {"name": "Jordan Davis", "serial": "34/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Marquise Brown", "serial": "46/199", "rarity": "RARE", "floor": "$2"},
            {"name": "Chris Long", "serial": "111/218", "rarity": "UNCOMMON", "floor": "$1"},
        ],
        "highlight": None
    },
]

def get_font(size, bold=False):
    """Get a system font"""
    fonts = [
        "/System/Library/Fonts/SFNSText.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
    return ImageFont.load_default()

def add_text_with_outline(draw, pos, text, font, fill, outline_color=(0,0,0), outline_width=2):
    """Add text with outline for visibility"""
    x, y = pos
    # Draw outline
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    # Draw main text
    draw.text(pos, text, font=font, fill=fill)

def add_glow_text(draw, pos, text, font, fill, glow_color, glow_radius=4):
    """Add text with glowing effect"""
    x, y = pos
    # Draw glow layers
    for r in range(glow_radius, 0, -1):
        alpha = int(100 / r)
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    # Draw main text
    draw.text(pos, text, font=font, fill=fill)

def process_frame(frame_path, output_path, frame_num, fps=55.7):
    """Add overlays to a single frame"""
    img = Image.open(frame_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    current_time = frame_num / fps
    
    # Fonts
    title_font = get_font(32, bold=True)
    subtitle_font = get_font(20)
    card_font = get_font(18)
    epic_font = get_font(24, bold=True)
    floor_font = get_font(16)
    
    # Colors
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    PURPLE = (180, 100, 255)
    GREEN = (100, 255, 100)
    EPIC_GLOW = (200, 100, 255)
    
    # INTRO: 0-5 seconds
    if current_time < 5:
        # Title
        add_text_with_outline(draw, (width//2 - 140, 30), "DRAKE MAYE HUNT", title_font, GOLD, outline_width=3)
        add_text_with_outline(draw, (width//2 - 50, 70), "EP. 7", title_font, WHITE, outline_width=2)
        add_text_with_outline(draw, (width//2 - 80, 110), "2024 Select Football", subtitle_font, WHITE, outline_width=2)
        add_text_with_outline(draw, (width//2 - 55, 140), "3 PACKS - $105", subtitle_font, GREEN, outline_width=2)
    
    # Pack 1 reveal: ~17s - show for 4 seconds
    if 17 <= current_time < 21:
        pack = PACKS[0]
        y_pos = height - 200
        
        # EPIC callout for Romeo Doubs (no emojis)
        add_glow_text(draw, (width//2 - 70, y_pos - 60), "EPIC PULL!", epic_font, PURPLE, EPIC_GLOW, glow_radius=3)
        add_text_with_outline(draw, (width//2 - 100, y_pos - 30), "ROMEO DOUBS 5/10", card_font, PURPLE, outline_width=2)
        add_text_with_outline(draw, (width//2 - 50, y_pos), "Floor: $15", floor_font, GREEN, outline_width=2)
        
        # Pack value
        add_text_with_outline(draw, (width//2 - 60, y_pos + 30), "PACK 1: ~$19", subtitle_font, WHITE, outline_width=2)
    
    # Pack 2 reveal: ~35s - show for 4 seconds
    if 35 <= current_time < 39:
        pack = PACKS[1]
        y_pos = height - 200
        
        # EPIC callout for Dallas Turner (no emojis)
        add_glow_text(draw, (width//2 - 70, y_pos - 60), "EPIC PULL!", epic_font, PURPLE, EPIC_GLOW, glow_radius=3)
        add_text_with_outline(draw, (width//2 - 100, y_pos - 30), "DALLAS TURNER 9/25", card_font, PURPLE, outline_width=2)
        add_text_with_outline(draw, (width//2 - 50, y_pos), "Floor: $12", floor_font, GREEN, outline_width=2)
        
        # Pack value
        add_text_with_outline(draw, (width//2 - 60, y_pos + 30), "PACK 2: ~$18", subtitle_font, WHITE, outline_width=2)
    
    # Pack 3 reveal: ~52s - show for 3 seconds
    if 52 <= current_time < 55:
        y_pos = height - 150
        add_text_with_outline(draw, (width//2 - 60, y_pos), "PACK 3: ~$6", subtitle_font, WHITE, outline_width=2)
    
    # Outro: last 2 seconds
    if current_time >= 53:
        y_pos = height - 80
        add_text_with_outline(draw, (width//2 - 80, y_pos - 30), "TOTAL VALUE: ~$43", subtitle_font, GREEN, outline_width=2)
        add_text_with_outline(draw, (width//2 - 90, y_pos), "COST: $105 - 2 EPICs!", subtitle_font, WHITE, outline_width=2)
    
    # Save
    img.convert("RGB").save(output_path, quality=95)

def main():
    os.chdir(WORK_DIR)
    
    # Create directories
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Step 1: Extracting frames...")
    subprocess.run([
        "ffmpeg", "-y", "-i", INPUT, "-q:v", "2", f"{FRAMES_DIR}/frame_%05d.jpg"
    ], capture_output=True)
    
    # Get frame count
    frames = sorted(glob.glob(f"{FRAMES_DIR}/frame_*.jpg"))
    total_frames = len(frames)
    print(f"Extracted {total_frames} frames")
    
    # Calculate FPS
    fps = total_frames / 55.0  # 55 second raw video
    print(f"Estimated FPS: {fps}")
    
    print("Step 2: Adding overlays...")
    for i, frame_path in enumerate(frames):
        if i % 100 == 0:
            print(f"  Processing frame {i}/{total_frames}")
        output_path = f"{OUTPUT_DIR}/frame_{i:05d}.jpg"
        process_frame(frame_path, output_path, i, fps)
    
    print("Step 3: Encoding final video with background music...")
    
    MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
    
    # Combine frames with background music (lowered volume)
    # Mix background music at 20% volume, no original audio needed for pack openings
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{OUTPUT_DIR}/frame_%05d.jpg",
        "-i", MUSIC,
        "-filter_complex", "[1:a]volume=0.25,afade=t=out:st=52:d=3[music]",
        "-map", "0:v",
        "-map", "[music]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "-t", "55",
        "-shortest",
        FINAL
    ])
    
    print(f"Done! Created: {FINAL}")
    
    # Cleanup
    print("Cleaning up temp files...")
    subprocess.run(["rm", "-rf", FRAMES_DIR, OUTPUT_DIR])

if __name__ == "__main__":
    main()
