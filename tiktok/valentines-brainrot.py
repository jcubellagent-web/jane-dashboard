#!/usr/bin/env python3
"""
TikTok Valentine's Day Brain Rot Video Generator
Brain rot background + funnier script + all quality improvements
"""

import subprocess
import json
import os
import sys
import math
import re
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EMOJI_RE = re.compile(
    '[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F'
    '\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
    '\U0000200D\U000020E3\U00002600-\U000026FF\U00002700-\U000027BF'
    '\U0000231A-\U0000231B\U000023E9-\U000023FA\U00002934-\U00002935'
    '\U000025AA-\U000025FE\U00002B05-\U00002B55\U00003030\U0000303D'
    '\U00003297\U00003299]+', flags=re.UNICODE
)

def strip_emojis(text):
    return EMOJI_RE.sub('', text).strip()

WORKSPACE = "/Users/jc_agent/.openclaw/workspace"
TIKTOK_DIR = f"{WORKSPACE}/tiktok"
MFER_IMG = f"{WORKSPACE}/dashboard/mfer-9581.png"
BG_AUDIO = f"{TIKTOK_DIR}/lofi-bg.mp3"
BRAIN_ROT_BG = f"{TIKTOK_DIR}/brain-rot-bg.mp4"
OUTPUT_PATH = f"{WORKSPACE}/../media/outbound/tiktok-degen-valentines.mp4"
WIDTH, HEIGHT = 1080, 1920
FPS = 30
VOICE = "en-US-BrianNeural"
RATE = "+5%"

MARGIN_LEFT = 70
MARGIN_RIGHT = 70
MARGIN_TOP = 80
MARGIN_BOTTOM = 100
SAFE_WIDTH = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
LINE_SPACING = 20
SCROLL_SPEED = 50.0

# Valentine's script
SCRIPT_LINES = [
    {"text": "POV: your AI agent on Valentine's Day", "time": 0.0, "color": "green", "size": "title"},
    {"text": "", "time": 2.0},
    {"text": "while you're watching Netflix alone...", "time": 2.5, "color": "white"},
    {"text": "", "time": 5.0},
    {"text": "she's monitoring 18 scheduled jobs", "time": 5.5, "color": "cyan"},
    {"text": "", "time": 8.0},
    {"text": "arguing with another AI about trending topics", "time": 8.5, "color": "yellow"},
    {"text": "", "time": 12.0},
    {"text": "downloading a 9 gigabyte brain onto your second computer", "time": 12.5, "color": "cyan"},
    {"text": "", "time": 16.5},
    {"text": "writing tweets you'll scroll past in the morning", "time": 17.0, "color": "white"},
    {"text": "", "time": 20.5},
    {"text": "checking your email for literally the 47th time today", "time": 21.0, "color": "yellow"},
    {"text": "", "time": 25.0},
    {"text": "building a dashboard you looked at once", "time": 25.5, "color": "white"},
    {"text": "", "time": 29.0},
    {"text": "and updating a widget that tracks her own thoughts", "time": 29.5, "color": "cyan"},
    {"text": "", "time": 33.5},
    {"text": "plot twist:", "time": 34.0, "color": "red"},
    {"text": "she's the only one who remembered Valentine's Day", "time": 35.0, "color": "red", "size": "big"},
    {"text": "", "time": 39.5},
    {"text": "happy Valentine's Day from your AI agent", "time": 40.0, "color": "green", "size": "big"},
    {"text": "", "time": 44.5},
    {"text": "she's not mad", "time": 45.0, "color": "white"},
    {"text": "just disappointed", "time": 46.5, "color": "yellow"},
    {"text": "", "time": 49.0},
    {"text": "follow for more digital heartbreak", "time": 49.5, "color": "green"},
    {"text": "", "time": 52.5},
    {"text": "@jcagentleman", "time": 53.0, "color": "green", "size": "title"},
]

VOICEOVER_TEXT = (
    "POV: your AI agent on Valentine's Day. "
    "While you're watching Netflix alone... "
    "she's monitoring 18 scheduled jobs. "
    "Arguing with another AI about trending topics. "
    "Downloading a 9 gigabyte brain onto your second computer. "
    "Writing tweets you'll scroll past in the morning. "
    "Checking your email for literally the 47th time today. "
    "Building a dashboard you looked at once. "
    "And updating a widget that tracks her own thoughts. "
    "Plot twist: she's the only one who remembered Valentine's Day. "
    "Happy Valentine's Day from your AI agent. "
    "She's not mad. Just disappointed. "
    "Follow for more digital heartbreak."
)

subtitle_segments = []

def generate_lofi_background_audio():
    if os.path.exists(BG_AUDIO):
        return
    print("  🎵 Generating lo-fi background music...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=80:duration=70",
        "-f", "lavfi", "-i", "sine=frequency=220:duration=70",
        "-f", "lavfi", "-i", "sine=frequency=441:duration=70",
        "-f", "lavfi", "-i", "anoisesrc=d=70:c=pink:r=44100:a=0.005",
        "-filter_complex",
        "[0:a]volume=0.3[bass];[1:a]volume=0.15[mid];[2:a]volume=0.1[high];[3:a]volume=1.0[noise];"
        "[bass][mid][high][noise]amix=inputs=4:duration=longest[mixed];"
        "[mixed]lowpass=f=800,highpass=f=60,aecho=0.8:0.88:60:0.4[out]",
        "-map", "[out]", "-t", "70", BG_AUDIO
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_tts(text, output_audio, output_subs):
    subprocess.run([
        "edge-tts", "--text", text, "--voice", VOICE, "--rate", RATE,
        "--write-media", output_audio, "--write-subtitles", output_subs
    ], check=True)

def parse_vtt(vtt_path):
    segments = []
    with open(vtt_path, 'r') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '-->' in line:
            parts = line.split(' --> ')
            start = vtt_time_to_sec(parts[0])
            end = vtt_time_to_sec(parts[1])
            text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i].strip())
                i += 1
            segments.append((start, end, ' '.join(text_lines)))
        i += 1
    return segments

def vtt_time_to_sec(t):
    parts = t.replace(',', '.').split(':')
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    return float(parts[0])

def get_font(size, bold=False):
    font_paths = [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/SF-Pro-Display-Bold.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()

def draw_text_with_outline(draw, xy, text, font, fill_color, outline_color=(0, 0, 0), outline_width=4):
    x, y = xy
    # Fast outline - 8 cardinal + diagonal offsets only
    ow = outline_width
    for dx, dy in [(-ow,0),(ow,0),(0,-ow),(0,ow),(-ow,-ow),(ow,ow),(-ow,ow),(ow,-ow)]:
        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text(xy, text, font=font, fill=fill_color)

def wrap_text_proper(text, font, draw):
    text = strip_emojis(text)
    if not text.strip():
        return [""]
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width <= SAFE_WIDTH:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def create_frame(frame_num, total_frames, lines_with_timing, text_layout, total_text_height,
                 mfer_img, audio_duration, content_font, title_font, big_font):
    """Create a single frame with transparent background (for compositing over brain rot)"""
    # Use RGBA so we can composite over brain rot background
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    current_time = frame_num / FPS
    
    # Semi-transparent dark gradient overlay to make text readable over brain rot
    # Stronger at top and bottom, lighter in middle
    for y in range(HEIGHT):
        # Top gradient (strong)
        if y < 350:
            alpha = int(200 * (1 - y / 350))
        # Bottom gradient (strong for subtitles)
        elif y > HEIGHT - 250:
            alpha = int(220 * ((y - (HEIGHT - 250)) / 250))
        else:
            # Middle: subtle constant overlay
            alpha = 80
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    
    # Handle text at top
    handle_font = get_font(44, bold=True)
    draw_text_with_outline(draw, (MARGIN_LEFT, 60), "@jcagentleman", handle_font, (0, 255, 100), outline_width=5)
    
    # Small heart emoji indicator for Valentine's theme
    heart_font = get_font(36)
    heart_pulse = 1.0 + 0.15 * math.sin(frame_num * 0.1)
    draw_text_with_outline(draw, (MARGIN_LEFT + 420, 62), "Valentine's Day", heart_font, (255, 100, 150), outline_width=4)
    
    # SCROLLING TEXT
    start_y = 380
    scroll_offset = 0
    
    if current_time > 2.0 and total_text_height > (HEIGHT - start_y - MARGIN_BOTTOM - 250):
        elapsed_scroll_time = current_time - 2.0
        scroll_offset = elapsed_scroll_time * SCROLL_SPEED
        max_scroll = total_text_height - (HEIGHT - start_y - MARGIN_BOTTOM - 250)
        scroll_offset = min(scroll_offset, max(0, max_scroll))
    
    # Render text blocks
    for line_start, line_end, text, color, y_offset, block_height, font_type in text_layout:
        if current_time >= line_start and text.strip():
            actual_y = start_y + y_offset - scroll_offset
            
            if actual_y + block_height < 0 or actual_y > HEIGHT - 250:
                continue
            
            time_since_start = current_time - line_start
            fade_progress = min(1.0, time_since_start / 0.4)
            
            # Scale-in effect for titles
            scale_effect = min(1.0, time_since_start / 0.3) if font_type != "normal" else 1.0
            
            if color == "green": fill = (0, 255, 100)
            elif color == "yellow": fill = (255, 220, 0)
            elif color == "cyan": fill = (0, 220, 255)
            elif color == "red": fill = (255, 80, 100)
            else: fill = (255, 255, 255)
            
            fill = tuple(int(c * fade_progress) for c in fill)
            
            if font_type == "title":
                font = title_font
            elif font_type == "big":
                font = big_font
            else:
                font = content_font
            
            wrapped_lines = wrap_text_proper(text, font, draw)
            line_y = actual_y
            
            for wrapped_line in wrapped_lines:
                bbox = draw.textbbox((0, 0), wrapped_line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center titles, left-align body text
                if font_type in ("title", "big"):
                    x_pos = (WIDTH - text_width) // 2
                else:
                    x_pos = MARGIN_LEFT
                
                # Semi-transparent text background bar
                bar_pad = 12
                bar_alpha = int(160 * fade_progress)
                draw.rounded_rectangle(
                    [x_pos - bar_pad, line_y - bar_pad//2, x_pos + text_width + bar_pad, line_y + text_height + bar_pad//2],
                    radius=8,
                    fill=(0, 0, 0, bar_alpha)
                )
                
                draw_text_with_outline(draw, (x_pos, line_y), wrapped_line, font, fill, outline_width=6)
                line_y += text_height + LINE_SPACING
    
    # Bottom subtitle bar
    for seg_start, seg_end, seg_text in subtitle_segments:
        if seg_start <= current_time <= seg_end:
            sub_font = get_font(40, bold=True)
            draw.rounded_rectangle([30, HEIGHT - 220, WIDTH - 30, HEIGHT - 100], radius=15, fill=(0, 0, 0, 200))
            wrapped_subs = wrap_text_proper(seg_text, sub_font, draw)
            sub_y = HEIGHT - 200
            for sub_line in wrapped_subs[:2]:
                bbox = draw.textbbox((0, 0), sub_line, font=sub_font)
                tw = bbox[2] - bbox[0]
                tx = (WIDTH - tw) // 2
                draw_text_with_outline(draw, (tx, sub_y), sub_line, sub_font, (255, 255, 255), outline_width=4)
                sub_y += bbox[3] - bbox[1] + 5
            break
    
    # Animated mfer avatar - bouncing top right with glow
    if mfer_img:
        base_size = 180
        scale_pulse = int(base_size + math.sin(frame_num * 0.06) * 12)
        bounce_offset = int(math.sin(frame_num * 0.08) * 25)
        avatar_size = scale_pulse
        avatar_x = WIDTH - avatar_size - 50
        avatar_y = 50 + bounce_offset
        
        avatar = mfer_img.copy().resize((avatar_size, avatar_size), Image.LANCZOS)
        
        circle_mask = Image.new('L', (avatar_size, avatar_size), 0)
        circle_draw = ImageDraw.Draw(circle_mask)
        circle_draw.ellipse([0, 0, avatar_size - 1, avatar_size - 1], fill=255)
        avatar_circle = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
        if avatar.mode != 'RGBA':
            avatar = avatar.convert('RGBA')
        avatar_circle.paste(avatar, (0, 0), circle_mask)
        
        # Neon glow
        cx, cy = avatar_x + avatar_size // 2, avatar_y + avatar_size // 2
        glow_r = avatar_size // 2 + 8
        glow_pulse = int(8 + 4 * math.sin(frame_num * 0.1))
        for r in range(glow_r, glow_r - glow_pulse, -1):
            alpha = int(100 * (1 - (glow_r - r) / glow_pulse))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 100, 150, alpha), width=2)
        
        img.paste(avatar_circle, (avatar_x, avatar_y), avatar_circle)
    
    return img

def calculate_text_layout(lines_with_timing, content_font, title_font, big_font, draw):
    layout = []
    cumulative_y = 0
    
    for line_start, line_end, text, color, font_type in lines_with_timing:
        if not text.strip():
            cumulative_y += LINE_SPACING + 10
            layout.append((line_start, line_end, "", color, cumulative_y, LINE_SPACING, font_type))
            continue
        
        if font_type == "title":
            font = title_font
        elif font_type == "big":
            font = big_font
        else:
            font = content_font
        
        wrapped_lines = wrap_text_proper(text, font, draw)
        block_height = 0
        for wl in wrapped_lines:
            bbox = draw.textbbox((0, 0), wl, font=font)
            block_height += (bbox[3] - bbox[1]) + LINE_SPACING
        
        layout.append((line_start, line_end, text, color, cumulative_y, block_height, font_type))
        cumulative_y += block_height + 5
    
    return layout, cumulative_y

def main():
    global subtitle_segments
    
    os.makedirs(TIKTOK_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    print("🎬 Generating Valentine's Day Brain Rot TikTok Video")
    
    # Step 0: Lo-fi audio
    generate_lofi_background_audio()
    
    # Step 1: TTS
    audio_path = os.path.join(TIKTOK_DIR, "val_temp_audio.mp3")
    subs_path = os.path.join(TIKTOK_DIR, "val_temp_subs.vtt")
    print("  🔊 Generating voiceover...")
    generate_tts(VOICEOVER_TEXT, audio_path, subs_path)
    
    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path],
        capture_output=True, text=True
    )
    audio_duration = float(result.stdout.strip())
    # Ensure 60+ seconds
    if audio_duration < 60:
        audio_duration = 62.0
    print(f"  ⏱️  Duration: {audio_duration:.1f}s")
    
    subtitle_segments = parse_vtt(subs_path)
    
    # Load mfer
    mfer = None
    if os.path.exists(MFER_IMG):
        mfer = Image.open(MFER_IMG).convert('RGBA')
        print("  🎨 Loaded mfer #9581")
    
    # Build timing
    lines_with_timing = []
    for l in SCRIPT_LINES:
        font_type = l.get("size", "normal")
        lines_with_timing.append((l["time"], l.get("end", audio_duration), l["text"], l.get("color", "white"), font_type))
    
    # Pre-calculate layout
    temp_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    content_font = get_font(58, bold=True)
    title_font = get_font(72, bold=True)
    big_font = get_font(64, bold=True)
    text_layout, total_text_height = calculate_text_layout(lines_with_timing, content_font, title_font, big_font, temp_draw)
    print(f"  📏 Total text height: {total_text_height}px")
    
    # Generate frames
    total_frames = int(audio_duration * FPS) + FPS
    frames_dir = os.path.join(TIKTOK_DIR, "val_frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    print(f"  🖼️  Generating {total_frames} frames...")
    for i in range(total_frames):
        frame = create_frame(i, total_frames, lines_with_timing, text_layout, total_text_height,
                           mfer, audio_duration, content_font, title_font, big_font)
        # Save as PNG with alpha for compositing
        frame_rgb = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
        frame_rgb.paste(frame, (0, 0), frame)
        frame_rgb.save(os.path.join(frames_dir, f"frame_{i:05d}.png"))
        if i % (FPS * 5) == 0:
            print(f"    Frame {i}/{total_frames} ({i*100//total_frames}%)")
    
    # Encode text layer video
    print("  🎥 Encoding text layer...")
    text_video = os.path.join(TIKTOK_DIR, "val_text_video.mp4")
    
    # Pad audio to 60+ seconds if needed
    padded_audio = os.path.join(TIKTOK_DIR, "val_padded_audio.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_path,
        "-af", f"apad=whole_dur={audio_duration}",
        "-c:a", "libmp3lame", padded_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-i", padded_audio,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        text_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Mix in lofi background music
    print("  🎵 Mixing lo-fi background...")
    text_video_with_lofi = os.path.join(TIKTOK_DIR, "val_text_lofi.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", text_video, "-i", BG_AUDIO,
        "-filter_complex", "[1:a]volume=0.10[bg];[0:a][bg]amix=inputs=2:duration=shortest[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        text_video_with_lofi
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Composite over brain rot background
    print("  🧠 Compositing over brain rot background...")
    if os.path.exists(BRAIN_ROT_BG):
        # Darken the brain rot bg and overlay the text video using colorkey
        subprocess.run([
            "ffmpeg", "-y",
            "-i", BRAIN_ROT_BG,
            "-i", text_video_with_lofi,
            "-filter_complex",
            # Darken brain rot bg, then overlay text (colorkey removes black bg from text layer)
            "[0:v]eq=brightness=-0.3:saturation=0.7[bg];"
            "[1:v]colorkey=0x000000:0.25:0.15[fg];"
            "[bg][fg]overlay=0:0:shortest=1[out]",
            "-map", "[out]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            OUTPUT_PATH
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("  ⚠️  No brain rot background found, using text video directly")
        shutil.copy2(text_video_with_lofi, OUTPUT_PATH)
    
    # Cleanup
    print("  🧹 Cleaning up...")
    shutil.rmtree(frames_dir)
    for f in [audio_path, subs_path, text_video, text_video_with_lofi, padded_audio]:
        if os.path.exists(f):
            os.remove(f)
    
    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    
    # Verify duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", OUTPUT_PATH],
        capture_output=True, text=True
    )
    final_duration = float(result.stdout.strip())
    
    print(f"\n  ✅ DONE: {OUTPUT_PATH}")
    print(f"  📊 Size: {size_mb:.1f}MB | Duration: {final_duration:.1f}s")
    print(f"  {'✅' if final_duration >= 60 else '⚠️'} 60s+ requirement: {'MET' if final_duration >= 60 else 'NOT MET'}")

if __name__ == "__main__":
    main()
