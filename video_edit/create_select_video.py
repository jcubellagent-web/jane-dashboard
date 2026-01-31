#!/usr/bin/env python3
"""
Create a polished TikTok video from the Select pack opening
- Add text overlays using PIL
- Add royalty-free background music
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Paths
INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/b9ab5dad-1a0d-4270-9c0f-81c28a1a5b52.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit"
OUTPUT_VIDEO = f"{WORK_DIR}/select_pack_final.mp4"
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
MUSIC_FILE = f"{WORK_DIR}/background_music2.mp3"

# Video dimensions
WIDTH = 384
HEIGHT = 848

def download_music():
    """Download royalty-free background music if not exists"""
    if not os.path.exists(MUSIC_FILE):
        print("Downloading background music...")
        subprocess.run(['curl', '-L', '-o', MUSIC_FILE, MUSIC_URL], check=True)
    return MUSIC_FILE

def create_text_overlay(text, filename, font_size=36, color=(255, 215, 0), bg_alpha=180, width=WIDTH, height=100):
    """Create a text overlay image with semi-transparent background"""
    # Create RGBA image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw semi-transparent background
    draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, bg_alpha))
    
    # Try to load a font, fall back to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with shadow
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 255))  # Shadow
    draw.text((x, y), text, font=font, fill=color + (255,))  # Main text
    
    img.save(filename)
    return filename

def create_video():
    print("Creating Select pack TikTok video...")
    
    # Download music
    music = download_music()
    
    # Create text overlays
    print("Creating text overlays...")
    
    # Top banner - gold text
    create_text_overlay(
        "$58 SELECT PACK RIP", 
        f"{WORK_DIR}/top_banner.png",
        font_size=32,
        color=(255, 215, 0),  # Gold
        height=80
    )
    
    # Middle text - white
    create_text_overlay(
        "2024 NFL TRADING CARDS", 
        f"{WORK_DIR}/mid_banner.png",
        font_size=24,
        color=(255, 255, 255),  # White
        height=60
    )
    
    # Bottom banner - highlight the hit
    create_text_overlay(
        "BUCKY IRVING ULTRA RARE 45/49", 
        f"{WORK_DIR}/bottom_banner.png",
        font_size=26,
        color=(255, 100, 100),  # Red/pink for Ultra Rare
        height=70
    )
    
    # Build ffmpeg command
    # Overlay text at different positions, mix in background music
    print("Building final video...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', INPUT_VIDEO,
        '-i', f"{WORK_DIR}/top_banner.png",
        '-i', f"{WORK_DIR}/mid_banner.png",
        '-i', f"{WORK_DIR}/bottom_banner.png",
        '-i', music,
        '-filter_complex',
        # Overlay top banner (0-full duration)
        '[0:v][1:v]overlay=0:30:enable=\'between(t,0,52)\'[v1];'
        # Overlay mid banner 
        '[v1][2:v]overlay=0:120:enable=\'between(t,0,52)\'[v2];'
        # Overlay bottom banner (show during reveal - from 25s onwards)
        '[v2][3:v]overlay=0:750:enable=\'between(t,25,52)\'[vout];'
        # Mix original audio with background music (music at 15% volume)
        '[0:a]volume=1.0[a1];'
        '[4:a]volume=0.15[a2];'
        '[a1][a2]amix=inputs=2:duration=first[aout]',
        '-map', '[vout]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-t', '52',  # Keep full duration
        '-movflags', '+faststart',
        OUTPUT_VIDEO
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    print(f"Video created: {OUTPUT_VIDEO}")
    return OUTPUT_VIDEO

if __name__ == "__main__":
    output = create_video()
    if output:
        # Get file size
        size = os.path.getsize(output) / (1024 * 1024)
        print(f"Output size: {size:.1f} MB")
