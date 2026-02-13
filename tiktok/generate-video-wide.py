#!/usr/bin/env python3
"""Widescreen (16:9) wrapper for generate-video-v4.py — for X/Twitter thread intros"""
import sys, os, json, importlib.util, types

# Load the v4 module despite the hyphenated filename
spec = importlib.util.spec_from_file_location("gen_v4", os.path.join(os.path.dirname(__file__), "generate-video-v4.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

# Override to 16:9 widescreen
gen.WIDTH = 1920
gen.HEIGHT = 1080

# Monkey-patch create_frame to use widescreen-friendly layout
_orig_create_frame = gen.create_frame

def widescreen_create_frame(frame_num, total_frames, lines_with_timing, mfer_circle, audio_duration,
                            palette, particles, subtitle_segments, bg_var, speaking_frames=None):
    import math, random
    from PIL import Image, ImageDraw
    
    W, H = gen.WIDTH, gen.HEIGHT
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)
    
    current_time = frame_num / gen.FPS
    
    # Draw background
    gen.draw_gradient_bg(draw, frame_num, palette)
    if bg_var.get("grid"): gen.draw_vaporwave_grid(draw, frame_num, palette)
    if bg_var.get("shapes"): gen.draw_floating_shapes(draw, frame_num, palette)
    if bg_var.get("particles"):
        for p in particles: p.update(frame_num)
        for p in particles: p.draw(draw)
    if bg_var.get("scan"): gen.draw_scan_lines(draw, frame_num, palette)
    if bg_var.get("sun"): gen.draw_vaporwave_sun(draw, frame_num, palette)
    
    # Avatar — left side for widescreen
    if mfer_circle:
        bounce = int(math.sin(frame_num * 0.08) * 5)
        actual_size = 250
        import PIL.Image
        avatar = mfer_circle.resize((actual_size, actual_size), PIL.Image.LANCZOS)
        avatar_x = 60
        avatar_y = 80 + bounce
        
        speaking = gen.is_speaking(current_time, subtitle_segments)
        if speaking and speaking_frames:
            frame_idx = frame_num % len(speaking_frames)
            avatar = speaking_frames[frame_idx].resize((actual_size, actual_size), PIL.Image.LANCZOS)
        
        # Glow ring
        cx, cy = avatar_x + actual_size // 2, avatar_y + actual_size // 2
        ring_r = actual_size // 2 + 8
        glow_alpha = 0.5 + 0.3 * math.sin(frame_num * 0.1)
        ring_color = tuple(int(c * glow_alpha) for c in palette["accent"][:3])
        draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], outline=ring_color, width=3)
        
        img.paste(avatar, (avatar_x, avatar_y), avatar)
    
    # Handle text — username top-left above avatar
    title_font = gen.get_font(36)
    gen.draw_text_with_glow(draw, (60, 50), "@AgentJc11443", title_font,
                            palette["text"], tuple(int(v * 0.3) for v in palette["accent"][:3]), 1)
    
    # Content text — RIGHT SIDE of screen (next to avatar)
    content_font = gen.get_font(40)
    LEFT_MARGIN = 380  # Right of avatar
    LINE_HEIGHT = 65
    content_top = 100
    content_bottom = 580  # Leave room for subtitle bar
    max_visible = int((content_bottom - content_top) / LINE_HEIGHT)
    
    visible_lines = []
    for line_start, line_end, text, color_name in lines_with_timing:
        if current_time >= line_start:
            progress = min(1.0, (current_time - line_start) / 0.4)
            visible_lines.append((line_start, text, color_name, progress))
    
    scroll_offset = 0
    if len(visible_lines) > max_visible:
        excess = len(visible_lines) - max_visible
        if visible_lines:
            newest_progress = visible_lines[-1][3]
            scroll_offset = int((excess - 1 + newest_progress) * LINE_HEIGHT)
    
    y_pos = content_top - scroll_offset
    
    for line_start, line_end, text, color_name in lines_with_timing:
        if current_time >= line_start:
            progress = min(1.0, (current_time - line_start) / 0.4)
            x_offset = int((1 - progress) * -200)
            alpha_mult = progress
            
            color_map = {
                "accent": palette["accent"],
                "highlight": palette["highlight"],
                "green": (0, 255, 100),
                "yellow": (255, 220, 0),
                "cyan": (0, 220, 255),
            }
            base_color = color_map.get(color_name, (255, 255, 255))
            color = tuple(int(c * alpha_mult) for c in base_color[:3])
            
            if content_top - LINE_HEIGHT <= y_pos <= content_bottom:
                if y_pos < content_top + LINE_HEIGHT:
                    fade = max(0.0, (y_pos - (content_top - LINE_HEIGHT)) / (LINE_HEIGHT * 2))
                    color = tuple(int(c * fade) for c in color[:3])
                
                if progress < 0.3 and random.random() < 0.3:
                    gx = random.randint(-5, 5)
                    gen.draw_text_with_glow(draw, (LEFT_MARGIN + x_offset + gx, y_pos), text, content_font,
                                           palette["highlight"], None)
                
                glow = tuple(int(v * 0.3) for v in palette["accent"][:3]) if color_name == "accent" else None
                gen.draw_text_with_glow(draw, (LEFT_MARGIN + x_offset, y_pos), text, content_font, color, glow, 1)
            y_pos += LINE_HEIGHT
        else:
            y_pos += LINE_HEIGHT
    
    # Subtitle bar — BOTTOM of screen, well below content
    sub_font = gen.get_font(32)
    for seg_start, seg_end, seg_text in subtitle_segments:
        if seg_start <= current_time <= seg_end:
            bar_y = H - 180
            bar_progress = min(1.0, (current_time - seg_start) / 0.15)
            bar_width = int(W * bar_progress)
            
            for dy in range(80):
                alpha = 0.7 * (1 - abs(dy - 40) / 40)
                c = tuple(int(v * alpha * 0.5) for v in palette["bg1"][:3])
                draw.line([(0, bar_y + dy), (bar_width, bar_y + dy)], fill=c)
            
            accent_line = tuple(int(v * bar_progress) for v in palette["accent"][:3])
            draw.line([(0, bar_y), (bar_width, bar_y)], fill=accent_line, width=2)
            draw.line([(0, bar_y + 79), (bar_width, bar_y + 79)], fill=accent_line, width=1)
            
            bbox = sub_font.getbbox(seg_text)
            tw = bbox[2] - bbox[0]
            tx = (W - tw) // 2
            gen.draw_text_with_glow(draw, (tx, bar_y + 22), seg_text, sub_font,
                                    (255, 255, 255), tuple(int(v * 0.4) for v in palette["accent"][:3]), 1)
            break
    
    # Corner brackets
    gen.draw_corner_brackets(draw, palette)
    
    return img

gen.create_frame = widescreen_create_frame

# Run
scripts_path = os.path.join(gen.TIKTOK_DIR, "video-scripts-wide.json")
if not os.path.exists(scripts_path):
    print("No video-scripts-wide.json found")
    sys.exit(1)

with open(scripts_path) as f:
    videos = json.load(f)

idx = int(sys.argv[1]) if len(sys.argv) > 1 else -1
if idx >= 0:
    if idx < len(videos):
        gen.generate_video(videos[idx])
    else:
        print(f"Index {idx} out of range ({len(videos)} videos)")
else:
    for v in videos:
        gen.generate_video(v)
