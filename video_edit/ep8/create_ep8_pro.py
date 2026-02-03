#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - PRO VERSION
Burns text directly into video frames using solid text boxes
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys
import tempfile
import shutil

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_PRO.mp4"

# Video specs
WIDTH = 384
HEIGHT = 848
FPS = 30

def create_title_frame(width, height):
    """Create a title card frame"""
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    font_large = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 42)
    font_med = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
    
    # Title
    title = "DRAKE MAYE"
    bbox = draw.textbbox((0,0), title, font=font_large)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, 200), title, font=font_large, fill=(255,255,255))
    
    title2 = "HUNT EP.8"
    bbox = draw.textbbox((0,0), title2, font=font_large)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, 260), title2, font=font_large, fill=(255,255,255))
    
    # Subtitle
    sub = "🏈 PATS TO THE SUPER BOWL 🏈"
    bbox = draw.textbbox((0,0), sub, font=font_med)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, 340), sub, font=font_med, fill=(255,215,0))
    
    # Pack info
    info = "2024 Panini Select"
    bbox = draw.textbbox((0,0), info, font=font_med)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, 420), info, font=font_med, fill=(150,150,150))
    
    return img

def create_results_frame(width, height):
    """Create end results card"""
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_large = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 36)
    font_med = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 26)
    font_small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    
    y = 180
    
    # Header
    text = "PACK RESULTS"
    bbox = draw.textbbox((0,0), text, font=font_large)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_large, fill=(255,255,255))
    y += 70
    
    # Ultra Rare
    text = "🔥 ULTRA RARE 🔥"
    bbox = draw.textbbox((0,0), text, font=font_med)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_med, fill=(255,100,50))
    y += 40
    
    text = "Dre Greenlaw 13/49"
    bbox = draw.textbbox((0,0), text, font=font_small)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_small, fill=(255,150,100))
    y += 30
    
    text = "Floor: $7"
    bbox = draw.textbbox((0,0), text, font=font_small)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_small, fill=(100,255,100))
    y += 60
    
    # Epic
    text = "🔥🔥 EPIC 🔥🔥"
    bbox = draw.textbbox((0,0), text, font=font_med)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_med, fill=(200,50,255))
    y += 40
    
    text = "Marquise Brown 3/10"
    bbox = draw.textbbox((0,0), text, font=font_small)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_small, fill=(220,150,255))
    y += 30
    
    text = "Floor: $15"
    bbox = draw.textbbox((0,0), text, font=font_small)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_small, fill=(100,255,100))
    y += 80
    
    # Total
    text = "PACK VALUE: $24"
    bbox = draw.textbbox((0,0), text, font=font_large)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_large, fill=(50,255,50))
    y += 50
    
    text = "The hunt continues..."
    bbox = draw.textbbox((0,0), text, font=font_small)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font_small, fill=(150,150,150))
    
    return img

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - PRO VERSION")
    print("=" * 50)
    
    tmpdir = tempfile.mkdtemp()
    print(f"Working in: {tmpdir}")
    
    try:
        # Step 1: Create title card video (3 seconds)
        print("\n1. Creating title card...")
        title_img = create_title_frame(WIDTH, HEIGHT)
        title_path = f"{tmpdir}/title.jpg"
        title_img.save(title_path, quality=95)
        
        title_vid = f"{tmpdir}/title.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', title_path,
            '-c:v', 'libx264', '-t', '3', '-pix_fmt', 'yuv420p',
            '-vf', f'scale={WIDTH}:{HEIGHT}', '-r', str(FPS),
            title_vid
        ], capture_output=True)
        print("   Title card: 3s")
        
        # Step 2: Speed up main footage (skip first 5s of original, use 5-38s -> 22s)
        print("\n2. Processing main footage...")
        main_vid = f"{tmpdir}/main.mp4"
        # Original is 38s, we want middle portion sped up
        # Skip intro (0-5s), take reveals (5-35s = 30s), speed to 22s
        subprocess.run([
            'ffmpeg', '-y', '-ss', '4', '-i', SOURCE, '-t', '30',
            '-filter_complex', '[0:v]setpts=0.73*PTS[v];[0:a]atempo=1.37[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '128k',
            main_vid
        ], capture_output=True)
        
        # Get actual duration
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=noprint_wrappers=1:nokey=1', main_vid],
                         capture_output=True, text=True)
        main_dur = float(r.stdout.strip())
        print(f"   Main footage: {main_dur:.1f}s")
        
        # Step 3: Create results card video (5 seconds)
        print("\n3. Creating results card...")
        results_img = create_results_frame(WIDTH, HEIGHT)
        results_path = f"{tmpdir}/results.jpg"
        results_img.save(results_path, quality=95)
        
        results_vid = f"{tmpdir}/results.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', results_path,
            '-c:v', 'libx264', '-t', '5', '-pix_fmt', 'yuv420p',
            '-vf', f'scale={WIDTH}:{HEIGHT}', '-r', str(FPS),
            results_vid
        ], capture_output=True)
        print("   Results card: 5s")
        
        # Step 4: Create concat list
        print("\n4. Concatenating segments...")
        concat_list = f"{tmpdir}/concat.txt"
        with open(concat_list, 'w') as f:
            f.write(f"file '{title_vid}'\n")
            f.write(f"file '{main_vid}'\n")
            f.write(f"file '{results_vid}'\n")
        
        concat_vid = f"{tmpdir}/concat.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '128k',
            concat_vid
        ], capture_output=True)
        
        # Step 5: Add background music
        print("\n5. Adding background music...")
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=noprint_wrappers=1:nokey=1', concat_vid],
                         capture_output=True, text=True)
        total_dur = float(r.stdout.strip())
        
        subprocess.run([
            'ffmpeg', '-y', '-i', concat_vid, '-i', MUSIC,
            '-filter_complex',
            f'[1:a]afade=t=in:d=1,afade=t=out:st={total_dur-2}:d=2,volume=0.15[m];'
            f'[0:a]volume=0.8[o];[o][m]amix=inputs=2:duration=first[a]',
            '-map', '0:v', '-map', '[a]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart',
            OUTPUT
        ], capture_output=True)
        
        if os.path.exists(OUTPUT):
            size_mb = os.path.getsize(OUTPUT) / (1024*1024)
            print(f"\n{'='*50}")
            print("SUCCESS!")
            print(f"Output: {OUTPUT}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"Duration: ~{total_dur:.0f}s")
            print(f"{'='*50}")
        else:
            print("FAILED!")
            
    finally:
        shutil.rmtree(tmpdir)
        print("\nCleaned up temp files.")

if __name__ == "__main__":
    main()
