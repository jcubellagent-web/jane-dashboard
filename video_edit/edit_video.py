#!/usr/bin/env python3
"""
TikTok Video Editor - Patriots Pack Rip
Adds text overlays and background music
"""

from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# Paths
VIDEO_PATH = "/Users/jc_agent/.openclaw/media/inbound/f409bb67-7fbc-4ca3-9df2-d5d1d1d289d6.mp4"
OUTPUT_PATH = "/Users/jc_agent/.openclaw/workspace/video_edit/patriots_final.mp4"

def create_text_clip(text, fontsize=40, color='white', stroke_color='black', stroke_width=3, duration=3, position='center'):
    """Create a text clip with stroke effect using PIL"""
    # Create image with text
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except:
        font = ImageFont.load_default()
    
    # Calculate text size
    dummy_img = Image.new('RGBA', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0] + stroke_width * 4
    text_height = bbox[3] - bbox[1] + stroke_width * 4
    
    # Create image
    img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    x, y = 10, 10
    
    # Draw stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=color)
    
    # Convert to numpy array
    img_array = np.array(img)
    
    # Create clip
    clip = ImageClip(img_array, duration=duration)
    return clip

def main():
    print("Loading video...")
    video = VideoFileClip(VIDEO_PATH)
    
    print(f"Video duration: {video.duration}s")
    print(f"Video size: {video.size}")
    
    # Create text overlays
    print("Creating text overlays...")
    
    # Opening text - "PATRIOTS TO THE SUPER BOWL 🏈"
    text1 = create_text_clip("PATRIOTS TO THE\nSUPER BOWL 🏈", fontsize=38, color='red', duration=4)
    text1 = text1.with_position(('center', 80)).with_start(0)
    
    # "$60 PACK" 
    text2 = create_text_clip("$60 PACK 💰", fontsize=32, color='yellow', duration=4)
    text2 = text2.with_position(('center', 160)).with_start(0)
    
    # "Hunting for DRAKE MAYE"
    text3 = create_text_clip("Hunting for DRAKE MAYE 👀", fontsize=30, color='white', duration=4)
    text3 = text3.with_position(('center', 220)).with_start(0)
    
    # Mid video - when cards reveal (around 15-25 sec)
    text4 = create_text_clip("JJ McCARTHY /99 🔥", fontsize=36, color='cyan', duration=4)
    text4 = text4.with_position(('center', 100)).with_start(15)
    
    text5 = create_text_clip("FRED TAYLOR 2/99! 🎯", fontsize=36, color='lime', duration=4)
    text5 = text5.with_position(('center', 100)).with_start(25)
    
    # End CTA
    text6 = create_text_clip("LIKE & COMMENT\nIF I SHOULD RIP MORE! 🔥", fontsize=34, color='white', duration=5)
    text6 = text6.with_position(('center', 120)).with_start(video.duration - 5)
    
    # Composite all clips
    print("Compositing video...")
    final = CompositeVideoClip([
        video,
        text1,
        text2,
        text3,
        text4,
        text5,
        text6
    ])
    
    # Write output
    print("Rendering final video...")
    final.write_videofile(
        OUTPUT_PATH,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='fast'
    )
    
    print(f"Done! Output saved to: {OUTPUT_PATH}")
    
    # Cleanup
    video.close()
    final.close()

if __name__ == "__main__":
    main()
