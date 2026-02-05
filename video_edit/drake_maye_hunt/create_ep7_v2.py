#!/usr/bin/env python3
"""
Drake Maye Hunt EP.7 - BIGGER TEXT VERSION
3 Packs with text overlays - larger fonts, better centered
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import glob

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt"
INPUT = f"{WORK_DIR}/3packs_only_raw.mp4"
FRAMES_DIR = f"{WORK_DIR}/frames_v2"
OUTPUT_DIR = f"{WORK_DIR}/output_frames_v2"
FINAL = f"{WORK_DIR}/EP7_FINAL_V2.mp4"

# Pack data
PACKS = [
    {
        "reveal_time": 17,
        "highlight": "Romeo Doubs",
        "serial": "5/10",
        "rarity": "EPIC",
        "floor": "$15",
        "pack_value": "$19"
    },
    {
        "reveal_time": 35,
        "highlight": "Dallas Turner",
        "serial": "9/25",
        "rarity": "EPIC",
        "floor": "$12",
        "pack_value": "$18"
    },
    {
        "reveal_time": 52,
        "highlight": None,
        "pack_value": "$6"
    },
]

def get_font(size):
    """Get a system font"""
    fonts = [
        "/System/Library/Fonts/SFNSText.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
    return ImageFont.load_default()

def get_text_width(draw, text, font):
    """Get text width for centering"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def add_centered_text(draw, y, text, font, fill, width, outline_color=(0,0,0), outline_width=3):
    """Add centered text with thick outline"""
    text_width = get_text_width(draw, text, font)
    x = (width - text_width) // 2
    
    # Draw thick outline
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)

def add_glow_centered(draw, y, text, font, fill, glow_color, width, glow_radius=5):
    """Add centered text with glowing effect"""
    text_width = get_text_width(draw, text, font)
    x = (width - text_width) // 2
    
    # Draw glow layers
    for r in range(glow_radius, 0, -1):
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)

def process_frame(frame_path, output_path, frame_num, fps, width, height):
    """Add overlays to a single frame"""
    img = Image.open(frame_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    current_time = frame_num / fps
    
    # BIGGER FONTS
    title_font = get_font(52)       # Was 32
    subtitle_font = get_font(36)    # Was 20
    card_font = get_font(32)        # Was 18
    epic_font = get_font(44)        # Was 24
    floor_font = get_font(28)       # Was 16
    value_font = get_font(40)       # New size for values
    
    # Colors
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    PURPLE = (180, 100, 255)
    GREEN = (100, 255, 100)
    EPIC_GLOW = (200, 100, 255)
    
    # INTRO: 0-5 seconds - TOP AND CENTER
    if current_time < 5:
        add_centered_text(draw, 50, "DRAKE MAYE HUNT", title_font, GOLD, width, outline_width=4)
        add_centered_text(draw, 115, "EP. 7", title_font, WHITE, width, outline_width=3)
        add_centered_text(draw, 185, "2024 SELECT FOOTBALL", subtitle_font, WHITE, width, outline_width=3)
        add_centered_text(draw, 235, "3 PACKS - $105", subtitle_font, GREEN, width, outline_width=3)
    
    # Pack 1 reveal: ~17s - CENTER OF SCREEN
    if 17 <= current_time < 21:
        center_y = height // 2 - 80
        
        add_glow_centered(draw, center_y - 50, "EPIC PULL!", epic_font, PURPLE, EPIC_GLOW, width, glow_radius=4)
        add_centered_text(draw, center_y + 10, "ROMEO DOUBS", card_font, PURPLE, width, outline_width=3)
        add_centered_text(draw, center_y + 50, "5/10", card_font, WHITE, width, outline_width=3)
        add_centered_text(draw, center_y + 95, "FLOOR: $15", floor_font, GREEN, width, outline_width=3)
        add_centered_text(draw, center_y + 145, "PACK 1: ~$19", value_font, WHITE, width, outline_width=3)
    
    # Pack 2 reveal: ~35s - CENTER OF SCREEN
    if 35 <= current_time < 39:
        center_y = height // 2 - 80
        
        add_glow_centered(draw, center_y - 50, "EPIC PULL!", epic_font, PURPLE, EPIC_GLOW, width, glow_radius=4)
        add_centered_text(draw, center_y + 10, "DALLAS TURNER", card_font, PURPLE, width, outline_width=3)
        add_centered_text(draw, center_y + 50, "9/25", card_font, WHITE, width, outline_width=3)
        add_centered_text(draw, center_y + 95, "FLOOR: $12", floor_font, GREEN, width, outline_width=3)
        add_centered_text(draw, center_y + 145, "PACK 2: ~$18", value_font, WHITE, width, outline_width=3)
    
    # Pack 3 reveal: ~52s
    if 52 <= current_time < 55:
        center_y = height // 2 - 30
        add_centered_text(draw, center_y, "PACK 3: ~$6", value_font, WHITE, width, outline_width=3)
    
    # Outro: last 2 seconds - CENTER
    if current_time >= 53:
        center_y = height // 2 + 100
        add_centered_text(draw, center_y - 30, "TOTAL VALUE: ~$43", value_font, GREEN, width, outline_width=4)
        add_centered_text(draw, center_y + 30, "2 EPICS FROM $105!", subtitle_font, WHITE, width, outline_width=3)
    
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
    
    # Get frame count and dimensions
    frames = sorted(glob.glob(f"{FRAMES_DIR}/frame_*.jpg"))
    total_frames = len(frames)
    print(f"Extracted {total_frames} frames")
    
    # Get video dimensions
    first_frame = Image.open(frames[0])
    width, height = first_frame.size
    print(f"Video dimensions: {width}x{height}")
    
    fps = total_frames / 55.0
    print(f"Estimated FPS: {fps}")
    
    print("Step 2: Adding BIGGER overlays...")
    for i, frame_path in enumerate(frames):
        if i % 100 == 0:
            print(f"  Processing frame {i}/{total_frames}")
        output_path = f"{OUTPUT_DIR}/frame_{i:05d}.jpg"
        process_frame(frame_path, output_path, i, fps, width, height)
    
    print("Step 3: Encoding final video...")
    
    MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
    
    if os.path.exists(MUSIC):
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
    else:
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", f"{OUTPUT_DIR}/frame_%05d.jpg",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-t", "55",
            FINAL
        ])
    
    print(f"Done! Created: {FINAL}")
    
    # Cleanup
    print("Cleaning up temp files...")
    subprocess.run(["rm", "-rf", FRAMES_DIR, OUTPUT_DIR])

if __name__ == "__main__":
    main()
