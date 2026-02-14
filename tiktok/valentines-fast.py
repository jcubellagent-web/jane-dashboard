#!/usr/bin/env python3
"""
Fast Valentine's TikTok generator - writes filter_complex to file to avoid escaping hell.
"""
import subprocess
import os
from PIL import Image, ImageDraw

WORKSPACE = "/Users/jc_agent/.openclaw/workspace"
TIKTOK_DIR = f"{WORKSPACE}/tiktok"
MFER_IMG = f"{WORKSPACE}/dashboard/mfer-9581.png"
BG_AUDIO = f"{TIKTOK_DIR}/lofi-bg.mp3"
BRAIN_ROT_BG = f"{TIKTOK_DIR}/brain-rot-bg.mp4"
OUTPUT_PATH = os.path.join(WORKSPACE, "..", "media", "outbound", "tiktok-degen-valentines.mp4")
VOICE = "en-US-BrianNeural"

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
    "Plot twist. She's the only one who remembered Valentine's Day. "
    "Happy Valentine's Day from your AI agent. "
    "She's not mad. Just disappointed. "
    "Follow for more digital heartbreak."
)

# (start, end, text, y, fontsize, color_hex) - NO apostrophes, use unicode
LINES = [
    (0.0, 3.5, "POV\\: your AI agent", 380, 68, "0x00FF64"),
    (0.0, 3.5, "on Valentines Day", 460, 68, "0x00FF64"),
    (3.5, 7.0, "while youre watching", 380, 56, "0xFFFFFF"),
    (3.5, 7.0, "Netflix alone...", 445, 56, "0xFFFFFF"),
    (7.0, 10.5, "shes monitoring", 380, 56, "0x00DCFF"),
    (7.0, 10.5, "18 scheduled jobs", 445, 56, "0x00DCFF"),
    (10.5, 15.0, "arguing with another AI", 380, 52, "0xFFDC00"),
    (10.5, 15.0, "about trending topics", 445, 52, "0xFFDC00"),
    (15.0, 19.5, "downloading a 9 gigabyte brain", 380, 48, "0x00DCFF"),
    (15.0, 19.5, "onto your second computer", 445, 48, "0x00DCFF"),
    (19.5, 23.5, "writing tweets youll", 380, 56, "0xFFFFFF"),
    (19.5, 23.5, "scroll past in the morning", 445, 56, "0xFFFFFF"),
    (23.5, 27.5, "checking your email for literally", 380, 46, "0xFFDC00"),
    (23.5, 27.5, "the 47th time today", 445, 46, "0xFFDC00"),
    (27.5, 31.0, "building a dashboard", 380, 56, "0xFFFFFF"),
    (27.5, 31.0, "you looked at once", 445, 56, "0xFFFFFF"),
    (31.0, 35.0, "and updating a widget", 380, 52, "0x00DCFF"),
    (31.0, 35.0, "that tracks her own thoughts", 445, 52, "0x00DCFF"),
    (35.0, 36.5, "plot twist\\:", 400, 64, "0xFF5064"),
    (36.5, 41.0, "shes the only one who", 370, 58, "0xFF5064"),
    (36.5, 41.0, "remembered Valentines Day", 445, 58, "0xFF5064"),
    (41.0, 46.0, "happy Valentines Day", 370, 60, "0x00FF64"),
    (41.0, 46.0, "from your AI agent", 445, 60, "0x00FF64"),
    (46.0, 50.0, "shes not mad", 380, 56, "0xFFFFFF"),
    (46.0, 50.0, "just disappointed", 455, 56, "0xFFDC00"),
    (50.0, 54.0, "follow for more", 380, 56, "0x00FF64"),
    (50.0, 54.0, "digital heartbreak", 450, 56, "0x00FF64"),
    (54.0, 62.0, "@jcagentleman", 410, 64, "0x00FF64"),
]

def create_mfer_overlay():
    avatar_path = os.path.join(TIKTOK_DIR, "mfer_circle.png")
    size = 180
    mfer = Image.open(MFER_IMG).convert('RGBA').resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    out = Image.new('RGBA', (size + 16, size + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    cx, cy = (size + 16) // 2, (size + 16) // 2
    for r in range(size//2 + 8, size//2, -1):
        alpha = int(150 * (1 - (r - size//2) / 8))
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(0, 255, 100, alpha), width=2)
    circ = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    circ.paste(mfer, (0, 0), mask)
    out.paste(circ, (8, 8), circ)
    out.save(avatar_path)
    return avatar_path

def generate_lofi():
    if os.path.exists(BG_AUDIO):
        return
    print("  Generating lo-fi background...")
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

def find_font():
    for fp in ["/System/Library/Fonts/Helvetica.ttc",
               "/System/Library/Fonts/HelveticaNeue.ttc",
               "/Library/Fonts/Arial Bold.ttf"]:
        if os.path.exists(fp):
            return fp
    return "/System/Library/Fonts/Supplemental/Arial.ttf"

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print("Valentine's Brain Rot TikTok - FAST mode")
    
    # TTS
    audio_path = os.path.join(TIKTOK_DIR, "val_voice.mp3")
    subs_path = os.path.join(TIKTOK_DIR, "val_subs.vtt")
    print("  Generating voiceover...")
    subprocess.run([
        "edge-tts", "--text", VOICEOVER_TEXT, "--voice", VOICE, "--rate", "+5%",
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
    
    print("  Creating mfer avatar...")
    mfer_path = create_mfer_overlay()
    
    font = find_font()
    print(f"  Font: {font}")
    
    # Pad audio
    padded = os.path.join(TIKTOK_DIR, "val_padded.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_path,
        "-af", f"apad=whole_dur={video_dur}",
        "-c:a", "libmp3lame", "-q:a", "2", padded
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Mix voice + lofi
    mixed = os.path.join(TIKTOK_DIR, "val_mixed.m4a")
    subprocess.run([
        "ffmpeg", "-y", "-i", padded, "-i", BG_AUDIO,
        "-filter_complex",
        "[1:a]volume=0.10[bg];[0:a][bg]amix=inputs=2:duration=first[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "192k", mixed
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Write filter_complex_script to a file (avoids shell escaping nightmare)
    filter_file = os.path.join(TIKTOK_DIR, "val_filter.txt")
    
    lines = []
    # Darken brain rot
    lines.append("[0:v]eq=brightness=-0.25:saturation=0.6[bg];")
    
    prev = "bg"
    idx = 0
    
    # Static handle
    lines.append(
        f"[{prev}]drawtext=fontfile='{font}':"
        f"text='@jcagentleman':"
        f"fontsize=44:fontcolor=0x00FF64:borderw=5:bordercolor=black:"
        f"x=70:y=65[t{idx}];"
    )
    prev = f"t{idx}"; idx += 1
    
    # Static valentine label  
    lines.append(
        f"[{prev}]drawtext=fontfile='{font}':"
        f"text='Valentines Day':"
        f"fontsize=36:fontcolor=0xFF6496:borderw=4:bordercolor=black:"
        f"x=490:y=68[t{idx}];"
    )
    prev = f"t{idx}"; idx += 1
    
    # Script lines - simple enable (no alpha fade, much cleaner)
    for start, end, text, y, fsize, color in LINES:
        lines.append(
            f"[{prev}]drawtext=fontfile='{font}':"
            f"text='{text}':"
            f"fontsize={fsize}:fontcolor={color}:borderw=5:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:"
            f"enable='between(t,{start},{end})'[t{idx}];"
        )
        prev = f"t{idx}"; idx += 1
    
    # Avatar overlay
    lines.append(f"[2:v]scale=196:-1[avatar];")
    lines.append(f"[{prev}][avatar]overlay=W-220:60+25*sin(t*0.5):shortest=1[out]")
    
    filter_text = "\n".join(lines)
    with open(filter_file, 'w') as f:
        f.write(filter_text)
    
    print(f"  Filter written to {filter_file}")
    print("  Composing final video...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", BRAIN_ROT_BG,
        "-i", mixed,
        "-i", mfer_path,
        "-filter_complex_script", filter_file,
        "-map", "[out]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "copy",
        "-t", str(video_dur),
        OUTPUT_PATH
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup
    for f in [audio_path, subs_path, padded, mixed, mfer_path, filter_file]:
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
    print(f"  60s+ requirement: {'MET' if final_dur >= 60 else 'NOT MET'}")

if __name__ == "__main__":
    main()
