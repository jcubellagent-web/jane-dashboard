#!/usr/bin/env python3
"""
Substack Newsletter Header Generator
Editorial/Newsletter style - Bloomberg Terminal meets modern newsletter
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def generate_substack_header(title, subtitle, date_str, key_stats=None, sections=None, output_path=None):
    """
    Generate a professional editorial-style newsletter header.
    
    Args:
        title: Main title (e.g., "AI Daily Brief")
        subtitle: Subtitle with main stories
        date_str: Date string (e.g., "Friday, February 13, 2026")
        key_stats: List of key stats to display at bottom
        sections: List of section names for the glossary/TOC (e.g., ["AI Providers", "VC/PE/M&A", ...])
        output_path: Where to save the image
    
    Returns:
        Path to saved image
    """
    # Dimensions - standard OG/email format
    WIDTH = 1200
    HEIGHT = 630
    
    # Color palette - editorial/professional
    BG_COLOR = (10, 10, 10)  # #0a0a0a - deep dark
    TEXT_PRIMARY = (255, 255, 255)  # White
    TEXT_SECONDARY = (180, 180, 180)  # Light gray
    ACCENT_CYAN = (100, 200, 220)  # Muted cyan
    ACCENT_GOLD = (200, 170, 100)  # Muted gold
    ACCENT_LINE = (60, 60, 60)  # Subtle gray
    
    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to load system fonts, fallback to default
    try:
        # Title font - bold and large
        font_title = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 72)
        # Subtitle font - medium
        font_subtitle = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 32)
        # Date font - smaller
        font_date = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
        # Stats font - clean
        font_stats = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
        # Branding font - small
        font_brand = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    except:
        # Fallback to default
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_stats = ImageFont.load_default()
        font_brand = ImageFont.load_default()
    
    # Top accent bar - thin gradient-like effect
    gradient_height = 4
    draw.rectangle([0, 0, WIDTH, gradient_height], fill=ACCENT_CYAN)
    
    # Margins and positioning
    margin_x = 60
    margin_top = 80
    
    # Date at top (small, subtle)
    draw.text((margin_x, margin_top), date_str, fill=TEXT_SECONDARY, font=font_date)
    
    # Title (main headline)
    title_y = margin_top + 60
    draw.text((margin_x, title_y), title, fill=TEXT_PRIMARY, font=font_title)
    
    # Thin accent line below title
    line_y = title_y + 90
    draw.rectangle([margin_x, line_y, WIDTH - margin_x, line_y + 2], fill=ACCENT_GOLD)
    
    # Subtitle (main stories) - word wrap
    subtitle_y = line_y + 30
    max_subtitle_width = WIDTH - (margin_x * 2)
    
    # Simple word wrapping for subtitle
    words = subtitle.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_subtitle)
        if bbox[2] - bbox[0] <= max_subtitle_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw subtitle lines
    for i, line in enumerate(lines[:3]):  # Max 3 lines
        draw.text((margin_x, subtitle_y + (i * 42)), line, fill=TEXT_SECONDARY, font=font_subtitle)
    
    # Sections glossary/TOC (between subtitle and stats)
    if sections:
        sections_y = subtitle_y + (len(lines[:3]) * 42) + 30
        # Draw a thin line above sections
        draw.rectangle([margin_x, sections_y, WIDTH - margin_x, sections_y + 1], fill=ACCENT_LINE)
        sections_y += 18
        
        # "INSIDE THIS ISSUE" label
        try:
            font_section_label = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
            font_section_item = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
        except:
            font_section_label = ImageFont.load_default()
            font_section_item = ImageFont.load_default()
        
        draw.text((margin_x, sections_y), "INSIDE THIS ISSUE", fill=(100, 100, 100), font=font_section_label)
        sections_y += 28
        
        # Draw sections in a flowing row with dot separators
        section_icons = {
            'AI Providers': '\u2022',
            'Venture, PE & M&A': '\u2022',
            'Enterprise SaaS': '\u2022',
            'NASDAQ 100': '\u2022',
            'Crypto Movers': '\u2022',
            'Hot Take': '\u2022',
        }
        
        x_cursor = margin_x
        for i, sec in enumerate(sections):
            color = ACCENT_CYAN if i % 2 == 0 else ACCENT_GOLD
            if i > 0:
                # Dot separator
                draw.text((x_cursor, sections_y), "  \u00b7  ", fill=(80, 80, 80), font=font_section_item)
                bbox = draw.textbbox((0, 0), "  \u00b7  ", font=font_section_item)
                x_cursor += bbox[2] - bbox[0]
            draw.text((x_cursor, sections_y), sec, fill=color, font=font_section_item)
            bbox = draw.textbbox((0, 0), sec, font=font_section_item)
            x_cursor += bbox[2] - bbox[0]
            
            # Wrap to next line if needed
            if x_cursor > WIDTH - margin_x - 100 and i < len(sections) - 1:
                x_cursor = margin_x
                sections_y += 28

    # Key stats at bottom (clean row)
    if key_stats:
        stats_y = HEIGHT - 80
        
        # Background bar for stats
        draw.rectangle([0, stats_y - 15, WIDTH, HEIGHT], fill=(15, 15, 15))
        
        # Calculate spacing for stats
        stat_spacing = (WIDTH - (margin_x * 2)) / len(key_stats)
        
        for i, stat in enumerate(key_stats):
            stat_x = margin_x + (i * stat_spacing)
            
            # Alternate accent colors for visual interest
            stat_color = ACCENT_CYAN if i % 2 == 0 else ACCENT_GOLD
            
            # Draw stat
            draw.text((stat_x, stats_y), stat, fill=stat_color, font=font_stats)
    
    # Branding (small, bottom right)
    brand_text = "@AgentJc11443"
    brand_x = WIDTH - margin_x - 150
    brand_y = HEIGHT - 35
    draw.text((brand_x, brand_y), brand_text, fill=(80, 80, 80), font=font_brand)
    
    # Save image
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, 'PNG', quality=95)
        return output_path
    else:
        return img

if __name__ == "__main__":
    # Test generation
    generate_substack_header(
        title="AI Daily Brief",
        subtitle="Anthropic's $30B Mega-Round, CPI Relief Rally & SaaS Rebound",
        date_str="Friday, February 13, 2026",
        key_stats=["Anthropic: $380B val", "CPI: 2.4%", "NASDAQ: +0.76%", "BTC: $69K"],
        output_path="/Users/jc_agent/.openclaw/workspace/tiktok/x-headers/substack-header-today.png"
    )
    print("✓ Header generated successfully")
