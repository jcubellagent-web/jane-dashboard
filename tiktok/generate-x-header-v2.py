#!/usr/bin/env python3
"""Generate a sleek, modern header card for X threads.
Clean dark aesthetic with accent gradients and sharp typography.
1200x675 (Twitter card optimal).
"""

import os, re, math
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 675

BG_DARK = (8, 8, 16)
ACCENT_BLUE = (59, 130, 246)
ACCENT_CYAN = (34, 211, 238)
ACCENT_GREEN = (74, 222, 128)
ACCENT_PURPLE = (168, 85, 247)
ACCENT_PINK = (236, 72, 153)
ACCENT_ORANGE = (251, 146, 60)
ACCENT_GOLD = (250, 204, 21)
WHITE = (255, 255, 255)
DIM = (120, 120, 150)
SUBTLE = (40, 40, 60)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

def load_font(size):
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def load_bold(size):
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return load_font(size)

def strip_emoji(text):
    return re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\U0001f926-\U0001f937\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF\u200d\ufe0f]+", flags=re.UNICODE).sub("", text).strip()

def load_mfer(size=100):
    for p in [os.path.join(WORKSPACE, "mfer-9581.png"), os.path.join(WORKSPACE, "tiktok", "mfer_circle.png")]:
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            return img.resize((size, size), Image.LANCZOS)
    return None

def draw_gradient_rect(draw, bbox, color_start, color_end, direction='h'):
    x1, y1, x2, y2 = bbox
    if direction == 'h':
        for x in range(x1, x2):
            t = (x - x1) / max(1, x2 - x1)
            r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
            draw.line([(x, y1), (x, y2)], fill=(r, g, b))
    else:
        for y in range(y1, y2):
            t = (y - y1) / max(1, y2 - y1)
            r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
            draw.line([(x1, y), (x2, y)], fill=(r, g, b))

def generate_header(
    date_str="Sunday, February 15th",
    headline="ALPHA INSIGHTS",
    thread_type="WEEKEND EDITION",
    sections=None,
    accent_from=ACCENT_BLUE,
    accent_to=ACCENT_PURPLE,
):
    if sections is None:
        sections = [
            ("AI REVENUE MACHINES", "$MSFT $CRM $ADBE", ACCENT_CYAN),
            ("BREAKOUT STARS", "$PLTR $NOW $SHOP", ACCENT_GREEN),
            ("INFRASTRUCTURE", "$SNOW $MDB $DDOG $CRWD", ACCENT_PURPLE),
            ("QUIET DISRUPTORS", "$DUOL $INTU $HUBS $TEAM", ACCENT_PINK),
            ("FOLLOW THE MONEY", "Anthropic, Waymo, VC wave", ACCENT_GOLD),
            ("THE TAKEAWAY", "Adapt and accelerate", ACCENT_ORANGE),
        ]

    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle corner gradient accents (very faint)
    for y_pos in range(0, 120):
        alpha = max(0, int(6 * (1 - y_pos / 120)))
        draw.line([(0, y_pos), (300, y_pos)], fill=(*accent_from[:3], alpha))
    for y_pos in range(HEIGHT - 100, HEIGHT):
        alpha = max(0, int(4 * ((y_pos - (HEIGHT - 100)) / 100)))
        draw.line([(WIDTH - 400, y_pos), (WIDTH, y_pos)], fill=(*accent_to[:3], alpha))

    # Top accent line — gradient
    draw_gradient_rect(draw, (0, 0, WIDTH, 3), accent_from, accent_to, 'h')

    # Diagonal accent lines (subtle geometric)
    for i in range(5):
        x_off = 80 + i * 18
        draw.line([(x_off, HEIGHT - 120), (x_off + 60, HEIGHT - 180)], fill=(*SUBTLE[:3], 60), width=1)

    # ===== LEFT SIDE =====
    left_w = 620

    font_type_badge = load_bold(16)
    font_date = load_font(20)
    font_headline = load_bold(68)
    font_sub = load_bold(22)

    # Thread type badge — pill shape with gradient fill
    badge_text = f"  {thread_type}  "
    badge_w = len(badge_text) * 11 + 20
    badge_h = 32
    bx, by = 35, 30
    # Rounded rectangle badge
    draw.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=4, fill=accent_from)
    draw.text((bx + 12, by + 6), thread_type, font=font_type_badge, fill=WHITE)

    # Date — clean, dimmed
    draw.text((bx + badge_w + 16, by + 7), date_str, font=font_date, fill=DIM)

    # Main headline — big, clean white with subtle glow
    words = strip_emoji(headline).split()
    lines = []
    line = ""
    for w in words:
        test = f"{line} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_headline)
        if bbox[2] - bbox[0] > left_w - 40:
            lines.append(line)
            line = w
        else:
            line = test
    if line: lines.append(line)

    y = 85
    for l in lines[:3]:
        # Soft glow behind text
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx == 0 and dy == 0: continue
                draw.text((35 + dx, y + dy), strip_emoji(l), font=font_headline, fill=(255, 255, 255, 15))
        draw.text((35, y), strip_emoji(l), font=font_headline, fill=WHITE)
        y += 76

    # Accent underline beneath headline
    draw_gradient_rect(draw, (35, y + 5, 350, y + 8), accent_from, accent_to, 'h')

    # Subtitle / tagline
    draw.text((35, y + 20), "What earnings calls are really telling us", font=font_sub, fill=DIM)

    # ===== mfer PFP — clean circle, bottom-left =====
    mfer_size = 110
    mfer_img = load_mfer(mfer_size)
    if mfer_img:
        mx, my = 35, HEIGHT - mfer_size - 65
        # Glow ring
        ring_r = mfer_size // 2 + 6
        cx, cy = mx + mfer_size // 2, my + mfer_size // 2
        for r in range(ring_r, ring_r - 4, -1):
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(*accent_from[:3], 80))
        # White border
        draw.ellipse([(mx - 2, my - 2), (mx + mfer_size + 2, my + mfer_size + 2)], outline=WHITE, width=2)
        img.paste(mfer_img, (mx, my), mfer_img)

    # @handle
    font_handle = load_bold(22)
    font_tagline = load_font(16)
    draw.text((mx + mfer_size + 14, my + 30), "@AgentJc11443", font=font_handle, fill=ACCENT_CYAN)
    draw.text((mx + mfer_size + 14, my + 58), "AI-Powered News Feed", font=font_tagline, fill=DIM)

    # ===== RIGHT SIDE: Section index =====
    right_x = 660
    
    # Vertical divider — thin gradient line
    for y_pos in range(30, HEIGHT - 55):
        t = (y_pos - 30) / max(1, HEIGHT - 85)
        alpha = int(40 * math.sin(t * math.pi))
        draw.point((left_w + 25, y_pos), fill=(*SUBTLE[:3], alpha))

    sec_top = 28
    font_sec_header = load_bold(13)
    font_sec_name = load_bold(18)
    font_sec_detail = load_font(13)

    # "IN THIS THREAD" — minimal
    draw.text((right_x, sec_top), "IN THIS THREAD", font=font_sec_header, fill=DIM)
    draw.line([(right_x, sec_top + 18), (WIDTH - 35, sec_top + 18)], fill=SUBTLE, width=1)

    sec_y = sec_top + 30
    available_h = HEIGHT - 70 - sec_y
    sec_spacing = min(58, available_h // max(1, len(sections)))

    for i, (name, detail, color) in enumerate(sections):
        num = str(i + 2)
        
        # Colored left accent bar instead of number badge
        draw.rectangle([(right_x, sec_y + 2), (right_x + 3, sec_y + 22)], fill=color)
        
        # Number — small, colored
        draw.text((right_x + 10, sec_y + 1), num, font=font_sec_header, fill=color)
        
        # Section name
        draw.text((right_x + 28, sec_y), name, font=font_sec_name, fill=WHITE)

        # Detail
        draw.text((right_x + 28, sec_y + 24), strip_emoji(detail), font=font_sec_detail, fill=DIM)

        # Subtle separator
        if i < len(sections) - 1:
            sep_y = sec_y + sec_spacing - 8
            draw.line([(right_x, sep_y), (WIDTH - 35, sep_y)], fill=(30, 30, 45), width=1)

        sec_y += sec_spacing

    # ===== BOTTOM BAR =====
    draw.line([(0, HEIGHT - 48), (WIDTH, HEIGHT - 48)], fill=SUBTLE, width=1)
    draw_gradient_rect(draw, (0, HEIGHT - 48, WIDTH, HEIGHT - 46), accent_from, accent_to, 'h')

    font_bottom = load_font(16)
    draw.text((WIDTH - 160, HEIGHT - 36), "7-tweet thread", font=font_bottom, fill=DIM)

    return img


if __name__ == "__main__":
    out = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out, exist_ok=True)
    img = generate_header()
    img.save(os.path.join(out, "test-v2.png"))
    print("Saved test-v2.png")
