#!/usr/bin/env python3
"""
Create the best TikTok yet - optimized version
Uses pre-rendered text PNGs overlaid at specific timestamps
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Paths
INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/6188cc9d-3e3a-4c85-92d6-8d2b6b849f7b.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/new_pack"
OUTPUT_VIDEO = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt_ep3.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"

WIDTH = 384
HEIGHT = 848

def create_text_png(text, filename, font_size=36, color="white", stroke_color="black", 
                    stroke_width=3, y_position="top"):
    """Create a PNG with text overlay"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font
    font = None
    for font_name in ['/System/Library/Fonts/Helvetica.ttc', 
                     '/Library/Fonts/Arial Bold.ttf',
                     '/System/Library/Fonts/Supplemental/Arial Bold.ttf']:
        if os.path.exists(font_name):
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center horizontally
    x = (WIDTH - text_width) // 2
    
    # Position vertically
    if y_position == "top":
        y = 80
    elif y_position == "upper":
        y = HEIGHT // 4
    elif y_position == "center":
        y = (HEIGHT - text_height) // 2
    elif y_position == "lower":
        y = HEIGHT * 3 // 4 - text_height
    elif y_position == "bottom":
        y = HEIGHT - text_height - 150
    else:
        y = int(y_position) if isinstance(y_position, (int, float)) else 80
    
    # Draw stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    # Draw text
    draw.text((x, y), text, font=font, fill=color)
    
    img.save(filename, 'PNG')
    return filename


def main():
    print("Creating the best TikTok yet! (Optimized)")
    print("=" * 50)
    
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Step 1: Create speed-adjusted base video first
    print("\nStep 1: Creating speed-adjusted base video...")
    
    # Speed segments for ~30 second target
    # Original: 42 seconds -> Target: ~30 seconds
    segments = [
        (0, 6, 2.5),      # Intro -> 2.4s
        (6, 9, 2.0),      # Animation -> 1.5s
        (9, 15, 1.8),     # Card screen -> 3.3s
        (15, 21, 1.3),    # Fashanu -> 4.6s
        (21, 30, 1.3),    # Kittle + Winston -> 6.9s
        (30, 36, 1.0),    # Karty (keep normal) -> 6s
        (36, 42, 1.5),    # Final -> 4s
    ]
    # Total: ~28.7 seconds
    
    segment_files = []
    for i, (start, end, speed) in enumerate(segments):
        segment_file = os.path.join(WORK_DIR, f"seg_{i}.mp4")
        segment_files.append(segment_file)
        
        duration = end - start
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start), '-t', str(duration),
            '-i', INPUT_VIDEO,
            '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast',
            '-c:a', 'aac',
            segment_file
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"  Segment {i}: {start}-{end}s @ {speed}x speed")
    
    # Concatenate segments
    print("\nStep 2: Concatenating segments...")
    concat_list = os.path.join(WORK_DIR, "concat.txt")
    with open(concat_list, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    base_video = os.path.join(WORK_DIR, "base.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'fast',
        '-c:a', 'aac',
        base_video
    ], capture_output=True)
    
    # Get duration
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', base_video
    ], capture_output=True, text=True)
    duration = float(probe.stdout.strip())
    print(f"  Base video: {duration:.1f}s")
    
    # Step 3: Create text overlay PNGs
    print("\nStep 3: Creating text overlay images...")
    
    # Calculate adjusted timestamps
    def get_new_time(original_time):
        cumulative_new = 0
        for start, end, speed in segments:
            if original_time <= start:
                return cumulative_new
            elif original_time <= end:
                return cumulative_new + (original_time - start) / speed
            cumulative_new += (end - start) / speed
        return cumulative_new
    
    # Text overlays with original timestamps
    texts = [
        # (text, original_start, original_end, font_size, color, position)
        ("DRAKE MAYE HUNT EP.3", 0, 3, 40, "#FFD700", "top"),
        ("$59 SELECT PACK", 0, 6, 30, "white", "upper"),
        ("WILL HE BE IN HERE?", 6, 9, 34, "#00FF00", "bottom"),
        ("2 RARES + 2 UNCOMMONS", 9, 12, 30, "#FF6B6B", "top"),
        ("FASHANU 8/218", 15, 18, 28, "#00CED1", "bottom"),
        ("GEORGE KITTLE!", 21, 24, 36, "#FF4444", "bottom"),
        ("RARE ALERT", 24, 26, 38, "#FFD700", "top"),
        ("JAMEIS WINSTON 30/99", 26, 30, 30, "#FF8C00", "bottom"),
        ("ANOTHER RARE!", 33, 35, 38, "#FFD700", "top"),
        ("JOSHUA KARTY 41/79", 35, 38, 30, "#9370DB", "bottom"),
        ("STILL NO DRAKE MAYE", 38, 41, 34, "#FF4444", "center"),
        ("THE HUNT CONTINUES", 39, 42, 26, "white", "lower"),
    ]
    
    # Create overlay filter chain
    overlay_inputs = []
    filter_parts = []
    
    for i, (text, orig_start, orig_end, font_size, color, position) in enumerate(texts):
        # Create PNG
        png_file = os.path.join(WORK_DIR, f"text_{i}.png")
        create_text_png(text, png_file, font_size=font_size, color=color, y_position=position)
        overlay_inputs.extend(['-i', png_file])
        
        # Calculate new timestamps
        new_start = get_new_time(orig_start)
        new_end = min(get_new_time(orig_end), duration)
        
        print(f"  '{text}': {new_start:.1f}s - {new_end:.1f}s")
        
        # Add to filter
        input_idx = i + 1  # +1 because base video is input 0
        if i == 0:
            filter_parts.append(f"[0:v][{input_idx}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
        else:
            filter_parts.append(f"[v{i-1}][{input_idx}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
    
    # Step 4: Apply all overlays
    print("\nStep 4: Applying text overlays...")
    filter_complex = ";".join(filter_parts)
    
    video_with_text = os.path.join(WORK_DIR, "with_text.mp4")
    cmd = [
        'ffmpeg', '-y',
        '-i', base_video,
    ] + overlay_inputs + [
        '-filter_complex', filter_complex,
        '-map', f'[v{len(texts)-1}]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac',
        video_with_text
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error applying overlays: {result.stderr}")
        # Fallback: just use base video
        video_with_text = base_video
    
    # Step 5: Add background music
    print("\nStep 5: Adding background music...")
    
    # Download music if needed
    if not os.path.exists(MUSIC_PATH):
        subprocess.run([
            'curl', '-L', '-o', MUSIC_PATH,
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3'
        ], capture_output=True)
    
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_with_text,
        '-i', MUSIC_PATH,
        '-filter_complex',
        '[0:a]volume=1.0[orig];[1:a]volume=0.12[music];[orig][music]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        OUTPUT_VIDEO
    ], capture_output=True)
    
    # Final stats
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,size',
        '-of', 'default=noprint_wrappers=1', OUTPUT_VIDEO
    ], capture_output=True, text=True)
    
    print("\n" + "=" * 50)
    print("SUCCESS! Video created:")
    print(f"  {OUTPUT_VIDEO}")
    for line in probe.stdout.strip().split('\n'):
        if 'duration' in line:
            print(f"  Duration: {float(line.split('=')[1]):.1f}s")
        if 'size' in line:
            print(f"  Size: {int(line.split('=')[1]) / 1024 / 1024:.2f} MB")
    
    # Cleanup
    print("\nCleaning up...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    
    return OUTPUT_VIDEO


if __name__ == "__main__":
    main()
