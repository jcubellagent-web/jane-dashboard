#!/usr/bin/env python3
"""
Drake Maye Hunt EP.8 - V6 FINAL
Text in CENTER of screen, BIGGER fonts
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/ep8"
SOURCE = "/Users/jc_agent/.openclaw/media/inbound/f5e305d5-c927-4160-a023-094872847b54.mp4"
MUSIC = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"
OUTPUT = f"{WORK_DIR}/EP8_V6.mp4"

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
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 42)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 30)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    
    texts = [
        ("DRAKE MAYE", 230, font_xl, (255,255,255)),
        ("HUNT EP.8", 290, font_xl, (255,215,0)),
        ("PATS TO THE", 400, font_md, (180,180,180)),
        ("SUPER BOWL", 430, font_lg, (255,215,0)),
        ("2024 Panini Select", 530, font_md, (100,100,100)),
    ]
    for text, y, font, color in texts:
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        draw_text_outline(draw, text, x, y, font, color)
    return img

def create_results_card():
    img = Image.new('RGB', (WIDTH, HEIGHT), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    font_xl = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 36)
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 26)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 20)
    
    texts = [
        ("PACK RESULTS", 130, font_xl, (255,255,255)),
        ("ULTRA RARE", 230, font_lg, (255,100,50)),
        ("Dre Greenlaw 13/49", 270, font_md, (255,180,150)),
        ("Floor: $7", 300, font_md, (100,255,100)),
        ("EPIC", 380, font_lg, (200,50,255)),
        ("Marquise Brown 3/10", 420, font_md, (220,150,255)),
        ("Floor: $15", 450, font_md, (100,255,100)),
        ("PACK VALUE", 550, font_lg, (255,255,255)),
        ("$24", 595, font_xl, (50,255,50)),
        ("The hunt continues...", 700, font_md, (120,120,120)),
    ]
    for text, y, font, color in texts:
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        draw_text_outline(draw, text, x, y, font, color)
    return img

def create_overlay_png(lines, filename):
    """Create overlay PNG - BIGGER text, positioned for CENTER of screen"""
    img = Image.new('RGBA', (WIDTH, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # BIGGER fonts
    font_lg = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 34)
    font_md = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 26)
    
    y_offset = 10
    for text, font_size, color in lines:
        font = font_lg if font_size == 'lg' else font_md
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        # Thicker outline for visibility
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx or dy:
                    draw.text((x+dx, y_offset+dy), text, font=font, fill=(0,0,0,255))
        draw.text((x, y_offset), text, font=font, fill=color+(255,))
        y_offset += 50 if font_size == 'lg' else 40
    
    img.save(filename, 'PNG')

def main():
    print("=" * 50)
    print("Drake Maye Hunt EP.8 - V6 (CENTER + BIGGER)")
    print("=" * 50)
    
    # Step 1: Create title card (3s)
    print("\n1. Creating title card...")
    title_jpg = f"{WORK_DIR}/v6_title.jpg"
    create_title_card().save(title_jpg, quality=95)
    title_mp4 = f"{WORK_DIR}/v6_title.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', title_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '3', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', title_mp4
    ], capture_output=True)
    
    # Step 2: Speed up main footage (24s)
    print("2. Processing main footage...")
    main_mp4 = f"{WORK_DIR}/v6_main.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-i', SOURCE,
        '-filter_complex', '[0:v]setpts=0.63*PTS[v];[0:a]atempo=1.59[a]',
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-t', '24', main_mp4
    ], capture_output=True)
    
    # Step 3: Create results card (4s)
    print("3. Creating results card...")
    results_jpg = f"{WORK_DIR}/v6_results.jpg"
    create_results_card().save(results_jpg, quality=95)
    results_mp4 = f"{WORK_DIR}/v6_results.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', results_jpg,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-c:v', 'libx264', '-t', '4', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-shortest', results_mp4
    ], capture_output=True)
    
    # Step 4: Concatenate segments
    print("4. Concatenating...")
    concat_txt = f"{WORK_DIR}/v6_concat.txt"
    with open(concat_txt, 'w') as f:
        f.write(f"file '{title_mp4}'\n")
        f.write(f"file '{main_mp4}'\n")
        f.write(f"file '{results_mp4}'\n")
    
    concat_mp4 = f"{WORK_DIR}/v6_concat.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', concat_mp4
    ], capture_output=True)
    
    # Step 5: Create overlays and apply - CENTERED position
    print("5. Applying overlays (CENTERED)...")
    
    overlays = [
        (12, 15, [("Tip Reiman 210/218", 'lg', (255,255,255)), ("UNCOMMON • $1", 'md', (100,255,100))]),
        (16, 19, [("Howie Long 185/397", 'lg', (255,255,255)), ("UNCOMMON • $1", 'md', (100,255,100))]),
        (20, 23, [("Dre Greenlaw 13/49", 'lg', (255,140,0)), ("ULTRA RARE • $7", 'md', (255,80,80))]),
        (24, 27, [("Marquise Brown 3/10", 'lg', (200,100,255)), ("EPIC • $15", 'md', (200,100,255))]),
    ]
    
    png_files = []
    for i, (start, end, lines) in enumerate(overlays):
        pf = f"{WORK_DIR}/v6_ov_{i}.png"
        create_overlay_png(lines, pf)
        png_files.append((pf, start, end))
        print(f"   [{start}-{end}s] {lines[0][0]}")
    
    # Apply overlays - CENTER of screen (y = 350, middle area)
    inputs = ['-i', concat_mp4]
    for pf, _, _ in png_files:
        inputs.extend(['-i', pf])
    
    filters = []
    prev = '0:v'
    CENTER_Y = 350  # Middle of 848px screen
    for i, (_, start, end) in enumerate(png_files):
        out = f'v{i}'
        filters.append(f"[{prev}][{i+1}:v]overlay=0:{CENTER_Y}:enable='between(t,{start},{end})'[{out}]")
        prev = out
    
    overlay_mp4 = f"{WORK_DIR}/v6_overlay.mp4"
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
        print("SUCCESS!")
        print(f"Output: {OUTPUT}")
        print(f"Size: {size_mb:.1f} MB | Duration: {dur:.0f}s")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
