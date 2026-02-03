#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - Video Creator v2
Using FFmpeg drawtext filter for reliability
"""

import subprocess
import os

# Paths
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
OUTPUT = os.path.join(WORK_DIR, "drake_maye_hunt_ep8_final.mp4")

# Video timing
SPEED_FACTOR = 1.28  # 38s -> 30s
PTS_FACTOR = 0.78

# Text overlays using drawtext
# Format: (start, end, text, y_position, fontsize, color_hex)
TEXTS = [
    # Title
    (0, 5, "DRAKE MAYE HUNT EP.8", "h*0.08", 42, "white"),
    (0, 5, "PATS TO THE SUPER BOWL", "h*0.15", 28, "gold"),
    
    # Card 1: Howie Long (reveals ~8s, text at 9s)
    (9, 12, "Howie Long 185/397", "h*0.72", 30, "white"),
    (9, 12, "UNCOMMON - FLOOR: $1", "h*0.78", 24, "lime"),
    
    # Card 2: Dre Greenlaw ULTRA RARE (reveals ~11s, text at 12s)
    (12, 16, "Dre Greenlaw 13/49", "h*0.68", 34, "orange"),
    (12, 16, "ULTRA RARE - FLOOR: $7", "h*0.75", 28, "red"),
    
    # Card 3: Tip Reiman (reveals ~17s, text at 18s)
    (18, 21, "Tip Reiman 210/218", "h*0.72", 30, "white"),
    (18, 21, "UNCOMMON - FLOOR: $1", "h*0.78", 24, "lime"),
    
    # Card 4: Marquise Brown EPIC (reveals ~27s, text at 28s)
    (27, 30, "Marquise Brown 3/10", "h*0.65", 36, "magenta"),
    (27, 30, "EPIC - FLOOR: $15", "h*0.72", 30, "magenta"),
    
    # Pack total
    (28, 30, "PACK VALUE: $24", "h*0.82", 28, "lime"),
    (28, 30, "THE HUNT CONTINUES!", "h*0.88", 22, "white"),
]

def build_drawtext_filter():
    """Build FFmpeg drawtext filter string"""
    filters = []
    
    for start, end, text, y_pos, fontsize, color in TEXTS:
        # Escape special characters
        text_escaped = text.replace(":", "\\:").replace("'", "\\'")
        
        # drawtext filter
        dt = (
            f"drawtext=text='{text_escaped}':"
            f"fontsize={fontsize}:"
            f"fontcolor={color}:"
            f"x=(w-text_w)/2:"
            f"y={y_pos}:"
            f"enable='between(t,{start},{end})':"
            f"shadowcolor=black:shadowx=2:shadowy=2"
        )
        filters.append(dt)
    
    return ",".join(filters)

def main():
    os.chdir(WORK_DIR)
    
    print("🎬 Creating Drake Maye Hunt EP.8 (v2)...")
    print("   Ultra Rare Dre Greenlaw + Epic Marquise Brown!")
    
    # Build filter complex
    speed_filter = f"setpts={PTS_FACTOR}*PTS"
    text_filters = build_drawtext_filter()
    video_filter = f"{speed_filter},{text_filters}"
    audio_filter = f"atempo={SPEED_FACTOR}"
    
    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-i', SOURCE,
        '-vf', video_filter,
        '-af', audio_filter,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '20',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-t', '30',
        OUTPUT
    ]
    
    print("\n📹 Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Check file size
        size = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n✅ Success! Video: {OUTPUT}")
        print(f"   Size: {size:.1f} MB")
        print(f"   Duration: 30 seconds")
    else:
        print(f"\n❌ Error: {result.stderr[:1000]}")
        return None
    
    return OUTPUT

if __name__ == "__main__":
    main()
