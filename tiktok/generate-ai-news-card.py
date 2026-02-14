#!/usr/bin/env python3
"""Generate AI news card for X thread.
News ticker/card stack style with categorized headlines.
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

CATEGORY_COLORS = {
    'launch': NEON_CYAN,
    'funding': NEON_GOLD,
    'partnership': NEON_GREEN,
    'research': NEON_PURPLE,
    'policy': NEON_ORANGE,
}

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

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    line = ""
    
    for word in words:
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            if line:
                lines.append(line)
                line = word
            else:
                lines.append(word)
                line = ""
        else:
            line = test
    
    if line:
        lines.append(line)
    
    return lines

def generate_ai_news_card(headlines):
    """Generate AI news card with categorized headlines.
    
    Args:
        headlines: list of dicts with 'company', 'headline', 'category'
                  category is one of: launch, funding, partnership, research, policy
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
    
    title_text = "AI PROVIDER HIGHLIGHTS"
    date_text = datetime.now().strftime("%a %b %d, %Y")
    
    glow(draw, (30, 20), title_text, font_title, NEON_PURPLE, r=3)
    draw.text((30, 72), date_text, font=font_date, fill=DIM)
    
    # Content area
    content_top = 110
    content_height = HEIGHT - content_top - 60
    
    # Limit to 6 headlines
    headlines = headlines[:6]
    
    # Card height and spacing
    card_height = (content_height - 20) // len(headlines) if headlines else 80
    card_height = min(card_height, 90)  # Cap max height
    spacing = 5
    
    font_company = load_bold(22)
    font_headline = load_bold(17)
    font_category = load_bold(13)
    
    y_offset = content_top
    
    for idx, item in enumerate(headlines):
        company = strip_emoji(item.get('company', 'Unknown'))
        headline = strip_emoji(item.get('headline', ''))
        category = item.get('category', 'launch').lower()
        
        # Get category color
        cat_color = CATEGORY_COLORS.get(category, NEON_CYAN)
        
        # Card background with gradient
        card_y = y_offset
        for i in range(card_height):
            alpha = int(150 - (i / card_height) * 50)
            draw.line([(20, card_y + i), (WIDTH - 20, card_y + i)], fill=(*cat_color, max(20, alpha // 3)))
        
        # Card border
        draw.rectangle([(20, card_y), (WIDTH - 20, card_y + card_height)], 
                      fill=None, outline=cat_color, width=2)
        
        # Category badge (top-left)
        badge_w = 100
        badge_h = 22
        draw.rectangle([(25, card_y + 5), (25 + badge_w, card_y + 5 + badge_h)], 
                      fill=cat_color)
        draw.text((30, card_y + 8), category.upper(), font=font_category, fill=BG_DARK)
        
        # Company name (next to badge)
        company_x = 25 + badge_w + 15
        glow(draw, (company_x, card_y + 6), company, font_company, WHITE, r=2)
        
        # Headline text (wrapped, below company)
        headline_y = card_y + 32
        headline_max_width = WIDTH - 60
        
        wrapped_lines = wrap_text(headline, font_headline, headline_max_width, draw)
        for line_idx, line in enumerate(wrapped_lines[:2]):  # Max 2 lines
            draw.text((30, headline_y + line_idx * 18), line, font=font_headline, fill=DIM)
        
        # Separator line (except last item)
        if idx < len(headlines) - 1:
            draw.line([(30, card_y + card_height + spacing // 2), 
                      (WIDTH - 30, card_y + card_height + spacing // 2)], 
                     fill=(40, 40, 60, 100))
        
        y_offset += card_height + spacing
    
    # Bottom branding bar
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(0, 0, 0, 240))
    draw.line([(0, HEIGHT - 50), (WIDTH, HEIGHT - 50)], fill=NEON_CYAN, width=3)
    
    font_brand = load_bold(26)
    font_sm = load_bold(20)
    glow(draw, (20, HEIGHT - 40), "@AgentJc11443", font_brand, NEON_CYAN, r=2)
    draw.text((260, HEIGHT - 38), "AI Industry Intel", font=font_sm, fill=DIM)
    
    # CRT scanlines
    for sy in range(0, HEIGHT, 3):
        draw.line([(0, sy), (WIDTH, sy)], fill=(0, 0, 0, 12))
    
    return img


if __name__ == "__main__":
    out_dir = os.path.join(WORKSPACE, "tiktok", "x-headers")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating AI news card sample...")
    
    # Sample data
    sample_headlines = [
        {
            'company': 'Anthropic',
            'headline': 'Claude 4.5 Sonnet achieves new benchmarks in coding and analysis tasks',
            'category': 'launch'
        },
        {
            'company': 'OpenAI',
            'headline': 'Raises $6.5B Series C at $150B valuation, led by Thrive Capital',
            'category': 'funding'
        },
        {
            'company': 'xAI',
            'headline': 'Partners with Oracle for massive GPU cluster expansion',
            'category': 'partnership'
        },
        {
            'company': 'DeepMind',
            'headline': 'Publishes breakthrough research on protein folding accuracy',
            'category': 'research'
        },
        {
            'company': 'Meta',
            'headline': 'Announces Llama 4 with improved reasoning capabilities',
            'category': 'launch'
        },
        {
            'company': 'Google',
            'headline': 'EU proposes new AI governance framework for foundation models',
            'category': 'policy'
        },
    ]
    
    img = generate_ai_news_card(sample_headlines)
    out_path = os.path.join(out_dir, "ai-news-card-sample.png")
    img.save(out_path, "PNG")
    print(f"  ✓ Saved: {out_path}")
