"""Create a focused PDF and a portable animated browser catalogue."""
import html
import json
import shutil
from io import BytesIO
from pathlib import Path
from browser_catalogue import create_browser_catalogue
from catalogue_images import image_bytes
from urllib.parse import quote

import pymupdf
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf'
TMP = ROOT / 'tmp/pdfs'
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
data = json.loads((TMP / 'catalogue-data.json').read_text(encoding='utf-8'))
groups = [g for g in data['categories'] if g.get('collection') == 'sugarcane-recycled']
products = [p for g in groups for p in data['papers'] if p['group'] == g['id']]
assert products and len(groups) == 4
W, H = 595.276, 841.89
INK, GREEN, RED, MUTED = '#262922', '#a70027', '#a70027', '#727168'
DEST = OUT / 'MA-Industries-Catalogue.pdf'
c = canvas.Canvas(str(DEST), pagesize=(W,H), pageCompression=1)
c.setTitle('M&A Industries | Sugarcane & Recycled Collection')
c.setAuthor('M&A Industries')
font_path = next((p for p in [Path('C:/Windows/Fonts/arial.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists()), Path(reportlab.__file__).parent/'fonts/Vera.ttf')
pdfmetrics.registerFont(TTFont('Specifications', str(font_path)))

def specifications(product):
    return [f"{s['label']}: {s['value']}" if isinstance(s,dict) else s for s in product.get('specifications',[])]

def text(x,y,s,size=10,color=INK,font='Helvetica'):
    c.setFillColor(HexColor(color)); c.setFont(font,size); c.drawString(x,y,s)

def para(x,y,s,w,size=12,leading=18,color=INK,font='Helvetica'):
    p=Paragraph(html.escape(s),ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,h=p.wrap(w,1000); p.drawOn(c,x,y-h); return h

def rect(x,y,w,h,color):
    c.setFillColor(HexColor(color)); c.rect(x,y,w,h,fill=1,stroke=0)

def photo(p,x,y,w,h):
    image=ImageReader(BytesIO(image_bytes(ROOT / p['image']))); iw,ih=image.getSize(); scale=min(w/iw,h/ih)
    c.drawImage(image,x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale,mask='auto')

def base(n,label):
    rect(0,0,W,H,'#fff5f3')
    c.drawImage(str(ROOT/'assets/images/brand-logo.png'),40,792,width=174,height=31.5,mask='auto')
    text(40,777,label.upper(),8,GREEN)
    rect(40,48,W-80,.6,'#dbaba7')
    text(40,30,'SUGARCANE / RECYCLED COLLECTION',7,MUTED)
    text(525,30,f'{n:02}',8,MUTED)

def enquiry(p):
    return 'https://wa.me/919819157417?text='+quote('Hello M&A Industries, I would like to enquire about '+p['name']+'. Please share specifications, pack sizes, pricing and availability.')

base(1,'The considered collection')
text(40,704,'Everyday objects.',44,font='Times-Roman')
text(40,652,'A thoughtful direction.',40,GREEN,'Times-Italic')
para(40,610,'Sugarcane-based materials and recycled essentials for foodservice, retail and the everyday home.',460,14,21,MUTED)
rect(40,257,515,300,'#ffffff')
photo(products[1],40,257,515,300)
text(40,214,'Thoughtful materials. Everyday possibilities.',19,GREEN,'Times-Italic')
text(40,158,'+91 98191 57417',13,font='Helvetica-Bold')
text(40,135,'info@maindustries.in  /  maindustries.in',10,MUTED)
c.linkURL('https://maindustries.in/',(40,125,410,150))
c.showPage()

base(2,'Collection directory')
text(40,708,'Find your everyday.',37,font='Times-Roman')
para(40,672,'Four focused ranges. One product per page. Select a collection to explore.',480,13,20,MUTED)
for i,g in enumerate(groups):
    y=548-i*107
    text(40,y,f'0{i+1}',29,GREEN,'Times-Italic')
    text(102,y+9,g['name'],18,font='Helvetica-Bold')
    count=sum(p['group']==g['id'] for p in products)
    para(102,y-6,g['line'],390,11,17,MUTED)
    text(102,y-43,f'{count} PRODUCTS  /  VIEW COLLECTION >',8,GREEN,'Helvetica-Bold')
    c.linkRect('',g['id'],(40,y-52,555,y+35),thickness=0)
para(40,152,'Material composition, bio-based or recycled content, dimensions and availability are confirmed for the selected item. Request supporting documentation for your application.',480,10,15,MUTED)
c.showPage()

for i,p in enumerate(products):
    g=next(g for g in groups if g['id']==p['group'])
    base(i+3,g['name'])
    c.bookmarkPage(p['id'])
    if i==0 or products[i-1]['group']!=p['group']:
        c.bookmarkPage(g['id']); c.addOutlineEntry(g['name'],g['id'],0)
    c.addOutlineEntry(p['name'],p['id'],1)
    text(40,737,f'{i+1:02} / {len(products):02}',9,GREEN,'Helvetica-Bold')
    para(40,719,p['name'],490,31,35,INK,'Times-Roman')
    rect(40,385,515,240,'#ffffff')
    photo(p,57,397,481,216)
    text(40,366,'THE MATERIAL',8,GREEN,'Helvetica-Bold')
    para(40,351,p.get('material','Specifications confirmed on enquiry'),500,10,14,MUTED)
    para(40,310,p['desc'],490,11.5,17)
    text(40,260,'DIMENSIONS & SPECIFICATIONS',8,GREEN,'Helvetica-Bold')
    y=244
    for spec in specifications(p) or ['Sizes and pack quantities confirmed on enquiry.']:
        y-=para(40,y,spec,330,9.5,14,MUTED,'Specifications')+5
    assert y>=114,(p['id'],'Specification content overlaps enquiry area',y)
    text(400,260,'SUITED TO',8,GREEN,'Helvetica-Bold')
    uses_height=para(400,244,' / '.join(p['uses']),155,9,13,MUTED)
    assert 244-uses_height>=114,(p['id'],'Uses overflow')
    rect(40,70,230,36,RED)
    text(55,83,'ENQUIRE ABOUT THIS PRODUCT  >',9,'#ffffff','Helvetica-Bold')
    c.linkURL(enquiry(p),(40,70,270,106))
    text(298,84,'Confirm options & availability',8,MUTED)
    c.showPage()

base(len(products)+3,'Start a conversation')
text(40,704,'Your next requirement.',39,font='Times-Roman')
text(40,650,'Our next conversation.',39,GREEN,'Times-Italic')
para(40,585,'Tell us what you are sourcing. We will help you explore the appropriate product, material and pack format.',475,17,25)
for y,num,title,copy in [(477,'01','Choose your product','Share the product name or a reference image.'),(382,'02','Define your requirement','Include quantity, dimensions and delivery location.'),(287,'03','Confirm the details','Discuss material content, item documentation and availability.')]:
    text(40,y,num,27,GREEN,'Times-Italic'); text(102,y+4,title,17,font='Helvetica-Bold'); para(102,y-12,copy,425,12,18,MUTED)
rect(40,114,515,72,RED)
text(58,154,'+91 98191 57417',20,'#ffffff','Helvetica-Bold')
text(58,131,'info@maindustries.in  /  maindustries.in',11,'#ffffff')
c.linkURL('https://wa.me/919819157417',(40,114,555,186))
c.showPage(); c.save()

doc=pymupdf.open(DEST)
assert len(doc)==len(products)+3
assert 'THE COLLECTION' not in doc[0].get_text()
assert 'Each with its' not in doc[0].get_text()
logo_size=Image.open(ROOT/'assets/images/brand-logo.png').size
for page in doc:
    assert any(tuple(image[2:4])==logo_size for image in page.get_images()), 'Missing brand logo'
for i,p in enumerate(products):
    page=doc[i+2]
    assert p['name'] in page.get_text().replace('\n',' ')
    assert any(link.get('uri')==enquiry(p) for link in page.get_links())
    normalized=' '.join(page.get_text().split())
    for spec in specifications(p):
        assert ' '.join(spec.split()) in normalized,(p['id'],'Missing specification',spec)
for i,page in enumerate(doc):
    for b in page.get_text('blocks'):
        assert b[0]>=0 and b[1]>=0 and b[2]<=W+1 and b[3]<=H+1,(i,b)
    page.get_pixmap(matrix=pymupdf.Matrix(.9,.9),alpha=False).save(TMP/f'focused-{i+1:02}.png')
for folder in [ROOT/'assets/catalogues',ROOT/'dist/assets/catalogues']:
    folder.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(DEST,folder/'MA-Industries-Paper-Catalogue.pdf')

sheet=Image.new('RGB',(6*220,6*330),'#eddcdd')
draw=ImageDraw.Draw(sheet)
for i in range(len(doc)):
    with Image.open(TMP/f'focused-{i+1:02}.png') as preview:
        preview.thumbnail((210,302))
        x=(i%6)*220+5; y=(i//6)*330+5
        sheet.paste(preview,(x,y)); draw.text((x,y+305),f'Page {i+1}',fill=INK)
sheet.save(OUT/'MA-Industries-Catalogue-Overview.png')

browser=OUT/'MA-Industries-Interactive-Catalogue.html'
create_browser_catalogue(ROOT,browser,products,groups,enquiry)
print(f'Created {len(doc)} PDF pages: {len(products)} products across {len(groups)} collections.')
print(DEST); print(browser)
