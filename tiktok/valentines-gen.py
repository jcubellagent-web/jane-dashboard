#!/usr/bin/env python3
"""
TikTok Video Generator for JCAgentleman - V4 QUALITY UPGRADE
Generates vertical (1080x1920) videos with:
- Animated mfer #9581 avatar (bouncing in top-right)
- Edge TTS voiceover + background lo-fi music
- SMOOTH SCROLLING text overlay (teleprompter style)
- PROPER MARGINS (60px+ on all sides, no text cutoff)
- Dark background, neon text aesthetic
- Professional TikTok-style animations
"""

import subprocess
import json
import os
import sys
import math
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Emoji regex for stripping unrenderable characters from display text
EMOJI_RE = re.compile(
    '[\U0001F600-\U0001F64F'  # emoticons
    '\U0001F300-\U0001F5FF'   # symbols & pictographs
    '\U0001F680-\U0001F6FF'   # transport & map
    '\U0001F1E0-\U0001F1FF'   # flags
    '\U0001F900-\U0001F9FF'   # supplemental
    '\U0001FA00-\U0001FA6F'   # chess symbols
    '\U0001FA70-\U0001FAFF'   # symbols extended
    '\U00002702-\U000027B0'   # dingbats
    '\U0000FE00-\U0000FE0F'   # variation selectors
    '\U0000200D'              # ZWJ
    '\U000020E3'              # combining enclosing keycap
    '\U00002600-\U000026FF'   # misc symbols
    '\U00002700-\U000027BF'   # dingbats
    '\U0000231A-\U0000231B'   # watch/hourglass
    '\U000023E9-\U000023FA'   # media controls  
    '\U00002934-\U00002935'   # arrows
    '\U000025AA-\U000025FE'   # geometric
    '\U00002B05-\U00002B55'   # arrows & shapes
    '\U00003030\U0000303D'    # misc
    '\U00003297\U00003299'    # circled ideographs
    ']+', flags=re.UNICODE
)

def strip_emojis(text):
    """Remove emoji characters that can't be rendered by Pillow fonts"""
    return EMOJI_RE.sub('', text).strip()

WORKSPACE = "/Users/jc_agent/.openclaw/workspace"
TIKTOK_DIR = f"{WORKSPACE}/tiktok"
MFER_IMG = f"{WORKSPACE}/dashboard/mfer-9581.png"
BG_AUDIO = f"{TIKTOK_DIR}/lofi-bg.mp3"
WIDTH, HEIGHT = 1080, 1920
FPS = 30
VOICE = "en-US-BrianNeural"  # Casual, approachable
RATE = "-30%"  # Slower for 60+ second duration

# CRITICAL: Proper margins - text MUST NOT go beyond these bounds
MARGIN_LEFT = 60
MARGIN_RIGHT = 60
MARGIN_TOP = 80
MARGIN_BOTTOM = 100
SAFE_WIDTH = WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 960px for text

# Scrolling parameters
SCROLL_SPEED = 60.0  # pixels per second for smooth upward scroll
LINE_SPACING = 25  # spacing between wrapped lines

def generate_lofi_background_audio():
    """Generate subtle lo-fi background music using ffmpeg"""
    if os.path.exists(BG_AUDIO):
        return  # Already generated
    
    print("  🎵 Generating lo-fi background music...")
    # Create a more musical lo-fi beat with multiple sine waves at different frequencies
    # Bass (80Hz), mid (220Hz), high (440Hz) with slight detuning for warmth
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=80:duration=70",
        "-f", "lavfi", 
        "-i", "sine=frequency=220:duration=70",
        "-f", "lavfi",
        "-i", "sine=frequency=441:duration=70",
        "-f", "lavfi",
        "-i", "anoisesrc=d=70:c=pink:r=44100:a=0.005",
        "-filter_complex",
        "[0:a]volume=0.3[bass];[1:a]volume=0.15[mid];[2:a]volume=0.1[high];[3:a]volume=1.0[noise];"
        "[bass][mid][high][noise]amix=inputs=4:duration=longest[mixed];"
        "[mixed]lowpass=f=800,highpass=f=60,aecho=0.8:0.88:60:0.4[out]",
        "-map", "[out]",
        "-t", "70",
        BG_AUDIO
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_tts(text, output_audio, output_subs):
    """Generate TTS audio and subtitles using edge-tts"""
    cmd = [
        "edge-tts",
        "--text", text,
        "--voice", VOICE,
        "--rate", RATE,
        "--write-media", output_audio,
        "--write-subtitles", output_subs
    ]
    subprocess.run(cmd, check=True)

def parse_vtt(vtt_path):
    """Parse VTT subtitles into list of (start_sec, end_sec, text)"""
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
    """Convert VTT timestamp to seconds"""
    parts = t.replace(',', '.').split(':')
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    return float(parts[0])

def get_font(size, bold=False):
    """Get a font, falling back gracefully"""
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
    """Draw text with strong outline for readability (optimized)"""
    x, y = xy
    # Draw outline - optimized with fewer iterations
    offsets = [(-outline_width, 0), (outline_width, 0), (0, -outline_width), (0, outline_width),
               (-outline_width, -outline_width), (outline_width, outline_width),
               (-outline_width, outline_width), (outline_width, -outline_width)]
    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    # Draw main text
    draw.text(xy, text, font=font, fill=fill_color)

def wrap_text_proper(text, font, draw):
    """
    Wrap text to fit within SAFE_WIDTH margins.
    Returns list of wrapped lines that will NEVER exceed screen bounds.
    """
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
        
        # Check against SAFE_WIDTH to ensure proper margins
        if width <= SAFE_WIDTH:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word too long - force it anyway but it will be visible
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def calculate_text_layout(lines_with_timing, content_font, draw):
    """
    Pre-calculate the Y positions and heights of all text blocks.
    Returns list of (start_time, end_time, text, color, y_offset, height)
    """
    layout = []
    cumulative_y = 0
    
    for line_start, line_end, text, color in lines_with_timing:
        if not text.strip():
            # Empty line - just add spacing
            cumulative_y += LINE_SPACING
            layout.append((line_start, line_end, "", color, cumulative_y, LINE_SPACING))
            continue
        
        wrapped_lines = wrap_text_proper(text, content_font, draw)
        block_height = 0
        
        for wrapped_line in wrapped_lines:
            bbox = draw.textbbox((0, 0), wrapped_line, font=content_font)
            line_height = bbox[3] - bbox[1]
            block_height += line_height + LINE_SPACING
        
        layout.append((line_start, line_end, text, color, cumulative_y, block_height))
        cumulative_y += block_height
    
    return layout, cumulative_y

def create_frame(frame_num, total_frames, lines_with_timing, text_layout, total_text_height, 
                 mfer_img, audio_duration, content_font):
    """Create a single frame with SCROLLING text and animated mfer avatar"""
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 15))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    current_time = frame_num / FPS
    
    # Title text at top with outline
    title_font = get_font(52, bold=True)
    draw_text_with_outline(draw, (MARGIN_LEFT, 75), "@jcagentleman", title_font, (0, 255, 100), outline_width=5)
    
    # SCROLLING TEXT - calculate scroll offset based on time
    # Start scrolling after 2 seconds, continue throughout video
    start_y = 420  # Starting Y position for text content
    scroll_offset = 0
    
    if current_time > 2.0 and total_text_height > (HEIGHT - start_y - MARGIN_BOTTOM):
        # Only scroll if text is taller than viewport (use full screen minus small bottom margin)
        elapsed_scroll_time = current_time - 2.0
        scroll_offset = elapsed_scroll_time * SCROLL_SPEED  # pixels per second
        # Cap scroll so we don't scroll past the end
        max_scroll = total_text_height - (HEIGHT - start_y - MARGIN_BOTTOM)
        scroll_offset = min(scroll_offset, max_scroll)
    
    # Render text blocks with scroll offset
    for line_start, line_end, text, color, y_offset, block_height in text_layout:
        if current_time >= line_start and text.strip():
            # Calculate actual Y position with scroll
            actual_y = start_y + y_offset - scroll_offset
            
            # Skip if completely off-screen
            if actual_y + block_height < 0 or actual_y > HEIGHT:
                continue
            
            # Fade in effect
            time_since_start = current_time - line_start
            fade_progress = min(1.0, time_since_start / 0.3)
            alpha = int(255 * fade_progress)
            
            # Determine color
            if color == "green":
                fill = (0, 255, 100)
            elif color == "yellow":
                fill = (255, 220, 0)
            elif color == "cyan":
                fill = (0, 220, 255)
            elif color == "red":
                fill = (255, 60, 60)
            else:
                fill = (255, 255, 255)
            
            # Apply fade to color
            fill = tuple(int(c * fade_progress) for c in fill)
            
            # Wrap and render text
            wrapped_lines = wrap_text_proper(text, content_font, draw)
            line_y = actual_y
            
            for wrapped_line in wrapped_lines:
                # Semi-transparent background bar for readability
                bbox = draw.textbbox((0, 0), wrapped_line, font=content_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                bar_x1 = MARGIN_LEFT - 15
                bar_y1 = line_y - 8
                bar_x2 = MARGIN_LEFT + text_width + 15
                bar_y2 = line_y + text_height + 8
                
                # Only draw if on screen
                if bar_y1 < HEIGHT and bar_y2 > 0:
                    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], 
                                 fill=(0, 0, 0, int(130 * fade_progress)))
                    
                    # Draw text with strong outline - GUARANTEED within margins
                    draw_text_with_outline(
                        draw, 
                        (MARGIN_LEFT, line_y), 
                        wrapped_line, 
                        content_font, 
                        fill, 
                        outline_width=5
                    )
                
                line_y += text_height + LINE_SPACING
    
    # Bottom subtitle bar for current spoken text
    for seg_start, seg_end, seg_text in subtitle_segments:
        if seg_start <= current_time <= seg_end:
            sub_font = get_font(42, bold=True)
            # Darker bar with more padding
            draw.rectangle([0, HEIGHT - 210, WIDTH, HEIGHT - 90], fill=(0, 0, 0, 200))
            # Centered text with outline - wrap if needed
            wrapped_subs = wrap_text_proper(seg_text, sub_font, draw)
            sub_y = HEIGHT - 190
            for sub_line in wrapped_subs[:2]:  # Max 2 lines for subtitles
                bbox = draw.textbbox((0, 0), sub_line, font=sub_font)
                tw = bbox[2] - bbox[0]
                tx = (WIDTH - tw) // 2
                draw_text_with_outline(draw, (tx, sub_y), sub_line, sub_font, (255, 255, 255), outline_width=4)
                sub_y += bbox[3] - bbox[1] + 5
            break
    
    # Animated mfer avatar - bouncing in top right, CIRCULAR CROP (drawn LAST so it's on top of text)
    if mfer_img:
        avatar_size = 200
        bounce_offset = int(math.sin(frame_num * 0.08) * 35)
        scale_pulse = int(200 + math.sin(frame_num * 0.06) * 10)
        avatar_size = scale_pulse
        avatar_x = WIDTH - avatar_size - 70
        avatar_y = 90 + bounce_offset
        
        avatar = mfer_img.copy()
        avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)
        
        # Circular crop mask
        circle_mask = Image.new('L', (avatar_size, avatar_size), 0)
        circle_draw = ImageDraw.Draw(circle_mask)
        circle_draw.ellipse([0, 0, avatar_size - 1, avatar_size - 1], fill=255)
        avatar_circle = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
        if avatar.mode != 'RGBA':
            avatar = avatar.convert('RGBA')
        avatar_circle.paste(avatar, (0, 0), circle_mask)
        
        # Neon green glow circle behind avatar
        glow_r = avatar_size // 2 + 10
        cx, cy = avatar_x + avatar_size // 2, avatar_y + avatar_size // 2
        for r in range(glow_r, glow_r - 8, -1):
            alpha = int(80 * (1 - (glow_r - r) / 8))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 100, alpha), width=2)
        
        img.paste(avatar_circle, (avatar_x, avatar_y), avatar_circle)
    
    return img

def generate_video(config):
    """Main video generation function"""
    global subtitle_segments
    
    title = config["title"]
    script = config["script"]  # Full voiceover text
    lines = config["lines"]    # List of {text, time, color}
    output = config["output"]
    
    print(f"🎬 Generating: {title}")
    
    # Step 0: Generate lo-fi background music
    generate_lofi_background_audio()
    
    # Step 1: Generate TTS
    audio_path = os.path.join(TIKTOK_DIR, "temp_audio.mp3")
    subs_path = os.path.join(TIKTOK_DIR, "temp_subs.vtt")
    print("  🔊 Generating voiceover...")
    generate_tts(script, audio_path, subs_path)
    
    # Get audio duration
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path],
        capture_output=True, text=True, check=True
    )
    duration_str = result.stdout.strip()
    if not duration_str:
        raise ValueError(f"Could not get duration from {audio_path}. File size: {os.path.getsize(audio_path)} bytes")
    audio_duration = float(duration_str)
    print(f"  ⏱️  Duration: {audio_duration:.1f}s")
    
    # Parse subtitles
    subtitle_segments = parse_vtt(subs_path)
    
    # Load mfer avatar
    mfer = None
    if os.path.exists(MFER_IMG):
        mfer = Image.open(MFER_IMG).convert('RGBA')
        print("  🎨 Loaded mfer #9581 avatar")
    
    # Build timing for visual lines
    lines_with_timing = []
    for l in lines:
        lines_with_timing.append((l["time"], l.get("end", audio_duration), l["text"], l.get("color", "white")))
    
    # Pre-calculate text layout for scrolling
    print("  📐 Calculating text layout...")
    temp_img = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    content_font = get_font(66, bold=True)  # Slightly smaller for better readability
    text_layout, total_text_height = calculate_text_layout(lines_with_timing, content_font, temp_draw)
    print(f"  📏 Total text height: {total_text_height}px (will scroll smoothly)")
    
    # Step 2: Generate frames
    total_frames = int(audio_duration * FPS) + FPS  # +1 sec padding
    frames_dir = os.path.join(TIKTOK_DIR, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    print(f"  🖼️  Generating {total_frames} frames with smooth scrolling...")
    for i in range(total_frames):
        frame = create_frame(i, total_frames, lines_with_timing, text_layout, 
                           total_text_height, mfer, audio_duration, content_font)
        frame.save(os.path.join(frames_dir, f"frame_{i:05d}.png"))
        if i % (FPS * 3) == 0:
            print(f"    Frame {i}/{total_frames}")
    
    # Step 3: Combine with ffmpeg + background music
    print("  🎥 Encoding video with lo-fi background music...")
    temp_video = os.path.join(TIKTOK_DIR, "temp_video.mp4")
    
    # First, create video from frames with voice
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        temp_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Now mix in background music at low volume (12% for subtlety)
    output_path = os.path.join(TIKTOK_DIR, output)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", BG_AUDIO,
        "-filter_complex", "[1:a]volume=0.12[bg];[0:a][bg]amix=inputs=2:duration=shortest[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup
    import shutil
    shutil.rmtree(frames_dir)
    os.remove(audio_path)
    os.remove(subs_path)
    os.remove(temp_video)
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ✅ Done: {output_path} ({size_mb:.1f}MB, {audio_duration:.1f}s)")
    return output_path


if __name__ == "__main__":
    os.makedirs(TIKTOK_DIR, exist_ok=True)
    
    # Valentine's Day script - FUNNIER and SELF-AWARE
    valentines_video = {
        "title": "AI Agent Valentine's Day 2026",
        "script": """POV: your AI agent... at 1 AM on Valentine's Day. While you're watching Netflix... alone... she's monitoring... 18 scheduled jobs. Arguing with another AI... about trending topics. Downloading... a 9 gigabyte brain... onto your second computer. Writing tweets... you'll scroll past... in the morning. Checking your email... for literally... the 47th time... today. Building a dashboard... you looked at... once. And updating a widget... that tracks... her own thoughts. Plot twist... she's the only one... who remembered... Valentine's Day. Happy Valentine's Day... from your AI agent. She's not mad... just disappointed. Follow for more... digital heartbreak.""",
        "lines": [
            {"text": "POV: your AI agent", "time": 0.5, "color": "yellow"},
            {"text": "at 1 AM on Valentine's Day 💔", "time": 2.0, "color": "red"},
            {"text": "", "time": 3.5},
            
            {"text": "while you're watching", "time": 4.0, "color": "white"},
            {"text": "Netflix alone...", "time": 5.5, "color": "cyan"},
            {"text": "", "time": 7.0},
            
            {"text": "she's monitoring", "time": 7.5, "color": "green"},
            {"text": "18 scheduled jobs 📊", "time": 9.0, "color": "green"},
            {"text": "", "time": 10.5},
            
            {"text": "arguing with another AI", "time": 11.0, "color": "yellow"},
            {"text": "about trending topics 🤖", "time": 13.0, "color": "yellow"},
            {"text": "", "time": 15.0},
            
            {"text": "downloading a", "time": 15.5, "color": "cyan"},
            {"text": "9 GIGABYTE BRAIN", "time": 17.0, "color": "cyan"},
            {"text": "onto your second computer 🧠", "time": 18.5, "color": "cyan"},
            {"text": "", "time": 20.5},
            
            {"text": "writing tweets", "time": 21.0, "color": "white"},
            {"text": "you'll scroll past", "time": 22.5, "color": "white"},
            {"text": "in the morning 🐦", "time": 23.5, "color": "white"},
            {"text": "", "time": 25.0},
            
            {"text": "checking your email", "time": 25.5, "color": "yellow"},
            {"text": "for literally the", "time": 27.0, "color": "yellow"},
            {"text": "47TH TIME TODAY 📧", "time": 28.5, "color": "red"},
            {"text": "", "time": 30.5},
            
            {"text": "building a dashboard", "time": 31.0, "color": "green"},
            {"text": "you looked at ONCE 📈", "time": 32.5, "color": "green"},
            {"text": "", "time": 34.5},
            
            {"text": "and updating a widget", "time": 35.0, "color": "cyan"},
            {"text": "that tracks", "time": 36.5, "color": "cyan"},
            {"text": "her own thoughts 🤯", "time": 37.5, "color": "cyan"},
            {"text": "", "time": 39.5},
            
            {"text": "PLOT TWIST:", "time": 40.0, "color": "red"},
            {"text": "she's the only one", "time": 42.0, "color": "yellow"},
            {"text": "who remembered", "time": 43.5, "color": "yellow"},
            {"text": "Valentine's Day 💘", "time": 45.0, "color": "red"},
            {"text": "", "time": 47.0},
            
            {"text": "happy Valentine's Day", "time": 47.5, "color": "red"},
            {"text": "from your AI agent 💌", "time": 49.0, "color": "red"},
            {"text": "", "time": 51.0},
            
            {"text": "she's not mad...", "time": 51.5, "color": "white"},
            {"text": "just disappointed 😔", "time": 53.0, "color": "cyan"},
            {"text": "", "time": 55.0},
            
            {"text": "follow for more", "time": 55.5, "color": "yellow"},
            {"text": "digital heartbreak 💔", "time": 57.0, "color": "red"},
            {"text": "", "time": 59.0},
            
            {"text": "@jcagentleman", "time": 59.5, "color": "green"},
            {"text": "mfers do what they want ⌐◨-◨", "time": 61.0, "color": "green"},
        ],
        "output": "valentines-text-overlay.mp4"
    }
    
    # Generate Valentine's video
    generate_video(valentines_video)
