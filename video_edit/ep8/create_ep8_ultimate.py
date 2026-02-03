#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - ULTIMATE VERSION
Title card + Pack opening WITH overlays + Results card
Professional quality with text throughout
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_ULTIMATE.mp4"

WIDTH = 384
HEIGHT = 848
FPS = 30

def draw_text(draw, text, y, font, fill, width=WIDTH):
    bbox = draw.textbbox((0,0), text, font=font)
    x = (width - (bbox[2]-bbox[0])) // 2
    # Black outline
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0))
    draw.text((x, y), text, font=font, fill=fill)

def create_title_card():
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 44)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 32)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
    
    draw_text(draw, "DRAKE MAYE", 220, font_xl, (255,255,255))
    draw_text(draw, "HUNT", 280, font_xl, (255,255,255))
    draw_text(draw, "EP.8", 350, font_lg, (255,215,0))
    draw_text(draw, "PATS TO THE", 450, font_md, (200,200,200))
    draw_text(draw, "SUPER BOWL", 485, font_lg, (255,215,0))
    draw_text(draw, "2024 Panini Select", 580, font_md, (120,120,120))
    return img

def create_results_card():
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 38)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    font_sm = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
    
    draw_text(draw, "PACK RESULTS", 120, font_xl, (255,255,255))
    draw_text(draw, "ULTRA RARE", 220, font_lg, (255,100,50))
    draw_text(draw, "Dre Greenlaw 13/49", 260, font_md, (255,180,150))
    draw_text(draw, "FLOOR: $7", 295, font_md, (100,255,100))
    draw_text(draw, "EPIC", 380, font_lg, (200,50,255))
    draw_text(draw, "Marquise Brown 3/10", 420, font_md, (220,150,255))
    draw_text(draw, "FLOOR: $15", 455, font_md, (100,255,100))
    draw_text(draw, "PACK VALUE", 560, font_lg, (255,255,255))
    draw_text(draw, "$24", 610, font_xl, (50,255,50))
    draw_text(draw, "The hunt continues...", 720, font_sm, (150,150,150))
    return img

def create_overlay_png(text1, text2, color1, color2, filename):
    """Create overlay with two lines of text"""
    img = Image.new('RGBA', (WIDTH, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    
    # Line 1
    bbox = draw.textbbox((0,0), text1, font=font_lg)
    x = (WIDTH - (bbox[2]-bbox[0])) // 2
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx or dy:
                draw.text((x+dx, 10+dy), text1, font=font_lg, fill=(0,0,0,255))
    draw.text((x, 10), text1, font=font_lg, fill=color1+(255,))
    
    # Line 2
    bbox = draw.textbbox((0,0), text2, font=font_md)
    x = (WIDTH - (bbox[2]-bbox[0])) // 2
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx or dy:
                draw.text((x+dx, 55+dy), text2, font=font_md, fill=(0,0,0,255))
    draw.text((x, 55), text2, font=font_md, fill=color2+(255,))
    
    img.save(filename, 'PNG')

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - ULTIMATE VERSION")
    print("=" * 50)
    
    # Step 1: Create title card
    print("\n1. Creating title card...")
    title_jpg = f"{WORK_DIR}/u_title.jpg"
    create_title_card().save(title_jpg, quality=95)
    title_mp4 = f"{WORK_DIR}/u_title.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', title_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '3', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', title_mp4
    ], capture_output=True)
    print(f"   Title: {os.path.getsize(title_mp4)//1024}KB")
    
    # Step 2: Create pack opening with overlays
    print("\n2. Processing pack opening with overlays...")
    
    # First, speed up source video
    base_mp4 = f"{WORK_DIR}/u_base.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.63*PTS[v];[0:a]atempo=1.59[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-t', '24', base_mp4
    ], capture_output=True)
    print(f"   Base: {os.path.getsize(base_mp4)//1024}KB")
    
    # Create overlay PNGs - timing adjusted for sped up video
    # Reveals happen at: ~9s Tip, ~13s Howie, ~17s Dre, ~21s Marquise
    overlays = [
        (10, 13, "Tip Reiman 210/218", "UNCOMMON - $1", (255,255,255), (100,255,100)),
        (14, 17, "Howie Long 185/397", "UNCOMMON - $1", (255,255,255), (100,255,100)),
        (18, 21, "Dre Greenlaw 13/49", "ULTRA RARE - $7", (255,140,0), (255,80,80)),
        (22, 24, "Marquise Brown 3/10", "EPIC - $15", (200,100,255), (200,100,255)),
    ]
    
    png_files = []
    for i, (start, end, t1, t2, c1, c2) in enumerate(overlays):
        pf = f"{WORK_DIR}/u_overlay_{i}.png"
        create_overlay_png(t1, t2, c1, c2, pf)
        png_files.append((pf, start, end))
        print(f"   Overlay {i+1}: [{start}-{end}s] {t1}")
    
    # Apply overlays to base
    inputs = ['-i', base_mp4]
    for pf, _, _ in png_files:
        inputs.extend(['-i', pf])
    
    filters = []
    prev = '0:v'
    for i, (_, start, end) in enumerate(png_files):
        out = f'v{i}'
        # Position at bottom of screen (y = HEIGHT - 150)
        filters.append(f"[{prev}][{i+1}:v]overlay=0:{HEIGHT-130}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    main_mp4 = f"{WORK_DIR}/u_main.mp4"
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filters),
        '-map', f'[{prev}]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', main_mp4
    ]
    subprocess.run(cmd, capture_output=True)
    print(f"   Main with overlays: {os.path.getsize(main_mp4)//1024}KB")
    
    # Step 3: Create results card
    print("\n3. Creating results card...")
    results_jpg = f"{WORK_DIR}/u_results.jpg"
    create_results_card().save(results_jpg, quality=95)
    results_mp4 = f"{WORK_DIR}/u_results.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', results_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '4', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', results_mp4
    ], capture_output=True)
    print(f"   Results: {os.path.getsize(results_mp4)//1024}KB")
    
    # Step 4: Concatenate
    print("\n4. Concatenating...")
    concat_txt = f"{WORK_DIR}/u_concat.txt"
    with open(concat_txt, 'w') as f:
        f.write(f"file '{title_mp4}'\n")
        f.write(f"file '{main_mp4}'\n")
        f.write(f"file '{results_mp4}'\n")
    
    concat_mp4 = f"{WORK_DIR}/u_concat.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', concat_mp4
    ], capture_output=True)
    
    # Step 5: Add music
    print("\n5. Adding background music...")
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', concat_mp4],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    
    subprocess.run([
        'ffmpeg', '-y', '-i', concat_mp4, '-i', MUSIC,
        '-filter_complex',
        f'[1:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.12[m];'
        f'[0:a]volume=0.9[o];[o][m]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy', '-c:a', 'aac', '-movflags', '+faststart',
        OUTPUT
    ], capture_output=True)
    
    # Cleanup
    for f in [title_jpg, title_mp4, base_mp4, main_mp4, results_jpg, results_mp4, concat_txt, concat_mp4]:
        if os.path.exists(f): os.remove(f)
    for pf, _, _ in png_files:
        if os.path.exists(pf): os.remove(pf)
    
    if os.path.exists(OUTPUT) and os.path.getsize(OUTPUT) > 0:
        size_mb = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {size_mb:.1f} MB | Duration: {dur:.0f}s")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
