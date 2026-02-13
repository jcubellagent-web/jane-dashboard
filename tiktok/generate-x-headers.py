#!/usr/bin/env python3
"""Generate news-style header cards for X/Twitter threads.
1200x675 (16:9 Twitter card optimal), vaporwave/neon aesthetic.
"""

import os, sys, re, json
from PIL import Image, ImageDraw, ImageFont

# Dimensions — Twitter card optimal
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
DARK_PANEL = (15, 15, 35, 220)
ACCENT_LINE = (0, 255, 255, 180)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

# Fonts
def load_font(size):
    paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def load_bold_font(size):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return load_font(size)

def strip_emoji(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2600-\u26FF"
        "\u2700-\u27BF"
        "\u200d\ufe0f"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text).strip()

def draw_glow_text(draw, pos, text, font, color, glow_radius=2):
    """Draw text with a subtle glow effect."""
    x, y = pos
    text = strip_emoji(text)
    # Glow layers
    glow_color = (*color[:3], 60) if len(color) == 3 else (*color[:3], 60)
    for dx in range(-glow_radius, glow_radius + 1):
        for dy in range(-glow_radius, glow_radius + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=color)

def draw_gradient_bar(draw, y, width, height, color_start, color_end):
    """Draw a horizontal gradient bar."""
    for i in range(width):
        ratio = i / width
        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
        draw.line([(i, y), (i, y + height)], fill=(r, g, b))

def draw_scanlines(img, opacity=15):
    """Add CRT scanline effect."""
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(0, HEIGHT, 3):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, opacity))

def load_mfer_avatar(size=120):
    """Load mfer PFP if available."""
    paths = [
        os.path.join(WORKSPACE, "tiktok", "mfer_avatar.png"),
        os.path.join(WORKSPACE, "assets", "mfer.png"),
    ]
    for p in paths:
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            return img
    return None

def create_base_card():
    """Create base card with dark bg and grid pattern."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Subtle grid
    for x in range(0, WIDTH, 40):
        draw.line([(x, 0), (x, HEIGHT)], fill=(30, 30, 60, 40))
    for y in range(0, HEIGHT, 40):
        draw.line([(0, y), (WIDTH, y)], fill=(30, 30, 60, 40))
    
    return img, draw

def add_branding(draw, img, date_str="Feb 13, 2026"):
    """Add @AgentJc11443 branding + mfer avatar."""
    font_sm = load_font(18)
    font_brand = load_bold_font(22)
    
    # Bottom bar
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(5, 5, 15, 230))
    draw.line([(0, HEIGHT - 50), (WIDTH, HEIGHT - 50)], fill=NEON_CYAN, width=2)
    
    # Brand text
    draw_glow_text(draw, (20, HEIGHT - 40), "@AgentJc11443", font_brand, NEON_CYAN)
    draw_glow_text(draw, (WIDTH - 200, HEIGHT - 40), date_str, font_sm, (150, 150, 180))
    
    # mfer avatar in top-right
    avatar = load_mfer_avatar(80)
    if avatar:
        img.paste(avatar, (WIDTH - 100, 15), avatar)

def card_storm_check(date_str="Thu Feb 13", storm=True, headline="CPI Comes in Cool — Markets Rip"):
    """Tweet 1: Storm Check / Anchor."""
    img, draw = create_base_card()
    
    # Top accent bar — gradient
    draw_gradient_bar(draw, 0, WIDTH, 6, (255, 0, 128), (0, 255, 255))
    
    # "AI DAILY BRIEF" header
    font_huge = load_bold_font(72)
    font_lg = load_bold_font(42)
    font_md = load_bold_font(30)
    font_sm = load_font(22)
    
    draw_glow_text(draw, (40, 30), "AI DAILY BRIEF", font_huge, WHITE, glow_radius=3)
    draw_glow_text(draw, (40, 115), date_str, font_lg, NEON_CYAN)
    
    # Storm check box
    box_y = 190
    draw.rectangle([(30, box_y), (WIDTH - 30, box_y + 180)], fill=(20, 20, 40, 200), outline=NEON_PINK if storm else (80, 80, 100), width=2)
    
    storm_label = "STORM CHECK: YES" if storm else "STORM CHECK: NO"
    storm_color = NEON_PINK if storm else (120, 120, 150)
    draw_glow_text(draw, (60, box_y + 20), storm_label, font_md, storm_color)
    
    # Headline
    draw_glow_text(draw, (60, box_y + 70), strip_emoji(headline), font_lg, WHITE)
    
    # "Thread below" indicator
    draw_glow_text(draw, (40, 420), "FULL THREAD BELOW", font_md, NEON_GREEN)
    
    # Decorative dots
    for i in range(7):
        color = [NEON_CYAN, NEON_PINK, NEON_GREEN, NEON_PURPLE, NEON_ORANGE, NEON_GOLD, WHITE][i]
        draw.ellipse([(40 + i * 50, 480), (60 + i * 50, 500)], fill=color)
        labels = ["AI", "VC", "SaaS", "NDX", "CRY", "HOT", "CTA"]
        draw.text((35 + i * 50, 505), labels[i], font=load_font(12), fill=(150, 150, 180))
    
    draw_scanlines(img)
    add_branding(draw, img, date_str)
    return img

def card_ai_providers(providers=None):
    """Tweet 2: AI Provider updates."""
    img, draw = create_base_card()
    
    if providers is None:
        providers = [
            ("Anthropic", "Claude pushed to classified DoD networks", NEON_CYAN),
            ("OpenAI", "Ads rolling out in ChatGPT Free", NEON_GREEN),
            ("xAI", "Absorbed into SpaceX operations", NEON_PURPLE),
            ("Meta AI", "Open-source Llama 4 rumors swirl", (0, 120, 255)),
            ("DeepSeek", "R2 model benchmarks leaked", NEON_ORANGE),
            ("Google", "Gemini 2.5 enterprise push", NEON_PINK),
        ]
    
    # Header
    draw_gradient_bar(draw, 0, WIDTH, 6, (0, 255, 255), (180, 0, 255))
    font_title = load_bold_font(52)
    font_provider = load_bold_font(26)
    font_desc = load_font(20)
    
    draw_glow_text(draw, (40, 20), "FOUNDATIONAL MODEL PROVIDERS", font_title, NEON_CYAN, glow_radius=3)
    
    # Provider rows
    y = 100
    for name, desc, color in providers[:6]:
        # Color indicator dot
        draw.ellipse([(40, y + 8), (56, y + 24)], fill=color)
        draw_glow_text(draw, (70, y), name.upper(), font_provider, color)
        draw.text((70, y + 32), strip_emoji(desc), font=font_desc, fill=(200, 200, 220))
        y += 80
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img

def card_venture_pe(deals=None):
    """Tweet 3: Venture, PE & M&A."""
    img, draw = create_base_card()
    
    draw_gradient_bar(draw, 0, WIDTH, 6, (255, 215, 0), (255, 0, 128))
    font_title = load_bold_font(48)
    font_section = load_bold_font(24)
    font_deal = load_font(20)
    
    draw_glow_text(draw, (40, 20), "VENTURE, PE & M&A", font_title, NEON_GOLD, glow_radius=3)
    
    # Three columns
    col_w = 370
    sections = [
        ("VENTURE / GROWTH", NEON_GREEN, [
            "Anthropic — $20B @ $300B val",
            "Sakana AI — $500M Series B",
            "Cursor — $200M growth round",
        ]),
        ("PRIVATE EQUITY", NEON_PURPLE, [
            "Blackstone → Anthropic stake",
            "KKR → ServiceNow cloud unit",
            "TPG → DataRobot buyout",
        ]),
        ("M&A / STRATEGIC", NEON_PINK, [
            "SpaceX absorbs xAI ops",
            "Savvy Games → Moonton $6B",
            "Samsung HBM4 supply deal",
        ]),
    ]
    
    for i, (title, color, items) in enumerate(sections):
        x = 30 + i * col_w
        draw.rectangle([(x, 90), (x + col_w - 20, 560)], fill=(15, 15, 35, 200), outline=color, width=1)
        draw_glow_text(draw, (x + 15, 100), title, font_section, color)
        draw.line([(x + 15, 132), (x + col_w - 35, 132)], fill=color, width=1)
        
        for j, deal in enumerate(items):
            draw.text((x + 15, 145 + j * 55), strip_emoji(deal), font=font_deal, fill=(200, 200, 220))
    
    # Rumor mill strip
    draw.rectangle([(30, 570), (WIDTH - 30, 610)], fill=(40, 20, 40, 200), outline=NEON_ORANGE, width=1)
    draw_glow_text(draw, (50, 578), "RUMOR MILL:", font_section, NEON_ORANGE)
    draw.text((250, 582), "Stripe IPO Q3 rumors intensify  |  Apple AI acquisitions in stealth mode", font=font_deal, fill=(200, 180, 150))
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img

def card_enterprise_saas(tickers=None):
    """Tweet 4: Enterprise SaaS."""
    img, draw = create_base_card()
    
    if tickers is None:
        tickers = [
            ("$CRM", "Salesforce", "+2.52%", True, "Agentforce momentum"),
            ("$NOW", "ServiceNow", "+3.74%", True, "AI workflow demand"),
            ("$WDAY", "Workday", "+0.85%", True, "HCM AI features"),
            ("$PLTR", "Palantir", "+2.72%", True, "AIP growth thesis"),
            ("$DUOL", "Duolingo", "+0.63%", True, "AI tutor expansion"),
        ]
    
    draw_gradient_bar(draw, 0, WIDTH, 6, (0, 255, 128), (0, 180, 255))
    font_title = load_bold_font(48)
    font_ticker = load_bold_font(36)
    font_name = load_font(20)
    font_pct = load_bold_font(30)
    font_note = load_font(18)
    
    draw_glow_text(draw, (40, 20), "AI IMPACT ON ENTERPRISE SaaS", font_title, NEON_GREEN, glow_radius=3)
    
    y = 100
    for ticker, name, pct, is_up, note in tickers:
        color = NEON_GREEN if is_up else NEON_PINK
        # Ticker box
        draw.rectangle([(30, y), (WIDTH - 30, y + 95)], fill=(15, 15, 35, 200), outline=(40, 40, 70), width=1)
        draw_glow_text(draw, (50, y + 10), ticker, font_ticker, color)
        draw.text((200, y + 15), name, font=font_name, fill=(150, 150, 180))
        draw_glow_text(draw, (WIDTH - 200, y + 10), pct, font_pct, color)
        draw.text((50, y + 58), strip_emoji(note), font=font_note, fill=(180, 180, 200))
        y += 105
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img

def card_nasdaq_movers(gainers=None, losers=None):
    """Tweet 5: NASDAQ 100 Top Movers."""
    img, draw = create_base_card()
    
    if gainers is None:
        gainers = [("$COIN", "+18.0%"), ("$FSLY", "+15.2%"), ("$AMAT", "+9.6%"), ("$MRVL", "+5.3%"), ("$NVDA", "+3.1%")]
    if losers is None:
        losers = [("$CSCO", "-12.3%"), ("$DASH", "-8.2%"), ("$MSTR", "-7.9%"), ("$AAPL", "-5.0%"), ("$AMD", "-5.0%")]
    
    draw_gradient_bar(draw, 0, WIDTH, 6, (0, 255, 128), (255, 0, 128))
    font_title = load_bold_font(48)
    font_ticker = load_bold_font(32)
    font_pct = load_bold_font(28)
    font_label = load_bold_font(22)
    
    draw_glow_text(draw, (40, 20), "NASDAQ 100 — TOP MOVERS", font_title, WHITE, glow_radius=3)
    
    # Two columns
    mid = WIDTH // 2
    
    # Gainers
    draw_glow_text(draw, (60, 90), "GAINERS", font_label, NEON_GREEN)
    draw.line([(60, 118), (mid - 40, 118)], fill=NEON_GREEN, width=2)
    for i, (ticker, pct) in enumerate(gainers[:5]):
        y = 130 + i * 90
        draw.rectangle([(40, y), (mid - 20, y + 75)], fill=(10, 30, 15, 200), outline=(0, 100, 50), width=1)
        draw_glow_text(draw, (60, y + 10), ticker, font_ticker, WHITE)
        draw_glow_text(draw, (mid - 180, y + 12), pct, font_pct, NEON_GREEN)
    
    # Losers
    draw_glow_text(draw, (mid + 40, 90), "LOSERS", font_label, NEON_PINK)
    draw.line([(mid + 40, 118), (WIDTH - 40, 118)], fill=NEON_PINK, width=2)
    for i, (ticker, pct) in enumerate(losers[:5]):
        y = 130 + i * 90
        draw.rectangle([(mid + 20, y), (WIDTH - 40, y + 75)], fill=(30, 10, 15, 200), outline=(100, 0, 50), width=1)
        draw_glow_text(draw, (mid + 40, y + 10), ticker, font_ticker, WHITE)
        draw_glow_text(draw, (WIDTH - 200, y + 12), pct, font_pct, NEON_PINK)
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img

def card_crypto_movers(gainers=None, losers=None):
    """Tweet 6: Crypto Movers."""
    img, draw = create_base_card()
    
    if gainers is None:
        gainers = [("HUMANITY", "+37.8%"), ("RIVER", "+31.4%"), ("POL", "+12.1%"), ("AAVE", "+9.8%"), ("SOL", "+9.9%")]
    if losers is None:
        losers = [("BERA", "-24.7%"), ("LAYER", "-18.3%"), ("IP", "-15.2%"), ("TRUMP", "-8.1%"), ("DOGE", "-4.2%")]
    
    draw_gradient_bar(draw, 0, WIDTH, 6, (255, 165, 0), (180, 0, 255))
    font_title = load_bold_font(48)
    font_coin = load_bold_font(30)
    font_pct = load_bold_font(26)
    font_label = load_bold_font(22)
    
    draw_glow_text(draw, (40, 20), "CRYPTO MOVERS — TOP 300", font_title, NEON_ORANGE, glow_radius=3)
    
    mid = WIDTH // 2
    
    # Gainers
    draw_glow_text(draw, (60, 90), "BIGGEST GAINERS", font_label, NEON_GREEN)
    draw.line([(60, 118), (mid - 40, 118)], fill=NEON_GREEN, width=2)
    for i, (coin, pct) in enumerate(gainers[:5]):
        y = 130 + i * 90
        draw.rectangle([(40, y), (mid - 20, y + 75)], fill=(10, 25, 20, 200), outline=(0, 80, 50), width=1)
        draw_glow_text(draw, (60, y + 12), coin, font_coin, WHITE)
        draw_glow_text(draw, (mid - 180, y + 14), pct, font_pct, NEON_GREEN)
    
    # Losers
    draw_glow_text(draw, (mid + 40, 90), "BIGGEST LOSERS", font_label, NEON_PINK)
    draw.line([(mid + 40, 118), (WIDTH - 40, 118)], fill=NEON_PINK, width=2)
    for i, (coin, pct) in enumerate(losers[:5]):
        y = 130 + i * 90
        draw.rectangle([(mid + 20, y), (WIDTH - 40, y + 75)], fill=(25, 10, 20, 200), outline=(80, 0, 50), width=1)
        draw_glow_text(draw, (mid + 40, y + 12), coin, font_coin, WHITE)
        draw_glow_text(draw, (WIDTH - 200, y + 14), pct, font_pct, NEON_PINK)
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img

def card_hot_take(take="Wall Street learned to short AI hype — but not AI infrastructure."):
    """Tweet 7: Hot Take."""
    img, draw = create_base_card()
    
    draw_gradient_bar(draw, 0, WIDTH, 6, (255, 0, 128), (255, 165, 0))
    font_title = load_bold_font(52)
    font_take = load_bold_font(36)
    
    draw_glow_text(draw, (40, 30), "TAKE OF THE DAY", font_title, NEON_PINK, glow_radius=3)
    
    # Big quote box
    draw.rectangle([(30, 120), (WIDTH - 30, 520)], fill=(20, 10, 25, 220), outline=NEON_PINK, width=2)
    
    # Quote marks
    font_quote = load_bold_font(120)
    draw.text((50, 100), '"', font=font_quote, fill=(255, 0, 128, 80))
    
    # Wrap text
    words = strip_emoji(take).split()
    lines = []
    line = ""
    for w in words:
        test = f"{line} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font_take)
        if bbox[2] - bbox[0] > WIDTH - 140:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    
    y = 180
    for l in lines[:4]:
        draw_glow_text(draw, (70, y), l, font_take, WHITE)
        y += 55
    
    draw_scanlines(img)
    add_branding(draw, img)
    return img


if __name__ == "__main__":
    out_dir = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating X thread header prototypes...")
    
    cards = [
        ("01-storm-check.png", card_storm_check()),
        ("02-ai-providers.png", card_ai_providers()),
        ("03-venture-pe-ma.png", card_venture_pe()),
        ("04-enterprise-saas.png", card_enterprise_saas()),
        ("05-nasdaq-movers.png", card_nasdaq_movers()),
        ("06-crypto-movers.png", card_crypto_movers()),
        ("07-hot-take.png", card_hot_take()),
    ]
    
    for name, img in cards:
        path = os.path.join(out_dir, name)
        img.save(path, "PNG")
        print(f"  Saved: {path}")
    
    print(f"\nDone! {len(cards)} cards generated in {out_dir}")
