#!/usr/bin/env python3
"""Generate NASDAQ 100 movers heatmap for X thread.
Treemap-style layout with gainers/losers visualization.
1200x675 (Twitter card optimal), vaporwave/neon aesthetic.
"""

import os, re, math
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

def get_color_for_change(pct, is_gainer=True):
    """Return gradient color based on % change."""
    abs_pct = abs(pct)
    intensity = min(abs_pct / 10.0, 1.0)  # Scale to 0-1, cap at 10%
    
    if is_gainer:
        # Green gradient: darker green to bright neon green
        r = int(0 + (0 - 0) * intensity)
        g = int(100 + (255 - 100) * intensity)
        b = int(50 + (128 - 50) * intensity)
    else:
        # Red/Pink gradient: darker red to bright neon pink
        r = int(100 + (255 - 100) * intensity)
        g = int(0 + (0 - 0) * intensity)
        b = int(30 + (128 - 30) * intensity)
    
    return (r, g, b)

def simple_treemap(items, x, y, w, h):
    """Simple treemap layout - returns list of (item, x, y, w, h) tuples."""
    if not items:
        return []
    
    # Sort by size (change_pct)
    sorted_items = sorted(items, key=lambda x: abs(x['change_pct']), reverse=True)
    
    total = sum(abs(i['change_pct']) for i in sorted_items)
    if total == 0:
        return []
    
    boxes = []
    area = w * h
    
    # Split space proportionally
    if len(sorted_items) <= 3:
        # Simple vertical stack
        current_y = y
        for item in sorted_items:
            ratio = abs(item['change_pct']) / total
            box_h = int(h * ratio)
            if item == sorted_items[-1]:  # Last one gets remaining space
                box_h = y + h - current_y
            boxes.append((item, x, current_y, w, max(box_h, 30)))
            current_y += box_h
    else:
        # Grid layout - 2 columns
        left_items = sorted_items[:len(sorted_items)//2]
        right_items = sorted_items[len(sorted_items)//2:]
        
        col_w = w // 2
        
        # Left column
        current_y = y
        left_total = sum(abs(i['change_pct']) for i in left_items)
        for item in left_items:
            ratio = abs(item['change_pct']) / left_total if left_total > 0 else 1.0 / len(left_items)
            box_h = int(h * ratio)
            if item == left_items[-1]:
                box_h = y + h - current_y
            boxes.append((item, x, current_y, col_w, max(box_h, 30)))
            current_y += box_h
        
        # Right column
        current_y = y
        right_total = sum(abs(i['change_pct']) for i in right_items)
        for item in right_items:
            ratio = abs(item['change_pct']) / right_total if right_total > 0 else 1.0 / len(right_items)
            box_h = int(h * ratio)
            if item == right_items[-1]:
                box_h = y + h - current_y
            boxes.append((item, x + col_w, current_y, col_w, max(box_h, 30)))
            current_y += box_h
    
    return boxes

def generate_nasdaq_heatmap(movers_data):
    """Generate NASDAQ 100 movers heatmap.
    
    Args:
        movers_data: dict with 'gainers' and 'losers' lists
                    each item has: ticker, name, change_pct, price
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
    
    title_text = "NASDAQ 100 MOVERS"
    date_text = datetime.now().strftime("%a %b %d, %Y")
    
    glow(draw, (30, 20), title_text, font_title, NEON_CYAN, r=3)
    draw.text((30, 72), date_text, font=font_date, fill=DIM)
    
    # Content area
    content_top = 100
    content_height = HEIGHT - content_top - 60  # Leave room for bottom bar
    
    # Split area: Gainers left, Losers right
    mid_x = WIDTH // 2
    padding = 20
    
    gainers = movers_data.get('gainers', [])[:5]
    losers = movers_data.get('losers', [])[:5]
    
    # Section labels
    font_label = load_bold(24)
    glow(draw, (padding + 10, content_top + 5), "GAINERS", font_label, NEON_GREEN, r=2)
    glow(draw, (mid_x + padding + 10, content_top + 5), "LOSERS", font_label, NEON_PINK, r=2)
    
    treemap_top = content_top + 30
    treemap_height = content_height - 30
    
    # Generate treemaps
    gainer_boxes = simple_treemap(gainers, padding, treemap_top, mid_x - 2*padding, treemap_height)
    loser_boxes = simple_treemap(losers, mid_x + padding, treemap_top, mid_x - 2*padding, treemap_height)
    
    # Draw boxes
    font_ticker = load_bold(32)
    font_pct = load_bold(26)
    font_price = load_bold(18)
    
    for item, bx, by, bw, bh in gainer_boxes:
        color = get_color_for_change(item['change_pct'], is_gainer=True)
        # Box with border
        draw.rectangle([(bx, by), (bx + bw - 2, by + bh - 2)], fill=(*color, 180), outline=NEON_GREEN, width=2)
        
        # Text
        ticker = strip_emoji(item['ticker'])
        pct_text = f"+{item['change_pct']:.2f}%"
        price_text = f"${item['price']:.2f}"
        
        # Center text in box
        text_y = by + (bh - 60) // 2
        if bh >= 50:
            glow(draw, (bx + 10, text_y), ticker, font_ticker, WHITE, r=2)
            glow(draw, (bx + 10, text_y + 38), pct_text, font_pct, NEON_GREEN, r=2)
            draw.text((bx + 10, text_y + 68), price_text, font=font_price, fill=DIM)
    
    for item, bx, by, bw, bh in loser_boxes:
        color = get_color_for_change(item['change_pct'], is_gainer=False)
        # Box with border
        draw.rectangle([(bx, by), (bx + bw - 2, by + bh - 2)], fill=(*color, 180), outline=NEON_PINK, width=2)
        
        # Text
        ticker = strip_emoji(item['ticker'])
        pct_text = f"{item['change_pct']:.2f}%"
        price_text = f"${item['price']:.2f}"
        
        # Center text in box
        text_y = by + (bh - 60) // 2
        if bh >= 50:
            glow(draw, (bx + 10, text_y), ticker, font_ticker, WHITE, r=2)
            glow(draw, (bx + 10, text_y + 38), pct_text, font_pct, NEON_PINK, r=2)
            draw.text((bx + 10, text_y + 68), price_text, font=font_price, fill=DIM)
    
    # Center divider
    draw.line([(mid_x, content_top), (mid_x, HEIGHT - 60)], fill=(60, 60, 100), width=2)
    
    # Bottom branding bar
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(0, 0, 0, 240))
    draw.line([(0, HEIGHT - 50), (WIDTH, HEIGHT - 50)], fill=NEON_CYAN, width=3)
    
    font_brand = load_bold(26)
    font_sm = load_bold(20)
    glow(draw, (20, HEIGHT - 40), "@AgentJc11443", font_brand, NEON_CYAN, r=2)
    draw.text((260, HEIGHT - 38), "AI-Powered Market Analysis", font=font_sm, fill=DIM)
    
    # CRT scanlines
    for sy in range(0, HEIGHT, 3):
        draw.line([(0, sy), (WIDTH, sy)], fill=(0, 0, 0, 12))
    
    return img


if __name__ == "__main__":
    out_dir = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating NASDAQ heatmap sample...")
    
    # Sample data
    sample_data = {
        'gainers': [
            {'ticker': 'NVDA', 'name': 'NVIDIA Corp', 'change_pct': 8.45, 'price': 892.50},
            {'ticker': 'AMD', 'name': 'Advanced Micro Devices', 'change_pct': 6.23, 'price': 156.78},
            {'ticker': 'TSLA', 'name': 'Tesla Inc', 'change_pct': 5.12, 'price': 234.89},
            {'ticker': 'META', 'name': 'Meta Platforms', 'change_pct': 4.67, 'price': 478.23},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc', 'change_pct': 3.45, 'price': 142.56},
        ],
        'losers': [
            {'ticker': 'NFLX', 'name': 'Netflix Inc', 'change_pct': -4.89, 'price': 567.12},
            {'ticker': 'AAPL', 'name': 'Apple Inc', 'change_pct': -3.56, 'price': 185.45},
            {'ticker': 'MSFT', 'name': 'Microsoft Corp', 'change_pct': -2.34, 'price': 412.34},
            {'ticker': 'AMZN', 'name': 'Amazon.com Inc', 'change_pct': -2.12, 'price': 178.90},
            {'ticker': 'COST', 'name': 'Costco Wholesale', 'change_pct': -1.78, 'price': 723.45},
        ]
    }
    
    img = generate_nasdaq_heatmap(sample_data)
    out_path = os.path.join(out_dir, "nasdaq-heatmap-sample.png")
    img.save(out_path, "PNG")
    print(f"  ✓ Saved: {out_path}")
