#!/usr/bin/env python3
"""
Polished TikTok Video - Patriots Pack Rip
Clean text overlays + royalty-free background music
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit"
VIDEO_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/patriots_drakemaye_hunt.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/energy_track.mp3"
OUTPUT_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/patriots_polished.mp4"

# Video dimensions (portrait TikTok)
WIDTH = 384
HEIGHT = 848

def create_text_image(text_lines, filename, fontsize=36, text_color=(255, 255, 255), 
                      stroke_color=(0, 0, 0), stroke_width=3, line_colors=None):
    """Create a transparent PNG with styled text"""
    
    # Try to use a bold font
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf", 
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, fontsize)
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # Calculate total height needed
    dummy = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy)
    
    line_heights = []
    line_widths = []
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    
    total_height = sum(line_heights) + (len(text_lines) - 1) * 10  # 10px line spacing
    max_width = max(line_widths) if line_widths else 100
    
    # Create image with padding
    img_width = max_width + stroke_width * 4 + 40
    img_height = total_height + stroke_width * 4 + 40
    
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw each line
    y_offset = 20
    for i, line in enumerate(text_lines):
        # Center the line
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (img_width - line_width) // 2
        
        # Get color for this line
        if line_colors and i < len(line_colors):
            color = line_colors[i]
        else:
            color = text_color
        
        # Draw stroke (outline)
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y_offset + dy), line, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y_offset), line, font=font, fill=color)
        
        y_offset += line_heights[i] + 10
    
    # Save
    output_file = os.path.join(WORK_DIR, filename)
    img.save(output_file, 'PNG')
    print(f"Created: {filename} ({img_width}x{img_height})")
    return output_file, img_width, img_height

def main():
    print("=" * 50)
    print("Creating Polished Patriots Video")
    print("=" * 50)
    
    # Create text overlays
    print("\n1. Creating text overlay images...")
    
    # Title overlay (0-5 sec)
    title_img, tw, th = create_text_image(
        ["PATRIOTS TO THE", "SUPER BOWL"],
        "overlay_title.png",
        fontsize=42,
        line_colors=[(255, 0, 0), (255, 0, 0)]  # Red
    )
    
    # Pack info (0-5 sec)
    pack_img, pw, ph = create_text_image(
        ["$60 PACK RIP"],
        "overlay_pack.png",
        fontsize=34,
        line_colors=[(255, 215, 0)]  # Gold
    )
    
    # Drake Maye hunt (0-5 sec)
    hunt_img, hw, hh = create_text_image(
        ["HUNTING FOR", "DRAKE MAYE"],
        "overlay_hunt.png",
        fontsize=32,
        line_colors=[(255, 255, 255), (0, 255, 255)]  # White, Cyan
    )
    
    # Card reveals
    jj_img, _, _ = create_text_image(
        ["JJ McCARTHY", "RARE 39/99"],
        "overlay_jj.png",
        fontsize=34,
        line_colors=[(0, 255, 255), (255, 215, 0)]  # Cyan, Gold
    )
    
    fred_img, _, _ = create_text_image(
        ["FRED TAYLOR", "RARE 2/99 !!"],
        "overlay_fred.png",
        fontsize=34,
        line_colors=[(0, 255, 0), (255, 0, 0)]  # Green, Red
    )
    
    kittle_img, _, _ = create_text_image(
        ["GEORGE KITTLE", "RARE 56/99"],
        "overlay_kittle.png",
        fontsize=34,
        line_colors=[(255, 0, 0), (255, 215, 0)]  # Red (49ers), Gold
    )
    
    # CTA at end
    cta_img, _, _ = create_text_image(
        ["LIKE + COMMENT", "IF I SHOULD", "RIP MORE!"],
        "overlay_cta.png",
        fontsize=38,
        line_colors=[(255, 255, 255), (255, 215, 0), (0, 255, 0)]
    )
    
    # 2. Build ffmpeg filter for compositing
    print("\n2. Building video with overlays and music...")
    
    # Calculate positions (centered horizontally)
    title_x = (WIDTH - tw) // 2
    pack_x = (WIDTH - pw) // 2
    hunt_x = (WIDTH - hw) // 2
    
    # Complex filter graph
    filter_complex = f"""
    [0:v]scale={WIDTH}:{HEIGHT}[base];
    [1:v]format=rgba[title];
    [2:v]format=rgba[pack];
    [3:v]format=rgba[hunt];
    [4:v]format=rgba[jj];
    [5:v]format=rgba[fred];
    [6:v]format=rgba[kittle];
    [7:v]format=rgba[cta];
    
    [base][title]overlay=x={title_x}:y=70:enable='between(t,0,5)'[v1];
    [v1][pack]overlay=x={pack_x}:y=170:enable='between(t,0,5)'[v2];
    [v2][hunt]overlay=x={hunt_x}:y=230:enable='between(t,0,5)'[v3];
    [v3][jj]overlay=x=(W-w)/2:y=80:enable='between(t,18,23)'[v4];
    [v4][fred]overlay=x=(W-w)/2:y=80:enable='between(t,28,33)'[v5];
    [v5][kittle]overlay=x=(W-w)/2:y=80:enable='between(t,23,28)'[v6];
    [v6][cta]overlay=x=(W-w)/2:y=100:enable='gt(t,33)'[vout];
    
    [8:a]atrim=0:40,afade=t=in:st=0:d=1,afade=t=out:st=36:d=3,volume=0.3[music];
    [0:a]volume=1.0[orig];
    [orig][music]amix=inputs=2:duration=first:dropout_transition=2[aout]
    """
    
    # Remove newlines for ffmpeg
    filter_complex = filter_complex.replace('\n', '').replace('  ', ' ')
    
    cmd = [
        'ffmpeg', '-y',
        '-i', VIDEO_PATH,
        '-i', os.path.join(WORK_DIR, 'overlay_title.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_pack.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_hunt.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_jj.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_fred.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_kittle.png'),
        '-i', os.path.join(WORK_DIR, 'overlay_cta.png'),
        '-i', MUSIC_PATH,
        '-filter_complex', filter_complex,
        '-map', '[vout]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-t', '39',
        OUTPUT_PATH
    ]
    
    print("Running ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("FFmpeg error:")
        print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        return False
    
    print(f"\n3. Success! Output: {OUTPUT_PATH}")
    
    # Verify output
    if os.path.exists(OUTPUT_PATH):
        size = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
        print(f"   File size: {size:.2f} MB")
    
    return True

if __name__ == "__main__":
    main()
