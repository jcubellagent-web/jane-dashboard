#!/usr/bin/env python3
"""
Drake Maye Hunt EP.6 - ULTRA RARE Anthony Richardson 7/49!
THE BEST ONE YET - Premium quality edit
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/bb4cb1e3-c0f2-4eaa-8cd4-8ab51e8da7fa.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep6_best"
OUTPUT_VIDEO = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt_ep6_BEST.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"

WIDTH = 384
HEIGHT = 848

def create_text_png(text, filename, font_size=36, color="white", stroke_color="black", 
                    stroke_width=3, y_position="top", glow=False):
    """Create text overlay PNG with optional glow effect"""
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
    
    positions = {
        "top": 70,
        "upper": HEIGHT // 4,
        "center": (HEIGHT - text_height) // 2,
        "lower": HEIGHT * 3 // 4 - text_height,
        "bottom": HEIGHT - text_height - 140,
        "subtitle": HEIGHT - text_height - 100
    }
    y = positions.get(y_position, 70)
    
    # Enhanced glow effect for special text
    if glow:
        for radius in range(8, 0, -2):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    draw.text((x + dx, y + dy), text, font=font, fill=(255, 200, 0, 30))
    
    # Stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    draw.text((x, y), text, font=font, fill=color)
    img.save(filename, 'PNG')


def main():
    print("🎬 Creating Drake Maye Hunt EP.6 - THE BEST ONE YET!")
    print("=" * 60)
    
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Video is 38 seconds - target 28-30 seconds
    # Timestamps based on frame analysis:
    # 0-3s: Pack display
    # 3-9s: Opening animation / rarity reveal
    # 9-12s: 4-card grid
    # 12-18s: Mo Alie-Cox reveal
    # 18-24s: DeVonta Smith reveal (RARE)
    # 24-30s: Anthony Richardson reveal (ULTRA RARE - THE HIT!)
    # 30-38s: Jalen Carter + final grid
    
    segments = [
        (0, 2, 2.5),       # Pack intro -> 0.8s
        (2, 4, 2.0),       # Pack details -> 1s
        (4, 9, 2.0),       # Opening animation -> 2.5s
        (9, 12, 1.8),      # Rarity grid reveal -> 1.7s
        (12, 18, 1.5),     # Mo Alie-Cox -> 4s
        (18, 24, 1.3),     # DeVonta Smith RARE -> 4.6s
        (24, 32, 0.9),     # Anthony Richardson ULTRA RARE -> 8.9s (SLOW FOR IMPACT!)
        (32, 38, 1.6),     # Jalen Carter + end -> 3.75s
    ]
    # Total: ~27.3s
    
    print("\n📹 Step 1: Creating dynamic speed segments...")
    segment_files = []
    for i, (start, end, speed) in enumerate(segments):
        segment_file = os.path.join(WORK_DIR, f"seg_{i}.mp4")
        segment_files.append(segment_file)
        
        # Handle audio tempo (max 2.0x per filter)
        if speed <= 2.0:
            audio_filter = f"atempo={speed}"
        else:
            audio_filter = f"atempo=2.0,atempo={speed/2.0}"
        
        cmd = [
            'ffmpeg', '-y', '-ss', str(start), '-t', str(end-start),
            '-i', INPUT_VIDEO,
            '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]{audio_filter}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac',
            segment_file
        ]
        subprocess.run(cmd, capture_output=True)
        desc = "🐌 SLOW" if speed < 1.0 else "⚡ FAST" if speed > 1.5 else "▶️ NORMAL"
        print(f"  Segment {i}: {start:2d}-{end:2d}s @ {speed}x {desc}")
    
    print("\n🔗 Step 2: Concatenating segments...")
    concat_list = os.path.join(WORK_DIR, "concat.txt")
    with open(concat_list, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    base_video = os.path.join(WORK_DIR, "base.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac',
        base_video
    ], capture_output=True)
    
    # Get actual duration
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', base_video
    ], capture_output=True, text=True)
    duration = float(probe.stdout.strip())
    print(f"  Base video duration: {duration:.1f}s ✓")
    
    # Calculate new timestamps
    def get_new_time(orig):
        cumulative = 0
        for start, end, speed in segments:
            if orig <= start:
                return cumulative
            elif orig <= end:
                return cumulative + (orig - start) / speed
            cumulative += (end - start) / speed
        return cumulative
    
    print("\n🎨 Step 3: Creating text overlay images...")
    
    # Text overlays - adjusted for new timestamps
    texts = [
        # (text, orig_start, orig_end, font_size, color, position, glow)
        ("🏈 DRAKE MAYE HUNT", 0, 4, 38, "#FFD700", "top", True),
        ("EP.6", 0, 4, 32, "white", "upper", False),
        ("SELECT PACK", 1, 4, 28, "#00CED1", "bottom", False),
        
        ("WHAT'S INSIDE? 👀", 5, 9, 32, "#00FF00", "bottom", False),
        ("2 UNCOMMON + 1 RARE", 9, 11, 26, "white", "top", False),
        ("+ 1 ULTRA RARE! 🔥", 9, 11, 28, "#FF1493", "upper", True),
        
        ("MO ALIE-COX", 13, 16, 32, "#00CED1", "bottom", False),
        ("2/218 UNCOMMON", 14, 17, 24, "white", "subtitle", False),
        
        ("DEVONTA SMITH 🦅", 19, 23, 34, "#00FF00", "bottom", False),
        ("84/199 RARE!", 20, 23, 28, "#4169E1", "subtitle", False),
        
        ("🔥 ULTRA RARE 🔥", 24, 26, 36, "#FFD700", "top", True),
        ("ANTHONY RICHARDSON", 26, 31, 34, "#FF4500", "bottom", True),
        ("🏆 7/49 ORANGE PULSAR 🏆", 27, 31, 28, "#FF8C00", "subtitle", True),
        ("MASSIVE HIT!", 28, 30, 40, "#FF1493", "center", True),
        
        ("JALEN CARTER", 33, 36, 30, "#00CED1", "bottom", False),
        ("69/397 UNCOMMON", 34, 36, 24, "white", "subtitle", False),
        
        ("STILL NO DRAKE MAYE 😤", 36, 39, 32, "#FF4444", "center", False),
        ("THE HUNT CONTINUES...", 37, 40, 24, "white", "lower", False),
    ]
    
    overlay_inputs = []
    filter_parts = []
    
    for i, (text, orig_start, orig_end, font_size, color, position, glow) in enumerate(texts):
        png_file = os.path.join(WORK_DIR, f"text_{i:02d}.png")
        create_text_png(text, png_file, font_size=font_size, color=color, 
                       y_position=position, glow=glow)
        overlay_inputs.extend(['-i', png_file])
        
        new_start = get_new_time(orig_start)
        new_end = min(get_new_time(orig_end), duration)
        
        input_idx = i + 1
        if i == 0:
            filter_parts.append(f"[0:v][{input_idx}:v]overlay=0:0:enable='between(t,{new_start:.2f},{new_end:.2f})'[v{i}]")
        else:
            filter_parts.append(f"[v{i-1}][{input_idx}:v]overlay=0:0:enable='between(t,{new_start:.2f},{new_end:.2f})'[v{i}]")
        
        print(f"  '{text[:25]}...' @ {new_start:.1f}s-{new_end:.1f}s")
    
    print("\n✨ Step 4: Applying text overlays...")
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
        print(f"  ⚠️ Overlay warning, using fallback...")
        video_with_text = base_video
    else:
        print("  ✓ Text overlays applied!")
    
    print("\n🎵 Step 5: Adding hype background music...")
    
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_with_text,
        '-i', MUSIC_PATH,
        '-filter_complex',
        '[0:a]volume=1.0[orig];[1:a]volume=0.15[music];[orig][music]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        OUTPUT_VIDEO
    ], capture_output=True)
    
    # Final stats
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,size',
        '-of', 'default=noprint_wrappers=1', OUTPUT_VIDEO
    ], capture_output=True, text=True)
    
    print("\n" + "=" * 60)
    print("🎬 SUCCESS! THE BEST TIKTOK YET!")
    print(f"📁 Output: {OUTPUT_VIDEO}")
    for line in probe.stdout.strip().split('\n'):
        if 'duration' in line:
            dur = float(line.split('=')[1])
            print(f"⏱️  Duration: {dur:.1f}s {'✓ Under 30s!' if dur <= 30 else '⚠️ Over 30s'}")
        if 'size' in line:
            size_mb = int(line.split('=')[1]) / 1024 / 1024
            print(f"📦 Size: {size_mb:.2f} MB")
    
    # Cleanup segment files
    print("\n🧹 Cleaning up temp files...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    
    print("\n✅ Ready for TikTok! 🎉")
    return OUTPUT_VIDEO


if __name__ == "__main__":
    main()
