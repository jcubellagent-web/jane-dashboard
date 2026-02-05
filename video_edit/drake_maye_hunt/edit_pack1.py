#!/usr/bin/env python3
"""
Drake Maye Hunt EP.7 - Pack 1 Edit
Cards: Jimmy Graham, Jordan Davis, Marquise Brown, Chris Long
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Paths
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt"
INPUT = f"{WORK_DIR}/pack1_raw.mp4"
OUTPUT = f"{WORK_DIR}/EP7_DRAFT.mp4"

# Card reveals (approximate times in the 43s clip, will adjust after speedup)
# Original: 43s → 30s = 0.70x PTS (1.43x speed)
CARDS = [
    {"name": "Jimmy Graham", "serial": "71/79", "rarity": "RARE", "floor": "$2"},
    {"name": "Jordan Davis", "serial": "34/397", "rarity": "UNCOMMON", "floor": "$1"},
    {"name": "Marquise Brown", "serial": "46/199", "rarity": "RARE", "floor": "$2"},
    {"name": "Chris Long", "serial": "111/218", "rarity": "UNCOMMON", "floor": "$1"},
]

# ASS subtitle file for overlays
ASS_CONTENT = """[Script Info]
Title: Drake Maye Hunt EP.7
ScriptType: v4.00+
PlayResX: 384
PlayResY: 832
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,SF Pro Display,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,8,10,10,30,1
Style: Subtitle,SF Pro Display,24,&H0000D4FF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,8,10,10,60,1
Style: Card,SF Pro Display,22,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,450,1
Style: Floor,SF Pro Display,20,&H0080FF80,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,490,1
Style: Rare,SF Pro Display,22,&H0000D4FF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,2,10,10,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,DRAKE MAYE HUNT EP.7
Dialogue: 0,0:00:00.00,0:00:05.00,Subtitle,,0,0,0,,2024 Panini Select
Dialogue: 0,0:00:08.00,0:00:12.00,Card,,0,0,0,,Jimmy Graham 71/79
Dialogue: 0,0:00:08.00,0:00:12.00,Floor,,0,0,0,,RARE - FLOOR: $2
Dialogue: 0,0:00:14.00,0:00:18.00,Card,,0,0,0,,Jordan Davis 34/397
Dialogue: 0,0:00:14.00,0:00:18.00,Floor,,0,0,0,,UNCOMMON - FLOOR: $1
Dialogue: 0,0:00:20.00,0:00:24.00,Card,,0,0,0,,Marquise Brown 46/199
Dialogue: 0,0:00:20.00,0:00:24.00,Floor,,0,0,0,,RARE - FLOOR: $2
Dialogue: 0,0:00:26.00,0:00:30.00,Card,,0,0,0,,Chris Long 111/218
Dialogue: 0,0:00:26.00,0:00:30.00,Floor,,0,0,0,,UNCOMMON - FLOOR: $1
Dialogue: 0,0:00:26.00,0:00:30.00,Title,,0,0,30,,PACK VALUE: ~$6
"""

def main():
    os.chdir(WORK_DIR)
    
    # Write ASS file
    with open("overlays.ass", "w") as f:
        f.write(ASS_CONTENT)
    
    # Speed up video and add overlays
    cmd = [
        "ffmpeg", "-y",
        "-i", INPUT,
        "-filter_complex",
        "[0:v]setpts=0.70*PTS,ass=overlays.ass[v];[0:a]atempo=1.43[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-t", "30",
        OUTPUT
    ]
    
    print("Running ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    
    print(f"Created: {OUTPUT}")

if __name__ == "__main__":
    main()
