"""Create a two-sided 90 x 50 mm card with 3 mm print bleed."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
import pymupdf
from PIL import Image
import argparse
from urllib.parse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument('--website', required=True, help='Confirmed public website URL')
parser.add_argument('--person', choices=['maaz', 'aadil', 'mohammed', 'yahya', 'hamza'], default='maaz')
args = parser.parse_args()
WEBSITE = args.website
NAME, PHONE, DISPLAY_PHONE, FILE_NAME = {
    'maaz': ('Maaz Dawa', '919819157417', '+91 98191 57417', 'Maaz'),
    'hamza': ('Hamza Ghojaria', '919892203101', '+91 98922 03101', 'Hamza'),
    'aadil': ('Aadil Dhukka', '919769554745', '+91 97695 54745', 'Aadil'),
    'mohammed': ('Mohammed Dhukka', '919773233219', '+91 97732 33219', 'Mohammed'),
    'yahya': ('Mohammed Yahya Seliya', '27844523727', '+27 844523727', 'Yahya'),
}[args.person]
EMAIL = 'info@maengineerings.in' if args.person == 'yahya' else 'info@maindustries.in'
TITLE = 'Business Development Manager' if args.person == 'yahya' else ('Managing Director' if args.person == 'mohammed' else 'Director')
if args.person == 'hamza':
    TITLE = 'Business Development Head'
assert urlparse(WEBSITE).scheme in ('https', 'http') and urlparse(WEBSITE).netloc

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output' / 'pdf'
TMP = ROOT / 'tmp' / 'pdfs'
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
W, H = 96 * mm, 56 * mm
GREEN, INK, CREAM = map(HexColor, ['#245c3a', '#262922', '#f5f2e9'])
MUTED, SAGE, SOFT_INK = map(HexColor, ['#52624a', '#e5ede2', '#727168'])
c = canvas.Canvas(str(TMP / 'card-raw.pdf'), pagesize=(W, H))
c.setTitle('M&A Industries | ' + NAME + ' | Visiting Card')
c.setAuthor('M&A Industries')

def text(x, y, value, size=8, font='Helvetica', color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x * mm, y * mm, value)

def centered(x, y, value, size=8, font='Helvetica', color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x * mm, y * mm, value)

def right(x, y, value, size=8, font='Helvetica', color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawRightString(x * mm, y * mm, value)

def qr_code(x, y, address, size=25):
    widget = qr.QrCodeWidget(address)
    x0, y0, x1, y1 = widget.getBounds()
    side = size * mm
    drawing = Drawing(side, side, transform=[side/(x1-x0),0,0,side/(y1-y0),0,0])
    drawing.add(widget)
    c.setFillColor(white)
    c.rect(x*mm, y*mm, side, side, fill=1, stroke=0)
    renderPDF.draw(drawing, c, x*mm, y*mm)
    c.linkURL(address, (x*mm, y*mm, (x+size)*mm, (y+size)*mm))

# Front: align the brand, contact details and product ranges with the website.
c.setFillColor(CREAM)
c.rect(0, 0, W, H, fill=1, stroke=0)
text(8, 47, DISPLAY_PHONE, 8, 'Helvetica-Bold')
text(8, 42.5, EMAIL, 7.3, color=SOFT_INK)
right(88, 47, NAME, 8.5 if args.person == 'yahya' else 10, 'Helvetica-Bold')
right(88, 42.5, TITLE, 7.0 if args.person == 'yahya' else 7.5, color=MUTED)
# A white panel preserves the supplied logo's original background.
c.setFillColor(white)
c.roundRect(8*mm, 24*mm, 80*mm, 15*mm, 2*mm, fill=1, stroke=0)
c.drawImage(str(ROOT / 'assets/images/brand-logo.png'), 12*mm, 25.5*mm,
            width=72*mm, height=13.05*mm, mask='auto')
centered(48, 20.5, 'Thoughtful materials. Everyday possibilities.', 8.2, 'Times-Italic', GREEN)

# Small, consistent product photographs introduce all three current ranges.
samples = [
    ('assets/images/products/sugarcane-bowls-pack.png', 'SUGARCANE'),
    ('assets/images/products/recycled-storage-boxes-photo.webp', 'RECYCLED'),
    ('assets/images/products/clean-republic-pine-floor-cleaner.png', 'CLEANING & HYGIENE')
]
sample_x = [15, 41.5, 68]
for (image, label), x in zip(samples, sample_x):
    c.setFillColor(white)
    c.roundRect((x-1)*mm, 5.2*mm, 16*mm, 11.4*mm, 1*mm, fill=1, stroke=0)
    c.drawImage(str(ROOT / image), x*mm, 6*mm, width=14*mm, height=9.8*mm,
                preserveAspectRatio=True, anchor='c', mask='auto')
    centered(x+7, 3.8, label, 4.7 if label != 'CLEANING & HYGIENE' else 4.1,
             'Helvetica-Bold', SOFT_INK)
c.linkURL('https://wa.me/' + PHONE, (8*mm,44*mm,42*mm,49*mm))
c.linkURL('mailto:' + EMAIL, (8*mm,40*mm,43*mm,44*mm))
c.showPage()

# Back: two equally sized codes with their quiet zones intact.
c.setFillColor(CREAM)
c.rect(0, 0, W, H, fill=1, stroke=0)
# A soft sage website side keeps the two-code layout quietly differentiated.
c.setFillColor(SAGE)
c.rect(48*mm, 0, 48*mm, H, fill=1, stroke=0)
centered(26, 44, 'WHATSAPP', 8, 'Helvetica-Bold', MUTED)
centered(70, 44, 'WEBSITE', 8, 'Helvetica-Bold', MUTED)
c.setStrokeColor(HexColor('#cdd9c7'))
c.setLineWidth(.65)
c.line(48*mm, 10*mm, 48*mm, 46*mm)
qr_code(13.5, 15, 'https://wa.me/' + PHONE)
qr_code(57.5, 15, WEBSITE)
centered(26, 10, 'Scan to chat', 7)
centered(70, 10, 'Explore M&A Industries', 7)
c.save()

# Explicit trim boxes let the printer distinguish artwork from bleed.
reader, writer = PdfReader(TMP / 'card-raw.pdf'), PdfWriter()
for page in reader.pages:
    page.trimbox = RectangleObject([3*mm, 3*mm, 93*mm, 53*mm])
    page.bleedbox = RectangleObject([0, 0, W, H])
    writer.add_page(page)
final = OUT / f'MA-Industries-{FILE_NAME}-Visiting-Card.pdf'
with final.open('wb') as stream:
    writer.write(stream)

doc = pymupdf.open(final)
previews = []
for index, page in enumerate(doc):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4), alpha=False)
    path = TMP / f'card-{index+1}.png'
    pix.save(path)
    previews.append(Image.open(path).copy())
preview = Image.new('RGB', (previews[0].width, sum(p.height for p in previews)+24), '#dddddd')
preview.paste(previews[0], (0, 0))
preview.paste(previews[1], (0, previews[0].height+24))
preview.save(OUT / f'MA-Industries-{FILE_NAME}-Visiting-Card-Preview.png')
assert len(doc) == 2
assert NAME in doc[0].get_text()
assert DISPLAY_PHONE in doc[0].get_text()
assert 'Scan to chat' in doc[1].get_text()
assert any(link.get('uri') == 'https://wa.me/' + PHONE for link in doc[1].get_links())
print(final)
