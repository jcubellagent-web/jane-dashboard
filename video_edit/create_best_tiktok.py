#!/usr/bin/env python3
"""
Create the best TikTok yet for Drake Maye hunting series
$59 Select Pack with dynamic text overlays and professional timing
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile
import shutil

# Paths
INPUT_VIDEO = "/Users/jc_agent/.openclaw/media/inbound/6188cc9d-3e3a-4c85-92d6-8d2b6b849f7b.mp4"
WORK_DIR = "/Users/jc_agent/.openclaw/workspace/video_edit/new_pack"
OUTPUT_VIDEO = "/Users/jc_agent/.openclaw/workspace/video_edit/drake_maye_hunt_ep3.mp4"
MUSIC_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/background_music.mp3"

# Video dimensions
WIDTH = 384
HEIGHT = 848

# Timeline markers (seconds) based on frame analysis
TIMELINE = {
    'pack_display': (0, 3),
    'confirm_dialog': (3, 6),
    'pack_animation': (6, 9),
    'four_card_screen': (9, 15),
    'fashanu_reveal': (15, 18),
    'kittle_reveal': (21, 24),
    'winston_reveal': (24, 30),
    'karty_reveal': (33, 36),
    'final_grid': (36, 42),
}

def create_text_overlay(text, width, height, font_size=36, color="white", bg_color=None, 
                        position="top", stroke_color="black", stroke_width=3, 
                        font_path=None, padding=20):
    """Create a professional text overlay image"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Try system fonts
            for font_name in ['/System/Library/Fonts/Helvetica.ttc', 
                             '/System/Library/Fonts/SFCompact.ttf',
                             '/Library/Fonts/Arial Bold.ttf',
                             '/System/Library/Fonts/Supplemental/Arial Bold.ttf']:
                if os.path.exists(font_name):
                    font = ImageFont.truetype(font_name, font_size)
                    break
            else:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position
    x = (width - text_width) // 2
    if position == "top":
        y = padding + 60  # Account for status bar
    elif position == "bottom":
        y = height - text_height - padding - 100  # Account for TikTok UI
    elif position == "center":
        y = (height - text_height) // 2
    elif position == "upper":
        y = height // 4
    elif position == "lower":
        y = height * 3 // 4 - text_height
    else:
        y = position if isinstance(position, int) else padding
    
    # Draw background box if specified
    if bg_color:
        box_padding = 15
        draw.rectangle([x - box_padding, y - box_padding, 
                       x + text_width + box_padding, y + text_height + box_padding],
                      fill=bg_color)
    
    # Draw text with stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=color)
    
    return img


def create_animated_text_sequence(texts_config, width, height, fps=60):
    """
    Create a sequence of frames with animated text
    texts_config: list of dicts with 'text', 'start_time', 'end_time', 'style' keys
    """
    frames_dir = os.path.join(WORK_DIR, "text_frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    # Clear old frames
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    
    # Get total duration
    max_time = max(t['end_time'] for t in texts_config)
    total_frames = int(max_time * fps)
    
    for frame_num in range(total_frames):
        current_time = frame_num / fps
        
        # Create transparent frame
        frame = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Check which texts are active
        for text_cfg in texts_config:
            if text_cfg['start_time'] <= current_time < text_cfg['end_time']:
                style = text_cfg.get('style', {})
                text_img = create_text_overlay(
                    text_cfg['text'],
                    width, height,
                    font_size=style.get('font_size', 36),
                    color=style.get('color', 'white'),
                    bg_color=style.get('bg_color'),
                    position=style.get('position', 'top'),
                    stroke_width=style.get('stroke_width', 3)
                )
                frame = Image.alpha_composite(frame, text_img)
        
        frame.save(os.path.join(frames_dir, f"frame_{frame_num:05d}.png"))
    
    return frames_dir, total_frames


def main():
    print("Creating the best TikTok yet!")
    print("=" * 50)
    
    # Step 1: Define text overlays with timestamps
    # These will appear at specific moments in the video
    texts_config = [
        # Opening hook
        {'text': 'DRAKE MAYE HUNT EP.3', 'start_time': 0, 'end_time': 3,
         'style': {'font_size': 42, 'color': '#FFD700', 'position': 'top', 'stroke_width': 4}},
        
        {'text': '$59 SELECT PACK', 'start_time': 0, 'end_time': 6,
         'style': {'font_size': 32, 'color': 'white', 'position': 'upper', 'stroke_width': 3}},
        
        # Pack opening tension
        {'text': 'WILL HE BE IN HERE?', 'start_time': 6, 'end_time': 9,
         'style': {'font_size': 36, 'color': '#00FF00', 'position': 'bottom', 'stroke_width': 3}},
        
        # Four card reveal setup
        {'text': '2 RARES + 2 UNCOMMONS', 'start_time': 9, 'end_time': 12,
         'style': {'font_size': 32, 'color': '#FF6B6B', 'position': 'top', 'stroke_width': 3}},
        
        # Card 1: Fashanu
        {'text': 'FASHANU 8/218', 'start_time': 15, 'end_time': 18,
         'style': {'font_size': 30, 'color': '#00CED1', 'position': 'bottom', 'stroke_width': 3}},
        
        # Card 2: Kittle
        {'text': 'GEORGE KITTLE!', 'start_time': 21, 'end_time': 24,
         'style': {'font_size': 38, 'color': '#FF4444', 'position': 'bottom', 'stroke_width': 4}},
        
        # Card 3: Winston - emphasize the RARE
        {'text': 'RARE ALERT', 'start_time': 24, 'end_time': 26,
         'style': {'font_size': 40, 'color': '#FFD700', 'position': 'top', 'stroke_width': 4}},
        
        {'text': 'JAMEIS WINSTON 30/99', 'start_time': 26, 'end_time': 30,
         'style': {'font_size': 32, 'color': '#FF8C00', 'position': 'bottom', 'stroke_width': 3}},
        
        # Card 4: Karty - another RARE
        {'text': 'ANOTHER RARE!', 'start_time': 33, 'end_time': 35,
         'style': {'font_size': 40, 'color': '#FFD700', 'position': 'top', 'stroke_width': 4}},
        
        {'text': 'JOSHUA KARTY 41/79', 'start_time': 35, 'end_time': 38,
         'style': {'font_size': 32, 'color': '#9370DB', 'position': 'bottom', 'stroke_width': 3}},
        
        # Ending - no Drake Maye
        {'text': 'STILL NO DRAKE MAYE...', 'start_time': 38, 'end_time': 41,
         'style': {'font_size': 36, 'color': '#FF0000', 'position': 'center', 'stroke_width': 4}},
        
        {'text': 'THE HUNT CONTINUES', 'start_time': 39, 'end_time': 42,
         'style': {'font_size': 28, 'color': 'white', 'position': 'lower', 'stroke_width': 3}},
    ]
    
    print("Step 1: Creating text overlay frames...")
    frames_dir, total_frames = create_animated_text_sequence(texts_config, WIDTH, HEIGHT, fps=60)
    print(f"  Created {total_frames} overlay frames")
    
    # Step 2: Create text overlay video
    print("\nStep 2: Creating text overlay video...")
    overlay_video = os.path.join(WORK_DIR, "text_overlay.mov")
    subprocess.run([
        'ffmpeg', '-y', '-framerate', '60',
        '-i', os.path.join(frames_dir, 'frame_%05d.png'),
        '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
        overlay_video
    ], capture_output=True)
    print("  Text overlay video created")
    
    # Step 3: Download background music if needed
    if not os.path.exists(MUSIC_PATH):
        print("\nStep 3: Downloading background music...")
        subprocess.run([
            'curl', '-L', '-o', MUSIC_PATH,
            'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3'
        ], capture_output=True)
    else:
        print("\nStep 3: Background music already exists")
    
    # Step 4: Create the final video with speed adjustments
    print("\nStep 4: Creating final video with speed adjustments...")
    
    # Speed mapping for a ~30 second target:
    # Original: 42 seconds
    # Target: ~30-32 seconds
    # - Intro (0-6s): 2.5x speed -> 2.4s
    # - Animation (6-9s): 2x speed -> 1.5s
    # - Card screen (9-15s): 1.8x speed -> 3.3s
    # - Fashanu reveal (15-21s): 1.2x speed -> 5s
    # - Kittle + Winston (21-30s): 1.2x speed -> 7.5s
    # - Karty reveal (30-36s): 1x speed -> 6s (keep dramatic)
    # - Final (36-42s): 1.5x speed -> 4s
    # Total: ~30 seconds
    
    # Create segments with different speeds
    segments = [
        (0, 6, 2.5, 'intro'),
        (6, 9, 2.0, 'animation'),
        (9, 15, 1.8, 'card_screen'),
        (15, 21, 1.2, 'fashanu'),
        (21, 30, 1.2, 'kittle_winston'),
        (30, 36, 1.0, 'karty'),  # Keep dramatic at normal speed
        (36, 42, 1.5, 'final'),
    ]
    
    segment_files = []
    for start, end, speed, name in segments:
        segment_file = os.path.join(WORK_DIR, f"segment_{name}.mp4")
        segment_files.append(segment_file)
        
        # Extract and speed up segment
        duration = end - start
        subprocess.run([
            'ffmpeg', '-y',
            '-ss', str(start), '-t', str(duration),
            '-i', INPUT_VIDEO,
            '-filter_complex', f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]',
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast',
            '-c:a', 'aac',
            segment_file
        ], capture_output=True)
        print(f"  Created segment: {name} ({duration}s @ {speed}x)")
    
    # Step 5: Concatenate segments
    print("\nStep 5: Concatenating segments...")
    concat_list = os.path.join(WORK_DIR, "concat_list.txt")
    with open(concat_list, 'w') as f:
        for seg_file in segment_files:
            f.write(f"file '{seg_file}'\n")
    
    base_video = os.path.join(WORK_DIR, "base_video.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'fast',
        '-c:a', 'aac',
        base_video
    ], capture_output=True)
    
    # Get base video duration
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', base_video
    ], capture_output=True, text=True)
    base_duration = float(probe.stdout.strip())
    print(f"  Base video duration: {base_duration:.1f}s")
    
    # Step 6: Create adjusted text overlays for the new timing
    print("\nStep 6: Adjusting text overlays for new timing...")
    
    # Recalculate text timings based on speed changes
    def adjust_time(original_time):
        """Convert original timestamp to new timestamp based on speed changes"""
        cumulative_original = 0
        cumulative_new = 0
        
        for start, end, speed, name in segments:
            segment_duration = end - start
            new_segment_duration = segment_duration / speed
            
            if original_time <= end:
                # Time falls within this segment
                time_into_segment = original_time - start
                new_time_into_segment = time_into_segment / speed
                return cumulative_new + new_time_into_segment
            
            cumulative_original += segment_duration
            cumulative_new += new_segment_duration
        
        return cumulative_new
    
    # Adjust all text timings
    adjusted_texts = []
    for text_cfg in texts_config:
        new_start = adjust_time(text_cfg['start_time'])
        new_end = adjust_time(text_cfg['end_time'])
        adjusted_texts.append({
            'text': text_cfg['text'],
            'start_time': new_start,
            'end_time': min(new_end, base_duration),
            'style': text_cfg['style']
        })
        print(f"  '{text_cfg['text']}': {text_cfg['start_time']:.1f}s -> {new_start:.1f}s")
    
    # Recreate overlay frames with adjusted timing
    print("\nStep 7: Creating adjusted text overlay frames...")
    frames_dir2, total_frames2 = create_animated_text_sequence(adjusted_texts, WIDTH, HEIGHT, fps=60)
    
    # Create new overlay video matching base video duration
    overlay_video2 = os.path.join(WORK_DIR, "text_overlay_adjusted.mov")
    subprocess.run([
        'ffmpeg', '-y', '-framerate', '60',
        '-i', os.path.join(frames_dir2, 'frame_%05d.png'),
        '-t', str(base_duration),
        '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
        overlay_video2
    ], capture_output=True)
    
    # Step 8: Composite overlay onto base video
    print("\nStep 8: Compositing text overlays...")
    video_with_text = os.path.join(WORK_DIR, "video_with_text.mp4")
    subprocess.run([
        'ffmpeg', '-y',
        '-i', base_video,
        '-i', overlay_video2,
        '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1[v]',
        '-map', '[v]', '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac',
        video_with_text
    ], capture_output=True)
    
    # Step 9: Add background music
    print("\nStep 9: Adding background music...")
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_with_text,
        '-i', MUSIC_PATH,
        '-filter_complex',
        f'[0:a]volume=1.0[original];[1:a]volume=0.12[music];[original][music]amix=inputs=2:duration=first[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        OUTPUT_VIDEO
    ], capture_output=True)
    
    # Get final stats
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration,size',
        '-of', 'default=noprint_wrappers=1', OUTPUT_VIDEO
    ], capture_output=True, text=True)
    
    print("\n" + "=" * 50)
    print("DONE! Final video created:")
    print(f"  Output: {OUTPUT_VIDEO}")
    print(f"  {probe.stdout}")
    print("\nText overlays included:")
    for text_cfg in adjusted_texts:
        print(f"  - '{text_cfg['text']}' @ {text_cfg['start_time']:.1f}s-{text_cfg['end_time']:.1f}s")
    
    # Cleanup temp files
    print("\nCleaning up temporary files...")
    for seg_file in segment_files:
        if os.path.exists(seg_file):
            os.remove(seg_file)


if __name__ == "__main__":
    main()
