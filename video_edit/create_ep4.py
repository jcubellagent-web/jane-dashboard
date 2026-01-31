#!/usr/bin/env python3
"""
Drake Maye Hunt EP.4 - ULTRA RARE + EPIC PACK!
Target: Under 30 seconds, max retention
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/3b9f89e3-4c9c-4381-a531-ab685f879bfc.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep4"
OUTPUT_VIDEO = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt_ep4.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"

WIDTH = 384
HEIGHT = 848

def create_text_png(text, filename, font_size=36, color="white", stroke_color="black", 
                    stroke_width=3, y_position="top"):
    """Create a PNG with text overlay"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
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
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (WIDTH - text_width) // 2
    
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
    
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    draw.text((x, y), text, font=font, fill=color)
    img.save(filename, 'PNG')
    return filename


def main():
    print("Creating Drake Maye Hunt EP.4 - BEST PACK YET!")
    print("=" * 50)
    
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Speed segments to get 52s -> ~28s
    # Focus on retention: fast intro, slow reveals for big hits
    print("\nStep 1: Creating speed-adjusted segments...")
    
    segments = [
        (0, 4, 3.0),      # Loading -> 1.3s
        (4, 8, 2.5),      # Pack animation -> 1.6s
        (8, 12, 2.0),     # 4-card screen (show rarities!) -> 2s
        (12, 24, 2.2),    # Early reveals -> 5.5s
        (24, 40, 2.0),    # Middle section -> 8s
        (40, 46, 1.3),    # Build to Bucky -> 4.6s
        (46, 50, 1.0),    # A.J. Brown EPIC reveal -> 4s (CLIMAX!)
        (50, 52, 1.5),    # Final grid -> 1.3s
    ]
    # Total: ~28.3s
    
    segment_files = []
    for i, (start, end, speed) in enumerate(segments):
        segment_file = os.path.join(WORK_DIR, f"seg_{i}.mp4")
        segment_files.append(segment_file)
        
        duration = end - start
        # Handle audio tempo (max 2.0 per pass)
        if speed <= 2.0:
            audio_filter = f"atempo={speed}"
        else:
            # Chain multiple atempo filters
            audio_filter = f"atempo=2.0,atempo={speed/2.0}"
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start), '-t', str(duration),
            '-i', INPUT_VIDEO,
            '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]{audio_filter}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast',
            '-c:a', 'aac',
            segment_file
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"  Segment {i}: {start}-{end}s @ {speed}x")
    
    # Concatenate
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
    
    # Time mapping function
    def get_new_time(original_time):
        cumulative_new = 0
        for start, end, speed in segments:
            if original_time <= start:
                return cumulative_new
            elif original_time <= end:
                return cumulative_new + (original_time - start) / speed
            cumulative_new += (end - start) / speed
        return cumulative_new
    
    # Text overlays - strategic for retention
    print("\nStep 3: Creating text overlays...")
    
    texts = [
        # HOOK - immediately grab attention
        ("BEST PACK YET?!", 0, 4, 42, "#FFD700", "top"),
        ("$58 SELECT", 0, 8, 28, "white", "upper"),
        
        # Build hype with rarity tease
        ("ULTRA RARE + EPIC!", 8, 12, 36, "#FF00FF", "bottom"),
        
        # Card reveals
        ("JARED GOFF 21/79", 14, 18, 28, "#00BFFF", "bottom"),
        ("JAYDEN DANIELS RC", 18, 22, 28, "#8B0000", "bottom"),
        
        # BIG HIT ALERT
        ("ULTRA RARE!", 22, 24, 40, "#FF1493", "top"),
        ("BUCKY IRVING 45/49", 24, 27, 32, "#FF6347", "bottom"),
        
        # CLIMAX - A.J. Brown EPIC
        ("EPIC ALERT!", 27, 28.5, 44, "#9400D3", "top"),
        ("A.J. BROWN 17/25!", 28, 30, 36, "#9400D3", "bottom"),
        
        # Drake Maye callback
        ("STILL NO DRAKE MAYE", 26, 28.5, 26, "#FF4444", "lower"),
        ("BUT THIS PACK WAS FIRE", 28, 30, 24, "#FFD700", "lower"),
    ]
    
    # Create overlay filter chain
    overlay_inputs = []
    filter_parts = []
    
    for i, (text, orig_start, orig_end, font_size, color, position) in enumerate(texts):
        png_file = os.path.join(WORK_DIR, f"text_{i}.png")
        create_text_png(text, png_file, font_size=font_size, color=color, y_position=position)
        overlay_inputs.extend(['-i', png_file])
        
        new_start = get_new_time(orig_start)
        new_end = min(get_new_time(orig_end), duration)
        
        print(f"  '{text}': {new_start:.1f}s - {new_end:.1f}s")
        
        input_idx = i + 1
        if i == 0:
            filter_parts.append(f"[0:v][{input_idx}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
        else:
            filter_parts.append(f"[v{i-1}][{input_idx}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
    
    # Apply overlays
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
        print(f"Warning: Overlay failed, using base video")
        video_with_text = base_video
    
    # Add background music
    print("\nStep 5: Adding background music...")
    
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
    print("SUCCESS!")
    print(f"  Output: {OUTPUT_VIDEO}")
    for line in probe.stdout.strip().split('\n'):
        if 'duration' in line:
            print(f"  Duration: {float(line.split('=')[1]):.1f}s")
        if 'size' in line:
            print(f"  Size: {int(line.split('=')[1]) / 1024 / 1024:.2f} MB")
    
    # Cleanup
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    
    return OUTPUT_VIDEO


if __name__ == "__main__":
    main()
