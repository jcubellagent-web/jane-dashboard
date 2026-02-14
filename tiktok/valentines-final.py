#!/usr/bin/env python3
"""
Valentine's TikTok - PIL frames at HALF resolution (540x960) then upscale.
Fast text rendering with minimal outline.
"""
import subprocess
import os
import sys
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = "/Users/jc_agent/.openclaw/workspace"
TIKTOK_DIR = f"{WORKSPACE}/tiktok"
MFER_IMG = f"{WORKSPACE}/dashboard/mfer-9581.png"
BG_AUDIO = f"{TIKTOK_DIR}/lofi-bg.mp3"
BRAIN_ROT_BG = f"{TIKTOK_DIR}/brain-rot-bg.mp4"
OUTPUT_PATH = os.path.join(WORKSPACE, "..", "media", "outbound", "tiktok-degen-valentines.mp4")

# Half res for speed, upscale later
W, H = 540, 960
FPS = 24  # Lower FPS for speed
VOICE = "en-US-BrianNeural"

VOICEOVER = (
    "POV: your AI agent on Valentine's Day. "
    "While you're watching Netflix alone... "
    "she's monitoring 18 scheduled jobs. "
    "Arguing with another AI about trending topics. "
    "Downloading a 9 gigabyte brain onto your second computer. "
    "Writing tweets you'll scroll past in the morning. "
    "Checking your email for literally the 47th time today. "
    "Building a dashboard you looked at once. "
    "And updating a widget that tracks her own thoughts. "
    "Plot twist. She's the only one who remembered Valentine's Day. "
    "Happy Valentine's Day from your AI agent. "
    "She's not mad. Just disappointed. "
    "Follow for more digital heartbreak."
)

# (start, end, line1, line2, color_rgb)
CARDS = [
    (0.0, 3.5, "POV: your AI agent", "on Valentine's Day", (0, 255, 100)),
    (3.5, 7.0, "while you're watching", "Netflix alone...", (255, 255, 255)),
    (7.0, 10.5, "she's monitoring", "18 scheduled jobs", (0, 220, 255)),
    (10.5, 15.0, "arguing with another AI", "about trending topics", (255, 220, 0)),
    (15.0, 19.5, "downloading a 9GB brain", "onto your second computer", (0, 220, 255)),
    (19.5, 23.5, "writing tweets you'll", "scroll past in the morning", (255, 255, 255)),
    (23.5, 27.5, "checking your email", "for the 47th time today", (255, 220, 0)),
    (27.5, 31.0, "building a dashboard", "you looked at once", (255, 255, 255)),
    (31.0, 35.0, "and updating a widget", "that tracks her own thoughts", (0, 220, 255)),
    (35.0, 36.5, "plot twist:", "", (255, 80, 100)),
    (36.5, 41.0, "she's the only one who", "remembered Valentine's Day", (255, 80, 100)),
    (41.0, 46.0, "happy Valentine's Day", "from your AI agent", (0, 255, 100)),
    (46.0, 50.0, "she's not mad", "just disappointed", (255, 220, 0)),
    (50.0, 54.0, "follow for more", "digital heartbreak", (0, 255, 100)),
    (54.0, 62.0, "@jcagentleman", "", (0, 255, 100)),
]

def get_font(size):
    for fp in ["/System/Library/Fonts/Helvetica.ttc",
               "/System/Library/Fonts/HelveticaNeue.ttc",
               "/Library/Fonts/Arial Bold.ttf"]:
        if os.path.exists(fp):
            try: return ImageFont.truetype(fp, size)
            except: continue
    return ImageFont.load_default()

def outline_text(draw, x, y, text, font, fill, ow=3):
    """Fast outline - just 4 cardinal directions"""
    bc = (0, 0, 0)
    draw.text((x-ow, y), text, font=font, fill=bc)
    draw.text((x+ow, y), text, font=font, fill=bc)
    draw.text((x, y-ow), text, font=font, fill=bc)
    draw.text((x, y+ow), text, font=font, fill=bc)
    draw.text((x, y), text, font=font, fill=fill)

def generate_lofi():
    if os.path.exists(BG_AUDIO):
        return
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

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print("Valentine's Brain Rot TikTok")
    
    # TTS
    audio_path = os.path.join(TIKTOK_DIR, "val_voice.mp3")
    subs_path = os.path.join(TIKTOK_DIR, "val_subs.vtt")
    print("  Generating voiceover...")
    subprocess.run([
        "edge-tts", "--text", VOICEOVER, "--voice", VOICE, "--rate", "+5%",
        "--write-media", audio_path, "--write-subtitles", subs_path
    ], check=True)
    
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path],
        capture_output=True, text=True
    )
    audio_dur = float(result.stdout.strip())
    video_dur = max(62.0, audio_dur + 2)
    print(f"  Audio: {audio_dur:.1f}s, Video: {video_dur:.1f}s")
    
    generate_lofi()
    
    # Load mfer
    mfer = None
    if os.path.exists(MFER_IMG):
        mfer_raw = Image.open(MFER_IMG).convert('RGBA')
        size = 90  # half res
        mfer_raw = mfer_raw.resize((size, size), Image.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
        mfer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        mfer.paste(mfer_raw, (0, 0), mask)
    
    # Fonts (half size)
    title_font = get_font(34)
    body_font = get_font(28)
    handle_font = get_font(22)
    
    # Generate frames
    total_frames = int(video_dur * FPS) + FPS
    frames_dir = os.path.join(TIKTOK_DIR, "val_frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    print(f"  Generating {total_frames} frames at {W}x{H}...")
    
    for i in range(total_frames):
        t = i / FPS
        img = Image.new('RGB', (W, H), (10, 10, 15))
        draw = ImageDraw.Draw(img)
        
        # Handle
        outline_text(draw, 35, 35, "@jcagentleman", handle_font, (0, 255, 100), 2)
        
        # Current card
        for start, end, line1, line2, color in CARDS:
            if start <= t < end:
                # Fade calc
                fade = min(1.0, (t - start) / 0.3)
                c = tuple(int(v * fade) for v in color)
                
                # Semi-transparent box behind text
                box_y = 185
                box_h = 80 if line2 else 45
                draw.rectangle([20, box_y, W-20, box_y + box_h], fill=(0, 0, 0, 160) if fade > 0.5 else (0, 0, 0, 80))
                
                # Center text
                bbox1 = draw.textbbox((0, 0), line1, font=title_font)
                tw1 = bbox1[2] - bbox1[0]
                outline_text(draw, (W - tw1) // 2, 190, line1, title_font, c, 3)
                
                if line2:
                    bbox2 = draw.textbbox((0, 0), line2, font=body_font)
                    tw2 = bbox2[2] - bbox2[0]
                    outline_text(draw, (W - tw2) // 2, 230, line2, body_font, c, 3)
                break
        
        # Mfer avatar bouncing top-right
        if mfer:
            bounce = int(math.sin(i * 0.08) * 12)
            ax = W - 100 - 10
            ay = 25 + bounce
            img.paste(mfer, (ax, ay), mfer)
        
        img.save(os.path.join(frames_dir, f"f_{i:05d}.jpg"), quality=85)
        
        if i % (FPS * 5) == 0:
            pct = i * 100 // total_frames
            print(f"    Frame {i}/{total_frames} ({pct}%)", flush=True)
    
    print("  Encoding text layer video...")
    text_video = os.path.join(TIKTOK_DIR, "val_text.mp4")
    
    # Pad audio
    padded = os.path.join(TIKTOK_DIR, "val_padded.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_path,
        "-af", f"apad=whole_dur={video_dur}",
        "-c:a", "libmp3lame", "-q:a", "2", padded
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Encode at half res
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f_%05d.jpg"),
        "-i", padded,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        text_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Mix lofi
    text_lofi = os.path.join(TIKTOK_DIR, "val_text_lofi.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", text_video, "-i", BG_AUDIO,
        "-filter_complex", "[1:a]volume=0.10[bg];[0:a][bg]amix=inputs=2:duration=shortest[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        text_lofi
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Composite: upscale text video to 1080x1920, overlay on darkened brain rot bg via colorkey
    print("  Compositing over brain rot background...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", BRAIN_ROT_BG,
        "-i", text_lofi,
        "-filter_complex",
        "[0:v]eq=brightness=-0.3:saturation=0.6,scale=1080:1920[bg];"
        "[1:v]scale=1080:1920[fg_scaled];"
        "[fg_scaled]colorkey=0x0A0A0F:0.15:0.1[fg];"
        "[bg][fg]overlay=0:0:shortest=1[out]",
        "-map", "[out]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "copy",
        "-t", str(video_dur),
        OUTPUT_PATH
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup
    print("  Cleaning up...")
    shutil.rmtree(frames_dir)
    for f in [audio_path, subs_path, padded, text_video, text_lofi]:
        if os.path.exists(f):
            os.remove(f)
    
    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", OUTPUT_PATH],
        capture_output=True, text=True
    )
    final_dur = float(result.stdout.strip())
    print(f"\n  DONE: {OUTPUT_PATH}")
    print(f"  Size: {size_mb:.1f}MB | Duration: {final_dur:.1f}s")
    print(f"  60s+: {'MET' if final_dur >= 60 else 'NOT MET'}")

if __name__ == "__main__":
    main()
