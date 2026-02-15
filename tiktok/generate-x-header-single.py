#!/usr/bin/env python3
"""Generate a single eye-catching header card for X thread.
Shows the thread headline + visual index of all sections.
1200x675 (Twitter card optimal), vaporwave/neon aesthetic.
"""

import os, re
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 675

# Colors
BG_DARK = (10, 10, 20)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)
NEON_PURPLE = (180, 0, 255)
NEON_ORANGE = (255, 165, 0)
NEON_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DIM = (150, 150, 180)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

def load_font(size):
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Bold.ttf"]:
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

def glow(draw, pos, text, font, color, r=2):
    x, y = pos
    text = strip_emoji(text)
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            if dx==0 and dy==0: continue
            draw.text((x+dx, y+dy), text, font=font, fill=(*color[:3], 50))
    draw.text((x, y), text, font=font, fill=color)

def load_mfer(size=100):
    for p in [os.path.join(WORKSPACE, "tiktok", "mfer_avatar.png"), os.path.join(WORKSPACE, "assets", "mfer.png")]:
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            return img.resize((size, size), Image.LANCZOS)
    return None

def generate_thread_header(
    date_str="Thu Feb 13, 2026",
    storm=True,
    headline="CPI Comes in Cool — Markets Rally Hard",
    thread_type="DAILY BRIEF",  # or "UPDATE" or "DAILY RECAP"
    sections=None
):
    """Generate single header card showing thread headline + section index."""
    
    if sections is None:
        sections = [
            ("AI PROVIDERS", "Anthropic, OpenAI, xAI, Meta, DeepSeek, Google", NEON_CYAN),
            ("VENTURE, PE & M&A", "VC rounds, PE deals, M&A, rumor mill", NEON_GOLD),
            ("ENTERPRISE SaaS", "$CRM $NOW $WDAY $PLTR $DUOL", NEON_GREEN),
            ("GEOPOLITICS & MACRO", "Trade wars, sanctions, tariffs, conflicts", (255, 100, 100)),
            ("NASDAQ 100", "Top 5 gainers + Top 5 losers", NEON_PINK),
            ("CRYPTO MOVERS", "Top gainers + losers, top 300", NEON_ORANGE),
            ("HOT TAKE", "One sharp observation", NEON_PURPLE),
        ]
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Subtle grid
    for x in range(0, WIDTH, 50):
        draw.line([(x, 0), (x, HEIGHT)], fill=(25, 25, 50, 30))
    for y in range(0, HEIGHT, 50):
        draw.line([(0, y), (WIDTH, y)], fill=(25, 25, 50, 30))
    
    # Top gradient bar
    for i in range(WIDTH):
        ratio = i / WIDTH
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        b = 255
        draw.line([(i, 0), (i, 5)], fill=(r, g, b))
    
    # ===== LEFT SIDE: Headline area =====
    left_w = 650
    
    # "AI DAILY BRIEF" or thread type
    font_type = load_bold(18)
    font_date = load_bold(20)
    font_title = load_bold(56)
    font_headline = load_bold(28)
    font_storm = load_bold(22)
    
    # Type badge
    badge_text = f"AI {thread_type}"
    draw.rectangle([(30, 20), (30 + len(badge_text)*12 + 20, 50)], fill=NEON_CYAN, outline=None)
    draw.text((40, 25), badge_text, font=font_type, fill=BG_DARK)
    
    # Date
    draw.text((30 + len(badge_text)*12 + 35, 25), date_str, font=font_date, fill=DIM)
    
    # Main headline
    words = strip_emoji(headline).split()
    lines = []
    line = ""
    for w in words:
        test = f"{line} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_title)
        if bbox[2] - bbox[0] > left_w - 60:
            lines.append(line)
            line = w
        else:
            line = test
    if line: lines.append(line)
    
    y = 70
    for l in lines[:3]:
        glow(draw, (30, y), l, font_title, WHITE, r=3)
        y += 62
    
    # Storm check
    storm_y = y + 10
    storm_text = "STORM CHECK: YES — BREAKING" if storm else "STORM CHECK: NO"
    storm_color = NEON_PINK if storm else (80, 80, 100)
    draw.rectangle([(30, storm_y), (left_w, storm_y + 35)], fill=(30, 10, 25, 180) if storm else (20, 20, 30, 180))
    glow(draw, (40, storm_y + 5), storm_text, font_storm, storm_color, r=1)
    
    # ===== RIGHT SIDE: Section index =====
    right_x = 670
    section_top = 20
    
    font_section_title = load_bold(13)
    font_idx_name = load_bold(17)
    font_idx_detail = load_font(13)
    
    # "IN THIS THREAD" header
    draw.text((right_x, section_top), "IN THIS THREAD", font=font_section_title, fill=NEON_CYAN)
    draw.line([(right_x, section_top + 18), (WIDTH - 30, section_top + 18)], fill=NEON_CYAN, width=1)
    
    sec_y = section_top + 28
    for i, (name, detail, color) in enumerate(sections):
        # Number badge
        num = str(i + 2)  # starts at tweet 2
        draw.rectangle([(right_x, sec_y), (right_x + 24, sec_y + 24)], fill=color)
        draw.text((right_x + 7 if len(num)==1 else right_x+4, sec_y + 3), num, font=font_section_title, fill=BG_DARK)
        
        # Section name
        glow(draw, (right_x + 32, sec_y), name, font_idx_name, color, r=1)
        
        # Detail text
        draw.text((right_x + 32, sec_y + 22), strip_emoji(detail), font=font_idx_detail, fill=DIM)
        
        # Separator line
        if i < len(sections) - 1:
            draw.line([(right_x, sec_y + 42), (WIDTH - 30, sec_y + 42)], fill=(40, 40, 60, 100))
        
        sec_y += 48
    
    # Vertical divider between left and right
    draw.line([(left_w + 15, 15), (left_w + 15, HEIGHT - 60)], fill=(40, 40, 80), width=1)
    
    # ===== BOTTOM BAR: Branding =====
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(5, 5, 15, 240))
    draw.line([(0, HEIGHT - 50), (WIDTH, HEIGHT - 50)], fill=NEON_CYAN, width=2)
    
    font_brand = load_bold(22)
    font_sm = load_font(16)
    glow(draw, (20, HEIGHT - 40), "@AgentJc11443", font_brand, NEON_CYAN)
    draw.text((220, HEIGHT - 38), "AI-Powered News Feed", font=font_sm, fill=DIM)
    draw.text((WIDTH - 180, HEIGHT - 38), "8-tweet thread", font=font_sm, fill=DIM)
    
    # mfer avatar bottom-right
    avatar = load_mfer(45)
    if avatar:
        img.paste(avatar, (WIDTH - 60, HEIGHT - 52), avatar)
    
    # CRT scanlines
    for sy in range(0, HEIGHT, 3):
        draw.line([(0, sy), (WIDTH, sy)], fill=(0, 0, 0, 12))
    
    return img


if __name__ == "__main__":
    out_dir = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating single thread header prototypes...")
    
    # Morning brief
    img1 = generate_thread_header(
        date_str="Thu Feb 13, 2026",
        storm=True,
        headline="CPI Comes in Cool — Markets Rally Hard",
        thread_type="DAILY BRIEF",
    )
    img1.save(os.path.join(out_dir, "header-morning-brief.png"), "PNG")
    print("  Saved: header-morning-brief.png")
    
    # Update brief
    img2 = generate_thread_header(
        date_str="Thu Feb 13, 2026 — 4:30 PM",
        storm=False,
        headline="Markets Digest CPI — Tech Leads Recovery",
        thread_type="UPDATE",
    )
    img2.save(os.path.join(out_dir, "header-update-brief.png"), "PNG")
    print("  Saved: header-update-brief.png")
    
    # Daily recap
    img3 = generate_thread_header(
        date_str="Thu Feb 13, 2026",
        storm=True,
        headline="Wall Street Sorts AI Winners From Victims",
        thread_type="DAILY RECAP",
    )
    img3.save(os.path.join(out_dir, "header-daily-recap.png"), "PNG")
    print("  Saved: header-daily-recap.png")
    
    print("\nDone! 3 header variants generated.")
