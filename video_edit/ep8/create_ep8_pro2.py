#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - PRO VERSION v2
Title card -> Pack opening -> Results card
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os
import sys

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_PRO.mp4"

WIDTH = 384
HEIGHT = 848
FPS = 30

def draw_centered_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0,0), text, font=font)
    x = (WIDTH - (bbox[2]-bbox[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)

def create_title_card():
    """Create intro title card"""
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 44)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 32)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
    
    draw_centered_text(draw, "DRAKE MAYE", 220, font_xl, (255,255,255))
    draw_centered_text(draw, "HUNT", 280, font_xl, (255,255,255))
    draw_centered_text(draw, "EP.8", 350, font_lg, (255,215,0))
    draw_centered_text(draw, "PATS TO THE", 450, font_md, (200,200,200))
    draw_centered_text(draw, "SUPER BOWL", 485, font_lg, (255,215,0))
    draw_centered_text(draw, "2024 Panini Select", 580, font_md, (120,120,120))
    
    return img

def create_results_card():
    """Create end results card"""
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 38)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    font_sm = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
    
    draw_centered_text(draw, "PACK RESULTS", 120, font_xl, (255,255,255))
    
    # Ultra Rare section
    draw_centered_text(draw, "ULTRA RARE", 220, font_lg, (255,100,50))
    draw_centered_text(draw, "Dre Greenlaw", 260, font_md, (255,180,150))
    draw_centered_text(draw, "13/49", 290, font_sm, (200,200,200))
    draw_centered_text(draw, "FLOOR: $7", 320, font_md, (100,255,100))
    
    # Epic section
    draw_centered_text(draw, "EPIC", 400, font_lg, (200,50,255))
    draw_centered_text(draw, "Marquise Brown", 440, font_md, (220,150,255))
    draw_centered_text(draw, "3/10", 470, font_sm, (200,200,200))
    draw_centered_text(draw, "FLOOR: $15", 500, font_md, (100,255,100))
    
    # Total
    draw_centered_text(draw, "PACK VALUE", 600, font_lg, (255,255,255))
    draw_centered_text(draw, "$24", 650, font_xl, (50,255,50))
    
    draw_centered_text(draw, "The hunt continues...", 750, font_sm, (150,150,150))
    
    return img

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - PRO VERSION")
    print("=" * 50)
    
    # Step 1: Create title card image and video
    print("\n1. Creating title card...")
    title_img = create_title_card()
    title_jpg = f"{WORK_DIR}/title_card.jpg"
    title_img.save(title_jpg, quality=95)
    
    title_mp4 = f"{WORK_DIR}/title.mp4"
    result = subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', title_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '3', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-shortest',
        title_mp4
    ], capture_output=True, text=True)
    if not os.path.exists(title_mp4) or os.path.getsize(title_mp4) == 0:
        print(f"Title failed: {result.stderr[-300:]}")
        return
    print(f"   Created: {os.path.getsize(title_mp4)//1024}KB")
    
    # Step 2: Process main pack opening footage
    print("\n2. Processing pack opening footage...")
    main_mp4 = f"{WORK_DIR}/main.mp4"
    # Take full video, speed up to ~24s
    result = subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.63*PTS[v];[0:a]atempo=1.59[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', '24',
        main_mp4
    ], capture_output=True, text=True)
    if not os.path.exists(main_mp4) or os.path.getsize(main_mp4) == 0:
        print(f"Main failed: {result.stderr[-300:]}")
        return
    print(f"   Created: {os.path.getsize(main_mp4)//1024}KB")
    
    # Step 3: Create results card
    print("\n3. Creating results card...")
    results_img = create_results_card()
    results_jpg = f"{WORK_DIR}/results_card.jpg"
    results_img.save(results_jpg, quality=95)
    
    results_mp4 = f"{WORK_DIR}/results.mp4"
    result = subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', results_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '4', '-pix_fmt', 'yuv420p',
        '-r', str(FPS), '-shortest',
        results_mp4
    ], capture_output=True, text=True)
    if not os.path.exists(results_mp4) or os.path.getsize(results_mp4) == 0:
        print(f"Results failed: {result.stderr[-300:]}")
        return
    print(f"   Created: {os.path.getsize(results_mp4)//1024}KB")
    
    # Step 4: Concatenate all segments
    print("\n4. Concatenating segments...")
    concat_txt = f"{WORK_DIR}/concat.txt"
    with open(concat_txt, 'w') as f:
        f.write(f"file '{title_mp4}'\n")
        f.write(f"file '{main_mp4}'\n")
        f.write(f"file '{results_mp4}'\n")
    
    concat_mp4 = f"{WORK_DIR}/concat.mp4"
    result = subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k',
        concat_mp4
    ], capture_output=True, text=True)
    if not os.path.exists(concat_mp4) or os.path.getsize(concat_mp4) == 0:
        print(f"Concat failed: {result.stderr[-500:]}")
        return
    print(f"   Created: {os.path.getsize(concat_mp4)//1024}KB")
    
    # Step 5: Add background music
    print("\n5. Adding background music...")
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', concat_mp4],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', concat_mp4, '-i', MUSIC,
        '-filter_complex',
        f'[1:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.12[m];'
        f'[0:a]volume=0.9[o];[o][m]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        OUTPUT
    ], capture_output=True, text=True)
    
    # Cleanup temp files
    for f in [title_jpg, title_mp4, results_jpg, results_mp4, main_mp4, concat_txt, concat_mp4]:
        if os.path.exists(f):
            os.remove(f)
    
    if os.path.exists(OUTPUT) and os.path.getsize(OUTPUT) > 0:
        size_mb = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {size_mb:.1f} MB | Duration: {dur:.0f}s")
        print(f"{'='*50}")
    else:
        print(f"Final step failed: {result.stderr[-500:]}")

if __name__ == "__main__":
    main()
