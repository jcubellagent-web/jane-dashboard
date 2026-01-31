#!/usr/bin/env python3
"""
Create a 30-second TikTok video from the Select pack opening
- Speed up intro/loading parts
- Keep card reveals at good pace
- Highlight the Bucky Irving Ultra Rare hit
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Paths
INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/b9ab5dad-1a0d-4270-9c0f-81c28a1a5b52.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit"
OUTPUT_VIDEO = f"{WORK_DIR}/select_pack_30s.mp4"
MUSIC_FILE = f"{WORK_DIR}/background_music2.mp3"

# Video dimensions
WIDTH = 384
HEIGHT = 848

def create_text_overlay(text, filename, font_size=36, color=(255, 215, 0), bg_alpha=180, width=WIDTH, height=100):
    """Create a text overlay image with semi-transparent background"""
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
    print("Creating 30-second Select pack video...")
    
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
        "BUCKY IRVING ULTRA RARE", 
        f"{WORK_DIR}/bottom_banner.png",
        font_size=26,
        color=(255, 100, 100),
        height=70
    )
    
    # Strategy: Create segments with different speeds, then concat
    # Segment 1: 0-8s (intro + pack animation) -> speed up 2.5x -> ~3.2s
    # Segment 2: 8-18s (4-card screen + Goff reveal) -> speed up 1.8x -> ~5.5s
    # Segment 3: 18-30s (Jayden loading + reveal) -> speed up 2x -> ~6s
    # Segment 4: 30-45s (Bucky Irving - THE HIT!) -> normal 1x -> 15s
    # Total: ~30s
    
    segments = [
        # (start, end, speed_factor)
        (0, 8, 2.5),      # Intro + pack open animation - fast
        (8, 18, 1.8),     # 4-card screen + Goff reveal - medium
        (18, 30, 2.0),    # Jayden Daniels reveal - medium
        (30, 45, 1.0),    # Bucky Irving (main hit!) - normal speed
    ]
    
    segment_files = []
    
    for i, (start, end, speed) in enumerate(segments):
        seg_file = f"{WORK_DIR}/segment_{i}.mp4"
        segment_files.append(seg_file)
        
        # Speed factor for setpts (inverse of speed)
        pts_factor = 1.0 / speed
        # Audio tempo (must be between 0.5 and 2.0)
        atempo = min(2.0, speed)
        if speed > 2.0:
            # Chain atempo filters for speeds > 2x
            atempo_filter = f"atempo={atempo},atempo={speed/2.0}"
        else:
            atempo_filter = f"atempo={atempo}"
        
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
        
        print(f"Creating segment {i+1}: {start}s-{end}s at {speed}x speed...")
        subprocess.run(cmd, capture_output=True)
    
    # Create concat file
    concat_file = f"{WORK_DIR}/concat_list.txt"
    with open(concat_file, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    # Concat segments
    temp_video = f"{WORK_DIR}/temp_concat.mp4"
    print("Concatenating segments...")
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        temp_video
    ], capture_output=True)
    
    # Add overlays and background music
    print("Adding overlays and music...")
    
    # Get duration of concatenated video
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', temp_video
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())
    print(f"Video duration: {duration:.1f}s")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', f"{WORK_DIR}/top_banner.png",
        '-i', f"{WORK_DIR}/bottom_banner.png",
        '-i', MUSIC_FILE,
        '-filter_complex',
        # Top banner throughout
        f'[0:v][1:v]overlay=0:30:enable=\'between(t,0,{duration})\'[v1];'
        # Bottom banner during Bucky reveal (last ~15s)
        f'[v1][2:v]overlay=0:750:enable=\'between(t,{duration-15},{duration})\'[vout];'
        # Mix audio with background music at low volume
        '[0:a]volume=1.0[a1];'
        '[3:a]volume=0.12[a2];'
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
    
    # Cleanup temp files
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    if os.path.exists(concat_file):
        os.remove(concat_file)
    
    print(f"Video created: {OUTPUT_VIDEO}")
    return OUTPUT_VIDEO

if __name__ == "__main__":
    output = create_video()
    if output:
        # Get file info
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration,size',
            '-of', 'default=noprint_wrappers=1', output
        ], capture_output=True, text=True)
        print(result.stdout)
