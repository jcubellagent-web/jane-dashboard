#!/usr/bin/env python3
"""
Drake Maye Super Bowl Hunt - THE FINALE!
He finally found Drake Maye! 9/10 EPIC!!!
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import glob

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
INPUT = "/Users/jc_agent/.openclaw/media/inbound/9e9fdcf1-a657-40e6-8eae-9f769b4d618b.mp4"
FRAMES_DIR = f"{WORK_DIR}/frames"
OUTPUT_DIR = f"{WORK_DIR}/output_frames"
FINAL = f"{WORK_DIR}/EP8_DRAKE_MAYE_FOUND.mp4"

# Video is 241s, speed up 4x to get ~60s final
SPEED = 4.0

# Pack timing (in ORIGINAL video seconds) and card data
PACKS = [
    {
        "reveal_start": 30,
        "reveal_end": 40,
        "highlight": "Andy Reid",
        "cards": [
            {"name": "A.J. Brown", "serial": "147/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Caleb Williams", "serial": "85/199", "rarity": "RARE", "floor": "$3"},
            {"name": "Kyle Pitts", "serial": "189/218", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Andy Reid", "serial": "37/49", "rarity": "ULTRA RARE", "floor": "$5"},
        ],
        "pack_value": "$10"
    },
    {
        "reveal_start": 55,
        "reveal_end": 75,
        "highlight": "Michael Penix Jr.",
        "is_mega": True,
        "cards": [
            {"name": "Rome Odunze", "serial": "21/25", "rarity": "EPIC", "floor": "$15"},
            {"name": "Michael Penix Jr.", "serial": "2/10", "rarity": "EPIC", "floor": "$30"},
            {"name": "DeMarvion Overshown", "serial": "200/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Grover Stewart", "serial": "11/25", "rarity": "EPIC", "floor": "$10"},
        ],
        "pack_value": "$56"
    },
    {
        "reveal_start": 85,
        "reveal_end": 95,
        "highlight": "Brock Bowers",
        "cards": [
            {"name": "Chris Jones", "serial": "185/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Jared Goff", "serial": "152/199", "rarity": "RARE", "floor": "$2"},
            {"name": "Kendrick Bourne", "serial": "210/218", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Brock Bowers", "serial": "3/25", "rarity": "EPIC", "floor": "$20"},
        ],
        "pack_value": "$24"
    },
    {
        "reveal_start": 120,
        "reveal_end": 130,
        "highlight": "Dre Greenlaw",
        "cards": [
            {"name": "Dre Greenlaw", "serial": "34/49", "rarity": "ULTRA RARE", "floor": "$4"},
            {"name": "Jameis Winston", "serial": "397/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Jordan Davis", "serial": "9/199", "rarity": "RARE", "floor": "$2"},
            {"name": "Alex Anzalone", "serial": "53/218", "rarity": "UNCOMMON", "floor": "$1"},
        ],
        "pack_value": "$8"
    },
    {
        "reveal_start": 190,
        "reveal_end": 200,
        "highlight": "Drake Maye",
        "is_drake": True,
        "cards": [
            {"name": "Joe Andreessen", "serial": "27/49", "rarity": "ULTRA RARE", "floor": "$4"},
            {"name": "Bucky Irving", "serial": "4/99", "rarity": "RARE", "floor": "$3"},
            {"name": "Deebo Samuel", "serial": "59/99", "rarity": "RARE", "floor": "$3"},
            {"name": "Drake Maye", "serial": "28/49", "rarity": "ULTRA RARE", "floor": "$15"},
        ],
        "pack_value": "$25"
    },
    {
        "reveal_start": 230,
        "reveal_end": 241,
        "highlight": "DRAKE MAYE",
        "is_finale": True,
        "cards": [
            {"name": "Malik Nabers", "serial": "198/397", "rarity": "UNCOMMON", "floor": "$1"},
            {"name": "Blake Corum", "serial": "119/199", "rarity": "RARE", "floor": "$2"},
            {"name": "Brock Purdy", "serial": "43/99", "rarity": "RARE", "floor": "$4"},
            {"name": "DRAKE MAYE", "serial": "9/10", "rarity": "EPIC", "floor": "$100+"},
        ],
        "pack_value": "$107+"
    },
]

def get_font(size):
    fonts = [
        "/System/Library/Fonts/SFNSText.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
    return ImageFont.load_default()

def get_text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def add_centered_text(draw, y, text, font, fill, width, outline_color=(0,0,0), outline_width=3):
    text_width = get_text_width(draw, text, font)
    x = (width - text_width) // 2
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill)

def add_glow_centered(draw, y, text, font, fill, glow_color, width, glow_radius=5):
    text_width = get_text_width(draw, text, font)
    x = (width - text_width) // 2
    for r in range(glow_radius, 0, -1):
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=fill)

def process_frame(frame_path, output_path, frame_num, fps, width, height):
    img = Image.open(frame_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # Calculate original video time from frame number (accounting for speed)
    original_time = frame_num / fps
    
    # Fonts
    title_font = get_font(48)
    subtitle_font = get_font(32)
    card_font = get_font(28)
    epic_font = get_font(42)
    value_font = get_font(36)
    
    # Colors
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    PURPLE = (180, 100, 255)
    GREEN = (100, 255, 100)
    RED = (255, 50, 50)
    CYAN = (50, 200, 255)
    EPIC_GLOW = (200, 100, 255)
    
    # INTRO: 0-8 seconds (original 0-32s)
    if original_time < 8:
        add_centered_text(draw, 40, "DRAKE MAYE HUNT", title_font, GOLD, width, outline_width=4)
        add_centered_text(draw, 100, "SUPER BOWL EDITION", subtitle_font, WHITE, width, outline_width=3)
        add_centered_text(draw, 150, "8 PACKS - $320", subtitle_font, GREEN, width, outline_width=3)
    
    # Find which pack we're in
    for i, pack in enumerate(PACKS):
        reveal_start = pack["reveal_start"] / SPEED
        reveal_end = pack["reveal_end"] / SPEED
        
        if reveal_start <= original_time < reveal_end:
            center_y = height // 2 - 100
            
            # FINALE - Drake Maye 9/10 EPIC
            if pack.get("is_finale"):
                add_glow_centered(draw, center_y - 80, "THE HUNT IS OVER!", epic_font, GOLD, (255, 200, 0), width, glow_radius=6)
                add_glow_centered(draw, center_y - 20, "DRAKE MAYE", epic_font, PURPLE, EPIC_GLOW, width, glow_radius=5)
                add_centered_text(draw, center_y + 40, "9/10 EPIC", card_font, PURPLE, width, outline_width=3)
                add_centered_text(draw, center_y + 80, "FLOOR: $100+", value_font, GREEN, width, outline_width=4)
                add_centered_text(draw, center_y + 130, "PACK VALUE: $107+", value_font, WHITE, width, outline_width=3)
            
            # First Drake Maye (Ultra Rare)
            elif pack.get("is_drake"):
                add_glow_centered(draw, center_y - 60, "DRAKE MAYE!", epic_font, CYAN, (50, 150, 200), width, glow_radius=4)
                add_centered_text(draw, center_y, "28/49 ULTRA RARE", card_font, CYAN, width, outline_width=3)
                add_centered_text(draw, center_y + 45, "FLOOR: $15", value_font, GREEN, width, outline_width=3)
                add_centered_text(draw, center_y + 95, f"PACK {i+1}: ~{pack['pack_value']}", subtitle_font, WHITE, width, outline_width=3)
            
            # Triple EPIC pack
            elif pack.get("is_mega"):
                add_glow_centered(draw, center_y - 60, "TRIPLE EPIC!", epic_font, PURPLE, EPIC_GLOW, width, glow_radius=4)
                add_centered_text(draw, center_y, "Penix Jr. 2/10", card_font, PURPLE, width, outline_width=3)
                add_centered_text(draw, center_y + 40, "Rome Odunze 21/25", card_font, PURPLE, width, outline_width=3)
                add_centered_text(draw, center_y + 85, "FLOOR: $56", value_font, GREEN, width, outline_width=3)
                add_centered_text(draw, center_y + 130, f"PACK {i+1}: ~{pack['pack_value']}", subtitle_font, WHITE, width, outline_width=3)
            
            # Regular packs with highlights
            else:
                highlight = pack.get("highlight", "")
                highlight_card = next((c for c in pack["cards"] if c["name"] == highlight), None)
                
                if highlight_card:
                    rarity = highlight_card["rarity"]
                    color = PURPLE if rarity == "EPIC" else CYAN if rarity == "ULTRA RARE" else WHITE
                    
                    add_centered_text(draw, center_y - 30, highlight, card_font, color, width, outline_width=3)
                    add_centered_text(draw, center_y + 15, highlight_card["serial"], card_font, WHITE, width, outline_width=3)
                    add_centered_text(draw, center_y + 55, f"FLOOR: {highlight_card['floor']}", value_font, GREEN, width, outline_width=3)
                    add_centered_text(draw, center_y + 100, f"PACK {i+1}: ~{pack['pack_value']}", subtitle_font, WHITE, width, outline_width=3)
            break
    
    # OUTRO: last 3 seconds
    if original_time >= 57:
        center_y = height // 2 + 50
        add_centered_text(draw, center_y - 50, "TOTAL VALUE: $240+", value_font, GREEN, width, outline_width=4)
        add_centered_text(draw, center_y, "COST: $320", subtitle_font, WHITE, width, outline_width=3)
        add_centered_text(draw, center_y + 45, "DRAKE MAYE 9/10 FOUND!", subtitle_font, GOLD, width, outline_width=3)
    
    img.convert("RGB").save(output_path, quality=95)

def main():
    os.chdir(WORK_DIR)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Extract frames from original video
    print("Step 1: Extracting frames...")
    subprocess.run([
        "ffmpeg", "-y", "-i", INPUT, "-q:v", "2", f"{FRAMES_DIR}/frame_%05d.jpg"
    ], capture_output=True)
    
    frames = sorted(glob.glob(f"{FRAMES_DIR}/frame_*.jpg"))
    total_frames = len(frames)
    print(f"Extracted {total_frames} frames")
    
    # Get dimensions
    first_frame = Image.open(frames[0])
    width, height = first_frame.size
    print(f"Video dimensions: {width}x{height}")
    
    # Calculate target frame count for sped-up video
    original_fps = total_frames / 241.0  # 241 second video
    target_fps = original_fps  # Keep same fps, just use fewer frames
    
    # Select every Nth frame for speedup
    frame_step = int(SPEED)
    selected_frames = frames[::frame_step]
    output_fps = original_fps
    
    print(f"Original FPS: {original_fps:.1f}, selecting every {frame_step}th frame")
    print(f"Output will have {len(selected_frames)} frames at {output_fps:.1f} fps = {len(selected_frames)/output_fps:.1f}s")
    
    print("Step 2: Adding overlays...")
    for i, frame_path in enumerate(selected_frames):
        if i % 100 == 0:
            print(f"  Processing frame {i}/{len(selected_frames)}")
        output_path = f"{OUTPUT_DIR}/frame_{i:05d}.jpg"
        process_frame(frame_path, output_path, i, output_fps, width, height)
    
    print("Step 3: Encoding final video...")
    
    # Try to use background music if available
    MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
    
    if os.path.exists(MUSIC):
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(output_fps),
            "-i", f"{OUTPUT_DIR}/frame_%05d.jpg",
            "-i", MUSIC,
            "-filter_complex", f"[1:a]volume=0.2,afade=t=out:st=57:d=3[music]",
            "-map", "0:v",
            "-map", "[music]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "60",
            "-shortest",
            FINAL
        ])
    else:
        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(output_fps),
            "-i", f"{OUTPUT_DIR}/frame_%05d.jpg",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-t", "60",
            FINAL
        ])
    
    print(f"Done! Created: {FINAL}")
    
    # Cleanup
    print("Cleaning up temp files...")
    subprocess.run(["rm", "-rf", FRAMES_DIR, OUTPUT_DIR])

if __name__ == "__main__":
    main()
