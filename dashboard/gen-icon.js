// Generate Jane PWA icon using node-canvas or pure PNG
// Since we may not have canvas, let's use the built-in approach with sharp or fallback

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Use Python with Pillow which is more likely available
const pyScript = `
import sys
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("NO_PILLOW")
    sys.exit(1)

size = int(sys.argv[1])
out = sys.argv[2]

img = Image.new('RGBA', (size, size), (0,0,0,0))
draw = ImageDraw.Draw(img)

# Rounded rectangle background - matte black
def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+2*radius, y0+2*radius], 180, 270, fill=fill)
    draw.pieslice([x1-2*radius, y0, x1, y0+2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1-2*radius, x0+2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1-2*radius, y1-2*radius, x1, y1], 0, 90, fill=fill)

radius = int(size * 0.21)
rounded_rect(draw, (0, 0, size-1, size-1), radius, (14, 14, 18, 255))

# Try to find a good font
font = None
font_size = int(size * 0.62)
font_paths = [
    '/System/Library/Fonts/SFPro-Bold.otf',
    '/System/Library/Fonts/Supplemental/SF-Pro-Display-Bold.otf',
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/SFCompact.ttf',
    '/Library/Fonts/SF-Pro-Display-Bold.otf',
]

# Also try system san francisco
import glob
sf_fonts = glob.glob('/System/Library/Fonts/SF*.ttf') + glob.glob('/System/Library/Fonts/SF*.otf') + glob.glob('/System/Library/Fonts/SFUI*.otf')
font_paths = sf_fonts + font_paths

for fp in font_paths:
    try:
        font = ImageFont.truetype(fp, font_size)
        break
    except:
        continue

if not font:
    font = ImageFont.load_default()

# Draw the J in green
text = "J"
green = (74, 222, 128)  # #4ade80

# Center it
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
x = (size - tw) // 2 - bbox[0]
y = (size - th) // 2 - bbox[1] - int(size * 0.02)

# Subtle glow layer
glow_img = Image.new('RGBA', (size, size), (0,0,0,0))
glow_draw = ImageDraw.Draw(glow_img)
glow_draw.text((x, y), text, font=font, fill=(74, 222, 128, 60))
glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=int(size*0.03)))
img = Image.alpha_composite(img, glow_img)

# Main letter
draw2 = ImageDraw.Draw(img)
draw2.text((x, y), text, font=font, fill=green)

# Small accent dot
dot_r = int(size * 0.022)
dot_x = int(size * 0.66)
dot_y = int(size * 0.77)
draw2.ellipse([dot_x-dot_r, dot_y-dot_r, dot_x+dot_r, dot_y+dot_r], fill=(74, 222, 128, 150))

img.save(out)
print(f"OK {out}")
`;

fs.writeFileSync('/tmp/gen_jane_icon.py', pyScript);

for (const s of [192, 512, 1024]) {
    const out = path.join(__dirname, `icon-${s}.png`);
    try {
        const r = execSync(`python3 /tmp/gen_jane_icon.py ${s} "${out}"`, { encoding: 'utf8' });
        console.log(r.trim());
    } catch(e) {
        console.error(`Failed ${s}: ${e.message}`);
    }
}
