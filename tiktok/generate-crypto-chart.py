#!/usr/bin/env python3
"""Generate crypto movers bar chart for X thread.
Horizontal bar chart with gainers/losers visualization.
1200x675 (Twitter card optimal), vaporwave/neon aesthetic.
"""

import os, re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 675

# Colors - Pure black background with bright neon colors
BG_DARK = (0, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (191, 64, 255)
NEON_ORANGE = (255, 165, 0)
NEON_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
DIM = (200, 200, 220)

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

def generate_crypto_chart(crypto_data):
    """Generate crypto movers horizontal bar chart.
    
    Args:
        crypto_data: dict with 'gainers' and 'losers' lists
                    each item has: symbol, change_pct, price
    """
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
    
    # Title bar
    font_title = load_bold(48)
    font_date = load_bold(22)
    
    title_text = "CRYPTO MOVERS — TOP 300"
    date_text = datetime.now().strftime("%a %b %d, %Y")
    
    glow(draw, (30, 20), title_text, font_title, NEON_ORANGE, r=3)
    draw.text((30, 72), date_text, font=font_date, fill=DIM)
    
    # Content area
    content_top = 110
    content_height = HEIGHT - content_top - 60
    
    gainers = crypto_data.get('gainers', [])[:5]
    losers = crypto_data.get('losers', [])[:5]
    
    # Center line (zero point)
    center_x = WIDTH // 2
    max_bar_width = center_x - 100  # Max width for bars on each side
    
    # Find max % for scaling
    max_pct = max(
        max([abs(g['change_pct']) for g in gainers], default=10),
        max([abs(l['change_pct']) for l in losers], default=10)
    )
    
    # Bar height and spacing
    total_items = len(gainers) + len(losers)
    bar_height = min(45, (content_height - 40) // total_items)
    spacing = 8
    
    font_symbol = load_bold(24)
    font_pct = load_bold(22)
    font_price = load_bold(18)
    
    # Draw gainers (bars extend right from center)
    y_offset = content_top + 20
    
    # Label
    font_section = load_bold(22)
    glow(draw, (center_x - 100, content_top), "GAINERS", font_section, NEON_GREEN, r=2)
    
    for item in gainers:
        symbol = strip_emoji(item['symbol'])
        pct = item['change_pct']
        price = item['price']
        
        # Calculate bar width (proportional to %)
        bar_w = int((abs(pct) / max_pct) * max_bar_width)
        
        # Gradient bar (green)
        for i in range(bar_w):
            intensity = i / bar_w if bar_w > 0 else 0
            r = int(0 + (0 - 0) * intensity)
            g = int(150 + (255 - 150) * intensity)
            b = int(80 + (128 - 80) * intensity)
            draw.line([(center_x + i, y_offset), (center_x + i, y_offset + bar_height)], fill=(r, g, b, 200))
        
        # Border
        draw.rectangle([(center_x, y_offset), (center_x + bar_w, y_offset + bar_height)], 
                      fill=None, outline=NEON_GREEN, width=2)
        
        # Text on bar
        text_x = center_x + 10
        glow(draw, (text_x, y_offset + 3), symbol, font_symbol, WHITE, r=2)
        glow(draw, (text_x, y_offset + 28), f"+{pct:.1f}%", font_pct, NEON_GREEN, r=2)
        
        # Price on right
        price_text = f"${price:.4f}" if price < 1 else f"${price:.2f}"
        draw.text((center_x + bar_w + 10, y_offset + 12), price_text, font=font_price, fill=DIM)
        
        y_offset += bar_height + spacing
    
    # Space between gainers and losers
    y_offset += 10
    
    # Label
    glow(draw, (center_x - 100, y_offset), "LOSERS", font_section, NEON_PINK, r=2)
    y_offset += 20
    
    # Draw losers (bars extend left from center)
    for item in losers:
        symbol = strip_emoji(item['symbol'])
        pct = item['change_pct']
        price = item['price']
        
        # Calculate bar width (proportional to %)
        bar_w = int((abs(pct) / max_pct) * max_bar_width)
        
        # Gradient bar (red/pink)
        for i in range(bar_w):
            intensity = i / bar_w if bar_w > 0 else 0
            r = int(150 + (255 - 150) * intensity)
            g = int(0 + (0 - 0) * intensity)
            b = int(60 + (128 - 60) * intensity)
            draw.line([(center_x - i, y_offset), (center_x - i, y_offset + bar_height)], fill=(r, g, b, 200))
        
        # Border
        draw.rectangle([(center_x - bar_w, y_offset), (center_x, y_offset + bar_height)], 
                      fill=None, outline=NEON_PINK, width=2)
        
        # Text on bar
        text_x = center_x - bar_w + 10
        glow(draw, (text_x, y_offset + 3), symbol, font_symbol, WHITE, r=2)
        glow(draw, (text_x, y_offset + 28), f"{pct:.1f}%", font_pct, NEON_PINK, r=2)
        
        # Price on left
        price_text = f"${price:.4f}" if price < 1 else f"${price:.2f}"
        draw.text((text_x + 100, y_offset + 12), price_text, font=font_price, fill=DIM)
        
        y_offset += bar_height + spacing
    
    # Center line
    draw.line([(center_x, content_top), (center_x, HEIGHT - 60)], fill=(80, 80, 120), width=2)
    
    # Zero marker
    draw.text((center_x - 15, content_top), "0%", font=load_font(12), fill=DIM)
    
    # Bottom branding bar
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(0, 0, 0, 240))
    draw.line([(0, HEIGHT - 50), (WIDTH, HEIGHT - 50)], fill=NEON_CYAN, width=3)
    
    font_brand = load_bold(26)
    font_sm = load_bold(20)
    glow(draw, (20, HEIGHT - 40), "@AgentJc11443", font_brand, NEON_CYAN, r=2)
    draw.text((260, HEIGHT - 38), "AI-Powered Crypto Tracking", font=font_sm, fill=DIM)
    
    # CRT scanlines
    for sy in range(0, HEIGHT, 3):
        draw.line([(0, sy), (WIDTH, sy)], fill=(0, 0, 0, 12))
    
    return img


if __name__ == "__main__":
    out_dir = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating crypto chart sample...")
    
    # Sample data
    sample_data = {
        'gainers': [
            {'symbol': 'BTC', 'change_pct': 12.34, 'price': 52345.67},
            {'symbol': 'ETH', 'change_pct': 9.87, 'price': 3234.56},
            {'symbol': 'SOL', 'change_pct': 15.23, 'price': 123.45},
            {'symbol': 'DOGE', 'change_pct': 22.45, 'price': 0.0823},
            {'symbol': 'MATIC', 'change_pct': 8.12, 'price': 0.9234},
        ],
        'losers': [
            {'symbol': 'XRP', 'change_pct': -8.45, 'price': 0.5234},
            {'symbol': 'ADA', 'change_pct': -6.78, 'price': 0.4567},
            {'symbol': 'AVAX', 'change_pct': -5.23, 'price': 34.56},
            {'symbol': 'DOT', 'change_pct': -4.12, 'price': 6.789},
            {'symbol': 'LINK', 'change_pct': -3.45, 'price': 15.67},
        ]
    }
    
    img = generate_crypto_chart(sample_data)
    out_path = os.path.join(out_dir, "crypto-chart-sample.png")
    img.save(out_path, "PNG")
    print(f"  ✓ Saved: {out_path}")
