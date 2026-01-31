#!/usr/bin/env python3
"""
Drake Maye Hunt EP.5 - ULTRA RARE Demario Davis 7/49!
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/7ffcac7e-768a-4ba3-bba5-a0a830ff9fe7.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep5"
OUTPUT_VIDEO = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt_ep5.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"

WIDTH = 384
HEIGHT = 848

def create_text_png(text, filename, font_size=36, color="white", stroke_color="black", 
                    stroke_width=3, y_position="top"):
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font = None
    for font_name in ['/System/Library/Fonts/Helvetica.ttc', 
                     '/Library/Fonts/Arial Bold.ttf']:
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
    
    if y_position == "top": y = 80
    elif y_position == "upper": y = HEIGHT // 4
    elif y_position == "center": y = (HEIGHT - text_height) // 2
    elif y_position == "lower": y = HEIGHT * 3 // 4 - text_height
    elif y_position == "bottom": y = HEIGHT - text_height - 150
    else: y = 80
    
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=color)
    img.save(filename, 'PNG')


def main():
    print("Creating Drake Maye Hunt EP.5!")
    print("=" * 50)
    
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # 37s -> 28s target
    segments = [
        (0, 3, 3.0),      # Pack display -> 1s
        (3, 9, 2.5),      # Animation -> 2.4s
        (9, 12, 2.0),     # 4-card screen -> 1.5s
        (12, 18, 1.8),    # Lavonte + grid -> 3.3s
        (18, 24, 1.5),    # Rome Odunze + DeMarcus -> 4s
        (24, 27, 1.3),    # Grid transition -> 2.3s
        (27, 34, 1.0),    # Demario Davis ULTRA RARE -> 7s (climax!)
        (34, 37, 1.5),    # Final grid -> 2s
    ]
    # Total: ~23.5s
    
    print("\nStep 1: Creating speed segments...")
    segment_files = []
    for i, (start, end, speed) in enumerate(segments):
        segment_file = os.path.join(WORK_DIR, f"seg_{i}.mp4")
        segment_files.append(segment_file)
        
        if speed <= 2.0:
            audio_filter = f"atempo={speed}"
        else:
            audio_filter = f"atempo=2.0,atempo={speed/2.0}"
        
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(start), '-t', str(end-start),
            '-i', INPUT_VIDEO,
            '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]{audio_filter}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac',
            segment_file
        ], capture_output=True)
        print(f"  Segment {i}: {start}-{end}s @ {speed}x")
    
    print("\nStep 2: Concatenating...")
    concat_list = os.path.join(WORK_DIR, "concat.txt")
    with open(concat_list, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    base_video = os.path.join(WORK_DIR, "base.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', base_video
    ], capture_output=True)
    
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', base_video
    ], capture_output=True, text=True)
    duration = float(probe.stdout.strip())
    print(f"  Base video: {duration:.1f}s")
    
    def get_new_time(orig):
        cum = 0
        for start, end, speed in segments:
            if orig <= start: return cum
            elif orig <= end: return cum + (orig - start) / speed
            cum += (end - start) / speed
        return cum
    
    print("\nStep 3: Creating text overlays...")
    texts = [
        ("DRAKE MAYE HUNT EP.5", 0, 3, 40, "#FFD700", "top"),
        ("SELECT PACK", 0, 9, 28, "white", "upper"),
        ("ULTRA RARE INSIDE!", 9, 12, 32, "#FF1493", "bottom"),
        ("LAVONTE DAVID", 12, 15, 26, "#E31837", "bottom"),
        ("ROME ODUNZE RC!", 18, 21, 28, "#0B162A", "bottom"),  # Bears colors
        ("DEMARCUS WARE", 21, 24, 26, "#FB4F14", "bottom"),  # Broncos
        ("ULTRA RARE!", 27, 29, 42, "#FF1493", "top"),
        ("DEMARIO DAVIS 7/49!", 29, 34, 32, "#D3BC8D", "bottom"),  # Saints gold
        ("STILL NO DRAKE MAYE", 32, 35, 30, "#FF4444", "center"),
        ("THE HUNT CONTINUES", 34, 37, 24, "white", "lower"),
    ]
    
    overlay_inputs = []
    filter_parts = []
    
    for i, (text, orig_start, orig_end, font_size, color, position) in enumerate(texts):
        png_file = os.path.join(WORK_DIR, f"text_{i}.png")
        create_text_png(text, png_file, font_size=font_size, color=color, y_position=position)
        overlay_inputs.extend(['-i', png_file])
        
        new_start = get_new_time(orig_start)
        new_end = min(get_new_time(orig_end), duration)
        print(f"  '{text}': {new_start:.1f}s - {new_end:.1f}s")
        
        if i == 0:
            filter_parts.append(f"[0:v][{i+1}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
        else:
            filter_parts.append(f"[v{i-1}][{i+1}:v]overlay=0:0:enable='between(t,{new_start},{new_end})'[v{i}]")
    
    print("\nStep 4: Applying overlays...")
    video_with_text = os.path.join(WORK_DIR, "with_text.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', base_video
    ] + overlay_inputs + [
        '-filter_complex', ";".join(filter_parts),
        '-map', f'[v{len(texts)-1}]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-c:a', 'aac',
        video_with_text
    ], capture_output=True)
    
    print("\nStep 5: Adding music...")
    subprocess.run([
        'ffmpeg', '-y', '-i', video_with_text, '-i', MUSIC_PATH,
        '-filter_complex', '[0:a]volume=1.0[orig];[1:a]volume=0.12[music];[orig][music]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest',
        OUTPUT_VIDEO
    ], capture_output=True)
    
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,size',
        '-of', 'default=noprint_wrappers=1', OUTPUT_VIDEO
    ], capture_output=True, text=True)
    
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"  Output: {OUTPUT_VIDEO}")
    for line in probe.stdout.strip().split('\n'):
        if 'duration' in line: print(f"  Duration: {float(line.split('=')[1]):.1f}s")
        if 'size' in line: print(f"  Size: {int(line.split('=')[1])/1024/1024:.2f} MB")
    
    for seg in segment_files:
        if os.path.exists(seg): os.remove(seg)


if __name__ == "__main__":
    main()
