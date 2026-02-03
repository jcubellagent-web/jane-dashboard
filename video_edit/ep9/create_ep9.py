#!/usr/bin/env python3
"""
Drake Maye Hunt EP.9 - DOUBLE EPIC EDITION! 
Joe Montana + Puka Nacua = PROFIT PACK!
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep9"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/7ce8e61d-e32b-4d4d-958d-58a7e9959f6d.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP9_DOUBLE_EPIC.mp4"

WIDTH = 384
HEIGHT = 848
FPS = 30

def draw_text_outline(draw, text, x, y, font, fill, outline=(0,0,0), width=4):
    for dx in range(-width, width+1):
        for dy in range(-width, width+1):
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def create_title_card():
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 40)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 28)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    
    texts = [
        ("DRAKE MAYE", 200, font_xl, (255,255,255)),
        ("HUNT EP.9", 255, font_xl, (255,215,0)),
        ("DOUBLE EPIC", 340, font_lg, (255,50,255)),
        ("EDITION", 380, font_lg, (255,50,255)),
        ("2024 Panini Select", 480, font_md, (100,100,100)),
    ]
    for text, y, font, color in texts:
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        draw_text_outline(draw, text, x, y, font, color)
    return img

def create_results_card():
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 34)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
    
    texts = [
        ("DOUBLE EPIC!", 100, font_xl, (255,50,255)),
        ("EPIC #1", 180, font_lg, (255,140,0)),
        ("Joe Montana 22/25", 215, font_md, (255,200,150)),
        ("Floor: $100", 245, font_md, (100,255,100)),
        ("EPIC #2", 310, font_lg, (255,140,0)),
        ("Puka Nacua 8/25", 345, font_md, (255,200,150)),
        ("Floor: $60", 375, font_md, (100,255,100)),
        ("+ Josh Allen $3", 430, font_md, (200,200,200)),
        ("+ Amari Cooper $2", 460, font_md, (200,200,200)),
        ("PACK VALUE", 530, font_lg, (255,255,255)),
        ("$165", 570, font_xl, (50,255,50)),
        ("PROFIT: +$105!", 630, font_lg, (50,255,50)),
        ("The hunt continues...", 720, font_md, (120,120,120)),
    ]
    for text, y, font, color in texts:
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        draw_text_outline(draw, text, x, y, font, color)
    return img

def create_overlay_png(lines, filename):
    img = Image.new('RGBA', (WIDTH, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 32)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
    
    y_offset = 10
    for text, font_size, color in lines:
        font = font_lg if font_size == 'lg' else font_md
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx or dy:
                    draw.text((x+dx, y_offset+dy), text, font=font, fill=(0,0,0,255))
        draw.text((x, y_offset), text, font=font, fill=color+(255,))
        y_offset += 48 if font_size == 'lg' else 38
    
    img.save(filename, 'PNG')

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.9 - DOUBLE EPIC EDITION!")
    print("=" * 50)
    
    # Step 1: Create title card (3s)
    print("\n1. Creating title card...")
    title_jpg = f"{WORK_DIR}/title.jpg"
    create_title_card().save(title_jpg, quality=95)
    title_mp4 = f"{WORK_DIR}/title.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', title_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '3', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', title_mp4
    ], capture_output=True)
    
    # Step 2: Speed up main footage (41s -> 26s)
    print("2. Processing main footage...")
    main_mp4 = f"{WORK_DIR}/main.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.63*PTS[v];[0:a]atempo=1.59[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-t', '26', main_mp4
    ], capture_output=True)
    
    # Step 3: Create results card (5s for this special pack!)
    print("3. Creating results card...")
    results_jpg = f"{WORK_DIR}/results.jpg"
    create_results_card().save(results_jpg, quality=95)
    results_mp4 = f"{WORK_DIR}/results.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', results_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '5', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', results_mp4
    ], capture_output=True)
    
    # Step 4: Concatenate segments
    print("4. Concatenating...")
    concat_txt = f"{WORK_DIR}/concat.txt"
    with open(concat_txt, 'w') as f:
        f.write(f"file '{title_mp4}'\n")
        f.write(f"file '{main_mp4}'\n")
        f.write(f"file '{results_mp4}'\n")
    
    concat_mp4 = f"{WORK_DIR}/concat.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', concat_mp4
    ], capture_output=True)
    
    # Step 5: Create and apply overlays
    # Timing after title card (3s offset):
    # In sped up footage: Josh Allen ~11s, Joe Montana ~17s, Amari ~20s, Puka ~23s
    # In final video: +3s = Josh ~14s, Joe ~20s, Amari ~23s, Puka ~26s
    print("5. Applying overlays (CENTERED)...")
    
    overlays = [
        (14, 17, [("Josh Allen 146/218", 'lg', (255,255,255)), ("UNCOMMON • $3", 'md', (100,255,100))]),
        (18, 22, [("Joe Montana 22/25", 'lg', (255,140,0)), ("EPIC • $100", 'md', (255,50,255))]),
        (23, 26, [("Amari Cooper 135/199", 'lg', (255,255,255)), ("RARE • $2", 'md', (255,215,0))]),
        (27, 29, [("Puka Nacua 8/25", 'lg', (255,140,0)), ("EPIC • $60", 'md', (255,50,255))]),
    ]
    
    png_files = []
    for i, (start, end, lines) in enumerate(overlays):
        pf = f"{WORK_DIR}/ov_{i}.png"
        create_overlay_png(lines, pf)
        png_files.append((pf, start, end))
        print(f"   [{start}-{end}s] {lines[0][0]}")
    
    inputs = ['-i', concat_mp4]
    for pf, _, _ in png_files:
        inputs.extend(['-i', pf])
    
    filters = []
    prev = '0:v'
    CENTER_Y = 350
    for i, (_, start, end) in enumerate(png_files):
        out = f'v{i}'
        filters.append(f"[{prev}][{i+1}:v]overlay=0:{CENTER_Y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    overlay_mp4 = f"{WORK_DIR}/overlay.mp4"
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', ';'.join(filters),
        '-map', f'[{prev}]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', overlay_mp4
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Step 6: Add background music
    print("6. Adding music...")
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                       '-of', 'default=noprint_wrappers=1:nokey=1', overlay_mp4],
                      capture_output=True, text=True)
    dur = float(r.stdout.strip())
    
    subprocess.run([
        'ffmpeg', '-y', '-i', overlay_mp4, '-i', MUSIC,
        '-filter_complex',
        f'[1:a]afade=t=in:d=1,afade=t=out:st={dur-2}:d=2,volume=0.12[m];'
        f'[0:a]volume=0.9[o];[o][m]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy', '-c:a', 'aac', '-movflags', '+faststart',
        OUTPUT
    ], capture_output=True)
    
    # Cleanup
    for f in [title_jpg, title_mp4, main_mp4, results_jpg, results_mp4, 
              concat_txt, concat_mp4, overlay_mp4]:
        if os.path.exists(f): os.remove(f)
    for pf, _, _ in png_files:
        if os.path.exists(pf): os.remove(pf)
    
    if os.path.exists(OUTPUT) and os.path.getsize(OUTPUT) > 0:
        size_mb = os.path.getsize(OUTPUT) / (1024*1024)
        print(f"\n{'='*50}")
        print("SUCCESS! DOUBLE EPIC EDITION!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {size_mb:.1f} MB | Duration: {dur:.0f}s")
        print("Joe Montana + Puka Nacua = $165 PROFIT PACK!")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
