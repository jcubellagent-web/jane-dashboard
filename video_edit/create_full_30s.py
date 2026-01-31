#!/usr/bin/env python3
"""
Create a 30-second TikTok video - FULL VIDEO, nothing cut
Speed up everything to fit, louder music
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/b9ab5dad-1a0d-4270-9c0f-81c28a1a5b52.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit"
OUTPUT_VIDEO = f"{WORK_DIR}/select_pack_full_30s.mp4"
MUSIC_FILE = f"{WORK_DIR}/background_music2.mp3"

WIDTH = 384
HEIGHT = 848

def create_text_overlay(text, filename, font_size=36, color=(255, 215, 0), bg_alpha=180, width=WIDTH, height=100):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, bg_alpha))
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), text, font=font, fill=color + (255,))
    
    img.save(filename)
    return filename

def create_video():
    print("Creating FULL 30-second video (nothing cut, just sped up)...")
    
    # Create text overlays
    print("Creating text overlays...")
    
    create_text_overlay(
        "$58 SELECT PACK RIP", 
        f"{WORK_DIR}/top_banner.png",
        font_size=32,
        color=(255, 215, 0),
        height=80
    )
    
    create_text_overlay(
        "4 HITS - EPIC + ULTRA RARE", 
        f"{WORK_DIR}/bottom_banner.png",
        font_size=24,
        color=(255, 100, 100),
        height=70
    )
    
    # Strategy: Variable speed to fit 52s into ~30s
    # Total original: 52 seconds -> target 30 seconds
    # 
    # Segment breakdown (in original time):
    # 0-5s: Pack screen + buy -> speed 3x = ~1.7s output
    # 5-12s: Pack opening animation -> speed 3x = ~2.3s output  
    # 12-17s: 4-card rarity reveal + Goff loading -> speed 2.5x = ~2s output
    # 17-24s: Goff reveal -> speed 1.5x = ~4.7s output
    # 24-32s: Loading + Jayden Daniels -> speed 2x = ~4s output
    # 32-42s: Bucky Irving reveal (ULTRA RARE!) -> speed 1.3x = ~7.7s output
    # 42-48s: A.J. Brown reveal (EPIC!) -> speed 1.3x = ~4.6s output
    # 48-52s: Final 4/4 screen -> speed 1.5x = ~2.7s output
    # Total output: ~29.7s
    
    segments = [
        (0, 5, 3.0),       # Pack screen - fast
        (5, 12, 3.0),      # Opening animation - fast
        (12, 17, 2.5),     # 4-card screen + loading - fast
        (17, 24, 1.5),     # Goff reveal - medium
        (24, 32, 2.0),     # Loading + Jayden - medium fast
        (32, 42, 1.3),     # Bucky Irving (ULTRA RARE) - slower, important!
        (42, 48, 1.3),     # A.J. Brown (EPIC) - slower, important!
        (48, 52, 1.5),     # Final screen - medium
    ]
    
    segment_files = []
    
    for i, (start, end, speed) in enumerate(segments):
        seg_file = f"{WORK_DIR}/seg_{i}.mp4"
        segment_files.append(seg_file)
        
        pts_factor = 1.0 / speed
        
        # Build atempo chain for speeds > 2.0
        if speed <= 2.0:
            atempo_filter = f"atempo={speed}"
        else:
            # Chain atempo filters (each max 2.0)
            atempo_filter = f"atempo=2.0,atempo={speed/2.0}"
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start),
            '-t', str(end - start),
            '-i', INPUT_VIDEO,
            '-filter_complex',
            f"[0:v]setpts={pts_factor}*PTS[v];[0:a]{atempo_filter}[a]",
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-c:a', 'aac',
            seg_file
        ]
        
        print(f"Segment {i+1}: {start}s-{end}s at {speed}x...")
        subprocess.run(cmd, capture_output=True)
    
    # Concat all segments
    concat_file = f"{WORK_DIR}/concat_full.txt"
    with open(concat_file, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    temp_video = f"{WORK_DIR}/temp_full.mp4"
    print("Concatenating all segments...")
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        temp_video
    ], capture_output=True)
    
    # Get duration
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', temp_video
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())
    print(f"Video duration: {duration:.1f}s")
    
    # Add overlays and LOUDER background music
    print("Adding overlays and LOUDER music...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', f"{WORK_DIR}/top_banner.png",
        '-i', f"{WORK_DIR}/bottom_banner.png",
        '-i', MUSIC_FILE,
        '-filter_complex',
        # Top banner throughout
        f'[0:v][1:v]overlay=0:30:enable=\'between(t,0,{duration})\'[v1];'
        # Bottom banner in last 10 seconds (showing all hits)
        f'[v1][2:v]overlay=0:750:enable=\'between(t,{duration-10},{duration})\'[vout];'
        # Mix audio - LOUDER music (0.35 instead of 0.12)
        '[0:a]volume=0.8[a1];'
        '[3:a]volume=0.35[a2];'
        '[a1][a2]amix=inputs=2:duration=first[aout]',
        '-map', '[vout]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        OUTPUT_VIDEO
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    # Cleanup
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    for f in [temp_video, concat_file]:
        if os.path.exists(f):
            os.remove(f)
    
    print(f"Video created: {OUTPUT_VIDEO}")
    return OUTPUT_VIDEO

if __name__ == "__main__":
    output = create_video()
    if output:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
            '-of', 'default=noprint_wrappers=1', output
        ], capture_output=True, text=True)
        print(result.stdout)
