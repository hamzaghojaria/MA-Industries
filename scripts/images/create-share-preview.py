"""Compose a 1200 x 630 sharing image from the current product photographs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SIZE = (1200, 630)
INK = '#183b2b'
MUTED = '#566052'
CREAM = '#f8f6ef'
SAGE = '#e5ede2'


def load_font(size, serif=False, bold=False):
    names = (['georgiab.ttf', 'Georgia Bold.ttf'] if bold else ['georgia.ttf', 'Georgia.ttf']) if serif else (
        ['arialbd.ttf', 'Arial Bold.ttf'] if bold else ['arial.ttf', 'Arial.ttf'])
    roots = [Path('C:/Windows/Fonts'), Path('/usr/share/fonts/truetype/msttcorefonts'),
             Path('/usr/share/fonts/truetype/liberation2')]
    for root in roots:
        for name in names:
            candidate = root / name
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def add_photo_card(canvas, path, position, side):
    x, y = position
    pad = 8
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x - pad + 3, y - pad + 5, x + side + pad + 3, y + side + pad + 5),
                                  radius=20, fill='#17271a30')
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))
    card = Image.new('RGBA', (side + 2 * pad, side + 2 * pad), '#fffdf8')
    photo = Image.open(path).convert('RGB')
    photo = ImageOps.fit(photo, (side, side), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new('L', (side, side), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, side - 1, side - 1), radius=14, fill=255)
    card.paste(photo, (pad, pad), mask)
    ImageDraw.Draw(card).rounded_rectangle((pad, pad, pad + side - 1, pad + side - 1),
                                           radius=14, outline='#d8dfd4', width=1)
    canvas.alpha_composite(card, (x - pad, y - pad))


def main():
    canvas = Image.new('RGBA', SIZE, CREAM)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((574, 34, 1173, 596), radius=34, fill=SAGE)

    logo = Image.open(ROOT / 'assets/images/brand-logo.png').convert('RGBA')
    logo.thumbnail((404, 74), Image.Resampling.LANCZOS)
    draw.rounded_rectangle((60, 54, 496, 145), radius=12, fill='white')
    canvas.alpha_composite(logo, (68, 62))

    heading = load_font(58, serif=True)
    draw.text((64, 190), 'For the work', fill=INK, font=heading)
    draw.text((64, 253), 'of every day.', fill=INK, font=heading)
    draw.text((67, 355), 'Thoughtful materials.', fill=INK, font=load_font(23))
    draw.text((67, 386), 'Everyday possibilities.', fill=INK, font=load_font(23))
    draw.rounded_rectangle((67, 438, 448, 440), radius=1, fill='#9bb093')
    draw.text((67, 462), 'SUGARCANE  ·  RECYCLED', fill=MUTED, font=load_font(15, bold=True))
    draw.text((67, 486), 'CLEANING & HYGIENE', fill=MUTED, font=load_font(15, bold=True))
    draw.text((67, 526), 'Product and bulk supply from Mumbai.', fill=MUTED, font=load_font(16))
    draw.text((67, 565), 'maindustries.in', fill=INK, font=load_font(18, bold=True))

    photos = [
        ('assets/images/products/sugarcane-bowls-pack.png', (602, 54)),
        ('assets/images/products/clean-republic-pine-floor-cleaner.png', (885, 54)),
        ('assets/images/products/recycled-storage-boxes-photo.webp', (602, 336)),
        ('assets/images/products/clean-republic-handwash.png', (885, 336))
    ]
    for image, position in photos:
        add_photo_card(canvas, ROOT / image, position, 246)

    output = ROOT / 'assets/images/share-preview.jpg'
    canvas.convert('RGB').save(output, 'JPEG', quality=91, optimize=True, progressive=True)
    with Image.open(output) as saved:
        if saved.size != SIZE:
            raise ValueError(f'Unexpected sharing image dimensions: {saved.size}')
    print(f'Created {output.relative_to(ROOT).as_posix()} ({SIZE[0]} x {SIZE[1]}).')


if __name__ == '__main__':
    main()
