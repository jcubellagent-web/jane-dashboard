#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - TikTok Edit v2
60-second montage with Drake Maye EPIC 9/10 as the climax!
Simplified approach with proper text overlays.
"""

import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
INPUT = "/Users/jc_agent/.openclaw/media/inbound/9e9fdcf1-a657-40e6-8eae-9f769b4d618b.mp4"
FINAL = f"{WORK_DIR}/EP8_FINAL.mp4"

# Key segments: (start, end, speed)
SEGMENTS = [
    (0, 5, 1.0),           # Intro - 5s
    (30, 38, 1.5),         # Pack 1: Andy Reid - 5.3s
    (55, 75, 1.5),         # Pack 2: Triple EPIC Penix - 13.3s
    (85, 95, 1.5),         # Pack 3: Brock Bowers - 6.7s
    (100, 115, 2.0),       # Pack 4: Xavien Howard - 7.5s
    (120, 130, 2.5),       # Pack 5: Dre Greenlaw - 4s
    (188, 200, 1.5),       # Drake tease - 8s
    (225, 241, 0.8),       # FINALE Drake EPIC - 20s
]

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
        
        setpts = 1.0 / speed
        
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
    
    print("\nStep 3: Trimming to 60 seconds...")
    subprocess.run([
        "ffmpeg", "-y", "-i", "combined.mp4",
        "-t", "60",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "trimmed.mp4"
    ], capture_output=True)
    
    print("\nStep 4: Adding text overlays...")
    
    font = "/System/Library/Fonts/Supplemental/Impact.ttf"
    if not os.path.exists(font):
        font = "/System/Library/Fonts/Helvetica.ttc"
    
    # Simplified overlays - key moments only
    # Timeline after segments:
    # 0-5s: Intro
    # 5-10.3s: Andy Reid
    # 10.3-23.6s: Triple EPIC Penix
    # 23.6-30.3s: Bowers
    # 30.3-37.8s: Xavien
    # 37.8-41.8s: Greenlaw
    # 41.8-49.8s: Drake tease
    # 49.8-60s: FINALE
    
    filter_parts = []
    
    # INTRO
    filter_parts.append(f"drawtext=fontfile='{font}':text='DRAKE MAYE HUNT':fontsize=52:fontcolor=gold:borderw=4:bordercolor=black:x=(w-text_w)/2:y=60:enable='between(t,0,5)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='EPISODE 8':fontsize=36:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=125:enable='between(t,0,5)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='Super Bowl Edition':fontsize=32:fontcolor=cyan:borderw=3:bordercolor=black:x=(w-text_w)/2:y=175:enable='between(t,0,5)'")
    
    # ANDY REID
    filter_parts.append(f"drawtext=fontfile='{font}':text='Andy Reid 37/49':fontsize=32:fontcolor=cyan:borderw=3:bordercolor=black:x=(w-text_w)/2:y=360:enable='between(t,7,10)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='ULTRA RARE':fontsize=28:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=405:enable='between(t,7,10)'")
    
    # TRIPLE EPIC PACK
    filter_parts.append(f"drawtext=fontfile='{font}':text='TRIPLE EPIC PACK':fontsize=42:fontcolor=magenta:borderw=4:bordercolor=black:x=(w-text_w)/2:y=300:enable='between(t,15,23)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='Michael Penix Jr. 2/10 - $250':fontsize=28:fontcolor=magenta:borderw=3:bordercolor=black:x=(w-text_w)/2:y=360:enable='between(t,15,23)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='Rome Odunze 21/25 - Grover Stewart 11/25':fontsize=22:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=400:enable='between(t,15,23)'")
    
    # BROCK BOWERS
    filter_parts.append(f"drawtext=fontfile='{font}':text='Brock Bowers 3/25':fontsize=32:fontcolor=magenta:borderw=3:bordercolor=black:x=(w-text_w)/2:y=360:enable='between(t,26,30)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='EPIC - $150':fontsize=28:fontcolor=lime:borderw=3:bordercolor=black:x=(w-text_w)/2:y=405:enable='between(t,26,30)'")
    
    # XAVIEN HOWARD
    filter_parts.append(f"drawtext=fontfile='{font}':text='Xavien Howard 10/25':fontsize=32:fontcolor=magenta:borderw=3:bordercolor=black:x=(w-text_w)/2:y=360:enable='between(t,33,37)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='EPIC - $50':fontsize=28:fontcolor=lime:borderw=3:bordercolor=black:x=(w-text_w)/2:y=405:enable='between(t,33,37)'")
    
    # DRE GREENLAW  
    filter_parts.append(f"drawtext=fontfile='{font}':text='Dre Greenlaw 34/49':fontsize=28:fontcolor=cyan:borderw=3:bordercolor=black:x=(w-text_w)/2:y=370:enable='between(t,39,41)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='ULTRA RARE':fontsize=24:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=410:enable='between(t,39,41)'")
    
    # DRAKE MAYE TEASE
    filter_parts.append(f"drawtext=fontfile='{font}':text='DRAKE MAYE':fontsize=42:fontcolor=cyan:borderw=4:bordercolor=black:x=(w-text_w)/2:y=330:enable='between(t,45,49)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='28/49 ULTRA RARE - $75':fontsize=28:fontcolor=lime:borderw=3:bordercolor=black:x=(w-text_w)/2:y=390:enable='between(t,45,49)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='But wait...':fontsize=26:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=440:enable='between(t,45,49)'")
    
    # THE FINALE - DRAKE MAYE EPIC
    filter_parts.append(f"drawtext=fontfile='{font}':text='THE HUNT IS OVER':fontsize=48:fontcolor=gold:borderw=5:bordercolor=black:x=(w-text_w)/2:y=180:enable='between(t,52,57)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='DRAKE MAYE':fontsize=52:fontcolor=magenta:borderw=5:bordercolor=black:x=(w-text_w)/2:y=250:enable='between(t,52,57)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='9/10 EPIC':fontsize=42:fontcolor=magenta:borderw=4:bordercolor=black:x=(w-text_w)/2:y=320:enable='between(t,52,57)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='$19,000':fontsize=56:fontcolor=lime:borderw=5:bordercolor=black:x=(w-text_w)/2:y=390:enable='between(t,52,57)'")
    
    # END CARD
    filter_parts.append(f"drawtext=fontfile='{font}':text='FOUND ONE':fontsize=52:fontcolor=gold:borderw=5:bordercolor=black:x=(w-text_w)/2:y=150:enable='between(t,57,60)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='Drake Maye 9/10 EPIC':fontsize=36:fontcolor=magenta:borderw=4:bordercolor=black:x=(w-text_w)/2:y=230:enable='between(t,57,60)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='$19,000 Value':fontsize=32:fontcolor=lime:borderw=3:bordercolor=black:x=(w-text_w)/2:y=290:enable='between(t,57,60)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='More Drake Maye hunting':fontsize=28:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=380:enable='between(t,57,60)'")
    filter_parts.append(f"drawtext=fontfile='{font}':text='before the Super Bowl':fontsize=28:fontcolor=cyan:borderw=3:bordercolor=black:x=(w-text_w)/2:y=420:enable='between(t,57,60)'")
    
    filter_chain = ",".join(filter_parts)
    
    result = subprocess.run([
        "ffmpeg", "-y", "-i", "trimmed.mp4",
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "copy",
        FINAL
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        # Fallback: copy without overlays
        subprocess.run(["cp", "trimmed.mp4", FINAL])
    
    final_duration = get_duration(FINAL)
    print(f"\n✅ Done! Created: {FINAL}")
    print(f"   Final duration: {final_duration:.1f}s")
    
    # Get file size
    size_mb = os.path.getsize(FINAL) / (1024*1024)
    print(f"   File size: {size_mb:.1f} MB")
    
    # Cleanup
    print("\nStep 5: Cleaning up...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
    for f in ["concat.txt", "combined.mp4", "trimmed.mp4"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("🎬 Video ready for review!")

if __name__ == "__main__":
    main()
