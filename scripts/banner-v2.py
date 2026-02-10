#!/usr/bin/env python3
"""Generate X banner v2: shrink current content + add neon green futuristic tech background."""
from PIL import Image, ImageDraw, ImageFilter
import random, math

W, H = 1500, 500
random.seed(42)

# Create base black canvas
img = Image.new('RGB', (W, H), (0, 0, 0))
draw = ImageDraw.Draw(img)

GREEN = (74, 222, 128)
DIM_GREEN = (20, 60, 35)
MID_GREEN = (35, 110, 60)
BRIGHT = (100, 255, 150)

# --- Background layer 1: Grid ---
for x in range(0, W, 40):
    opacity = random.randint(15, 40)
    c = (0, opacity, int(opacity * 0.6))
    draw.line([(x, 0), (x, H)], fill=c, width=1)
for y in range(0, H, 40):
    opacity = random.randint(15, 40)
    c = (0, opacity, int(opacity * 0.6))
    draw.line([(0, y), (W, y)], fill=c, width=1)

# --- Background layer 2: Circuit traces ---
def draw_circuit(draw, start_x, start_y, length=8):
    x, y = start_x, start_y
    for _ in range(length):
        direction = random.choice(['h', 'v'])
        dist = random.randint(20, 80)
        if direction == 'h':
            nx = x + random.choice([-1, 1]) * dist
            nx = max(0, min(W, nx))
            draw.line([(x, y), (nx, y)], fill=DIM_GREEN, width=1)
            x = nx
        else:
            ny = y + random.choice([-1, 1]) * dist
            ny = max(0, min(H, ny))
            draw.line([(x, y), (x, ny)], fill=DIM_GREEN, width=1)
            y = ny
        # Node dot at junction
        draw.ellipse([x-2, y-2, x+2, y+2], fill=MID_GREEN)

for _ in range(40):
    draw_circuit(draw, random.randint(0, W), random.randint(0, H), random.randint(5, 12))

# --- Background layer 3: Hexagons ---
def draw_hexagon(draw, cx, cy, r, color, width=1):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, outline=color, fill=None)

for _ in range(25):
    hx = random.randint(0, W)
    hy = random.randint(0, H)
    hr = random.randint(15, 50)
    draw_hexagon(draw, hx, hy, hr, DIM_GREEN)

# --- Background layer 4: Glowing particles ---
particle_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pdraw = ImageDraw.Draw(particle_layer)
for _ in range(100):
    px = random.randint(0, W)
    py = random.randint(0, H)
    pr = random.randint(1, 3)
    brightness = random.randint(100, 255)
    pdraw.ellipse([px-pr, py-pr, px+pr, py+pr], fill=(50, brightness, 80, brightness))

particle_blurred = particle_layer.filter(ImageFilter.GaussianBlur(2))
img.paste(Image.alpha_composite(Image.new('RGBA', (W, H), (0,0,0,255)), particle_blurred).convert('RGB'), (0, 0))

# Re-draw circuits and hex on top (they got covered by particle paste)
draw = ImageDraw.Draw(img)
for x in range(0, W, 40):
    opacity = random.randint(10, 30)
    draw.line([(x, 0), (x, H)], fill=(0, opacity, int(opacity*0.5)), width=1)
for y in range(0, H, 40):
    opacity = random.randint(10, 30)
    draw.line([(0, y), (W, y)], fill=(0, opacity, int(opacity*0.5)), width=1)

for _ in range(30):
    draw_circuit(draw, random.randint(0, W), random.randint(0, H), random.randint(5, 10))

for _ in range(20):
    hx = random.randint(0, W)
    hy = random.randint(0, H)
    hr = random.randint(15, 45)
    draw_hexagon(draw, hx, hy, hr, (25, 80, 45))

# --- Background layer 5: Horizontal data streams ---
for _ in range(15):
    sy = random.randint(0, H)
    sx = random.randint(0, W - 200)
    length = random.randint(80, 300)
    alpha = random.randint(30, 70)
    draw.line([(sx, sy), (sx + length, sy)], fill=(0, alpha, int(alpha*0.6)), width=1)

# --- Background layer 6: Scan line effect (subtle) ---
for y in range(0, H, 3):
    draw.line([(0, y), (W, y)], fill=(0, 0, 0), width=1)

# --- Center glow ---
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for r in range(200, 0, -2):
    alpha = int(15 * (1 - r/200))
    gdraw.ellipse([W//2 - r, H//2 - r, W//2 + r, H//2 + r], fill=(40, 180, 90, alpha))
glow_blurred = glow.filter(ImageFilter.GaussianBlur(30))
# Composite glow
base_rgba = img.convert('RGBA')
result = Image.alpha_composite(base_rgba, glow_blurred)
img = result.convert('RGB')

# --- Overlay the original banner content, shrunk ~85% ---
original = Image.open('/Users/jc_agent/.openclaw/workspace/dashboard/x-banner.png')
scale = 0.82
new_w = int(W * scale)
new_h = int(H * scale)
shrunk = original.resize((new_w, new_h), Image.LANCZOS)

# Center it
offset_x = (W - new_w) // 2
offset_y = (H - new_h) // 2

# Need to blend — extract non-black pixels from shrunk and overlay
shrunk_rgba = shrunk.convert('RGBA')
pixels = shrunk_rgba.load()
for x in range(new_w):
    for y in range(new_h):
        r, g, b, a = pixels[x, y]
        # Make very dark pixels transparent so background shows through
        brightness = r + g + b
        if brightness < 30:
            pixels[x, y] = (r, g, b, 0)
        elif brightness < 60:
            pixels[x, y] = (r, g, b, int(255 * brightness / 60))

img_rgba = img.convert('RGBA')
img_rgba.paste(shrunk_rgba, (offset_x, offset_y), shrunk_rgba)
final = img_rgba.convert('RGB')

# Save
out_path = '/Users/jc_agent/.openclaw/workspace/dashboard/x-banner-v2.png'
desktop_path = '/Users/jc_agent/Desktop/x-banner-v2.png'
final.save(out_path, 'PNG')
final.save(desktop_path, 'PNG')
print(f"Saved to {out_path} and {desktop_path}")
