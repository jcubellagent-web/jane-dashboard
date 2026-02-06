#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - TikTok Edit (Fast version using FFmpeg filters)
60-second montage with Drake Maye EPIC 9/10 as the climax!
"""

import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
INPUT = "/Users/jc_agent/.openclaw/media/inbound/9e9fdcf1-a657-40e6-8eae-9f769b4d618b.mp4"
FINAL = f"{WORK_DIR}/EP8_FINAL.mp4"

# Key segments to extract and their durations after speed adjustment
# Format: (start_sec, end_sec, speed_factor)
SEGMENTS = [
    (0, 5, 1.0),           # Intro - 5s
    (30, 38, 1.5),         # Pack 1: Andy Reid - 5.3s
    (55, 75, 1.5),         # Pack 2: Triple EPIC Penix - 13.3s
    (85, 95, 1.5),         # Pack 3: Brock Bowers - 6.7s
    (100, 115, 2.0),       # Pack 4: Xavien Howard - 7.5s
    (120, 130, 2.5),       # Pack 5: Dre Greenlaw - 4s
    (188, 200, 1.5),       # Drake tease - 8s
    (225, 241, 0.8),       # FINALE - 20s (slowed for impact)
]
# Total ~70s - will trim to 60s

def get_duration(file):
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def main():
    os.chdir(WORK_DIR)
    
    print("Step 1: Creating speed-adjusted segments...")
    segment_files = []
    
    for i, (start, end, speed) in enumerate(SEGMENTS):
        print(f"  Segment {i+1}: {start}s-{end}s at {speed}x speed")
        segment_output = f"seg_{i:02d}.mp4"
        
        # Calculate PTS multiplier (inverse of speed)
        setpts = 1.0 / speed
        
        # Handle atempo range (0.5-2.0)
        if speed <= 2:
            atempo = f"atempo={speed}"
        else:
            atempo = f"atempo=2.0,atempo={speed/2}"
        
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start), "-to", str(end), "-i", INPUT,
            "-filter_complex", f"[0:v]setpts={setpts}*PTS[v];[0:a]{atempo}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "128k",
            segment_output
        ], capture_output=True)
        
        segment_files.append(segment_output)
    
    print("\nStep 2: Concatenating segments...")
    with open("concat.txt", "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt",
        "-c", "copy", "combined.mp4"
    ], capture_output=True)
    
    duration = get_duration("combined.mp4")
    print(f"  Combined duration: {duration:.1f}s")
    
    print("\nStep 3: Adding text overlays...")
    
    # Build complex filter for all text overlays
    # FFmpeg drawtext: enable='between(t,start,end)'
    font = "/System/Library/Fonts/Supplemental/Impact.ttf"
    fontalt = "/System/Library/Fonts/Helvetica.ttc"
    
    # Use Impact if available, else Helvetica
    fontfile = font if os.path.exists(font) else fontalt
    
    # Text overlays with timing based on combined video
    # Calculate cumulative times:
    # Intro: 0-5s
    # Pack1: 5-10.3s (Andy Reid text at ~8s)
    # Pack2: 10.3-23.6s (Triple EPIC at ~17s)
    # Pack3: 23.6-30.3s (Bowers at ~27s)
    # Pack4: 30.3-37.8s (Xavien at ~34s)
    # Pack5: 37.8-41.8s (Greenlaw at ~40s)
    # Drake tease: 41.8-49.8s (Drake UR at ~46s)
    # Finale: 49.8-69.8s (Drake EPIC at ~55s, end card ~62s)
    
    overlays = [
        # Intro title
        (0, 5, "DRAKE MAYE HUNT", 60, 52, "gold", True),
        (0, 5, "EPISODE 8", 125, 36, "white", False),
        (0, 5, "Super Bowl Edition", 175, 32, "cyan", False),
        
        # Pack 1: Andy Reid
        (7, 10.3, "Andy Reid 37/49", 360, 32, "cyan", False),
        (7, 10.3, "ULTRA RARE - $5", 410, 28, "lime", False),
        
        # Pack 2: Triple EPIC
        (15, 23.6, "TRIPLE EPIC!", 310, 48, "magenta", True),
        (15, 23.6, "Michael Penix Jr. 2/10", 380, 32, "magenta", False),
        (15, 23.6, "EPIC - $250+", 425, 32, "lime", False),
        
        # Pack 3: Brock Bowers
        (26, 30.3, "Brock Bowers 3/25", 360, 32, "magenta", False),
        (26, 30.3, "EPIC - $150", 410, 28, "lime", False),
        
        # Pack 4: Xavien Howard
        (33, 37.8, "Xavien Howard 10/25", 360, 32, "magenta", False),
        (33, 37.8, "EPIC - $50", 410, 28, "lime", False),
        
        # Pack 5: Dre Greenlaw
        (39, 41.8, "Dre Greenlaw 34/49", 370, 28, "cyan", False),
        (39, 41.8, "ULTRA RARE", 410, 24, "white", False),
        
        # Drake Maye Tease
        (45, 49.8, "DRAKE MAYE!", 330, 48, "cyan", True),
        (45, 49.8, "28/49 ULTRA RARE", 395, 32, "cyan", False),
        (45, 49.8, "$75", 440, 32, "lime", False),
        (45, 49.8, "But wait...", 490, 28, "white", False),
        
        # THE FINALE - Drake Maye EPIC
        (52, 58, "THE HUNT IS OVER!", 200, 56, "gold", True),
        (52, 58, "DRAKE MAYE", 280, 56, "magenta", True),
        (52, 58, "9/10 EPIC", 360, 48, "magenta", False),
        (52, 58, "$19,000!", 430, 52, "lime", True),
        
        # End card
        (58, 70, "FOUND ONE!", 180, 56, "gold", True),
        (58, 70, "Drake Maye 9/10 EPIC", 260, 42, "magenta", False),
        (58, 70, "Value: $19,000+", 320, 36, "lime", False),
        (58, 70, "More Drake Maye hunting", 400, 32, "white", False),
        (58, 70, "before the Super Bowl!", 445, 32, "cyan", False),
    ]
    
    # Build filter chain
    filter_parts = []
    for start, end, text, y, size, color, glow in overlays:
        # Escape special characters for FFmpeg
        escaped_text = text.replace("'", "\\'").replace(":", "\\:")
        
        # Color mapping
        colors = {
            "gold": "0xFFD700",
            "white": "0xFFFFFF", 
            "cyan": "0x00FFFF",
            "magenta": "0xFF00FF",
            "lime": "0x00FF00",
            "orange": "0xFF8C00",
        }
        fc = colors.get(color, "0xFFFFFF")
        
        # Add black outline for readability
        if glow:
            # Draw shadow/glow effect with larger borderw
            filter_parts.append(
                f"drawtext=fontfile='{fontfile}':text='{escaped_text}':"
                f"fontsize={size}:fontcolor={fc}:borderw=4:bordercolor=black:"
                f"x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})'"
            )
        else:
            filter_parts.append(
                f"drawtext=fontfile='{fontfile}':text='{escaped_text}':"
                f"fontsize={size}:fontcolor={fc}:borderw=3:bordercolor=black:"
                f"x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})'"
            )
    
    filter_chain = ",".join(filter_parts)
    
    # Apply overlays and trim to 60s
    subprocess.run([
        "ffmpeg", "-y", "-i", "combined.mp4",
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "-t", "60",
        FINAL
    ], capture_output=True)
    
    final_duration = get_duration(FINAL)
    print(f"\n✅ Done! Created: {FINAL}")
    print(f"   Final duration: {final_duration:.1f}s")
    
    # Cleanup
    print("\nStep 4: Cleaning up...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    for f in ["concat.txt", "combined.mp4"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("🎬 Video ready for review!")

if __name__ == "__main__":
    main()
