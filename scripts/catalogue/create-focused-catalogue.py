"""Produce the branded client catalogue and browser edition from shared product data."""
import html
import argparse
import json
import math
import shutil
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import pymupdf
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from browser_catalogue import create_browser_catalogue
from catalogue_images import image_bytes

ROOT = Path(__file__).resolve().parents[2]
OUT, TMP = ROOT / 'output/pdf', ROOT / 'tmp/pdfs'
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description='Build the full catalogue or one collection catalogue.')
parser.add_argument('--collection', choices=['clean-republic', 'sugarcane-recycled'])
args = parser.parse_args()
data = json.loads((TMP / 'catalogue-data.json').read_text(encoding='utf-8'))
groups = [g for g in data['categories'] if not args.collection or g['collection'] == args.collection]
products = [p for g in groups for p in data['papers'] if p['group'] == g['id']]
assert products and groups
W, H = 595.276, 841.89
M, CW = 40, W-80
INK, GREEN, MUTED = '#24382e', '#245c3a', '#647269'
CREAM, LINE = '#f5f4ee', '#dce3d8'
FILENAMES = {
    'clean-republic': 'MA-Industries-Cleaning-Hygiene-Catalogue.pdf',
    'sugarcane-recycled': 'MA-Industries-Sugarcane-Recycled-Catalogue.pdf'
}
COLLECTION_NAMES = {
    'clean-republic': 'Cleaning & Hygiene',
    'sugarcane-recycled': 'Sugarcane & Recycled'
}
INTRO_PAGES = {
    'all': {
        'image': 'assets/images/catalogue-intros/full-range-industry-grid.png',
        'eyebrow': 'For the spaces and routines you look after',
        'title': 'Products for the work of every day.',
        'copy': 'From food service and paper to recycled household essentials and cleaning, our ranges support the everyday work of homes, workplaces and shared spaces.',
        'labels': ['Hospitality', 'Food & Beverage', 'Packing & Retail', 'Care & Education', 'Commercial Cleaning', 'Industry & Recycling'],
        'promise': 'Choose by task. Compare products, sizes and formats.',
        'cards': [('SERVE', 'Tableware and food-service essentials'), ('PACK', 'Paper, bags and packaging formats'), ('CARE', 'Cleaning and household products')]
    },
    'clean-republic': {
        'image': 'assets/images/catalogue-intros/cleaning-hygiene-industry-grid.png',
        'eyebrow': 'Cleaning & Hygiene',
        'title': 'Cleaning for the spaces people share.',
        'copy': 'Explore floor and surface care, washroom hygiene and commercial cleaning for hospitality, transport, food service, healthcare, education and industrial settings.',
        'labels': ['Hospitality', 'Commercial Cleaning', 'Auto & Transport', 'Health & Care', 'Food Service', 'Industry'],
        'promise': 'Start with the space. Check the surface, pack and instructions.',
        'cards': [('HOME & SURFACE', 'Floor, kitchen and glass care'), ('HAND & WASHROOM', 'Handwash and washroom care'), ('COMMERCIAL', 'Cleaning for work and transport')]
    },
    'sugarcane-recycled': {
        'image': 'assets/images/catalogue-intros/sugarcane-recycled-industry-grid.png',
        'eyebrow': 'Sugarcane & Recycled',
        'title': 'Thoughtful essentials for daily use.',
        'copy': 'Explore sugarcane-based products for serving, packing and paper use, alongside recycled household goods for kitchens, offices and storage.',
        'labels': ['Food Service', 'Kitchen & Dining', 'Packaging', 'Office & Paper', 'Home Storage', 'Recycling'],
        'promise': 'Find a useful format for serving, packing or organising.',
        'cards': [('SUGARCANE', 'Kitchenware, bags and paper'), ('RECYCLED', 'Household storage and tools'), ('BY FORMAT', 'Compare sizes and pack details')]
    }
}
collection_name = COLLECTION_NAMES.get(args.collection, 'The collection')
DEST = OUT / (FILENAMES[args.collection] if args.collection else 'MA-Industries-Catalogue.pdf')
fonts = Path(reportlab.__file__).parent / 'fonts'
for name, candidates in {
    'Body': ['C:/Windows/Fonts/arial.ttf', str(fonts/'Vera.ttf')],
    'Bold': ['C:/Windows/Fonts/arialbd.ttf', str(fonts/'VeraBd.ttf')],
    'Display': ['C:/Windows/Fonts/georgia.ttf', str(fonts/'Vera.ttf')],
    'Italic': ['C:/Windows/Fonts/georgiai.ttf', str(fonts/'VeraIt.ttf')]
}.items():
    pdfmetrics.registerFont(TTFont(name, next(p for p in candidates if Path(p).exists())))
c = canvas.Canvas(str(DEST), pagesize=(W,H), pageCompression=1)
c.setTitle('M&A Industries | ' + (COLLECTION_NAMES.get(args.collection, 'Product Collection')))
c.setAuthor('M&A Industries')
c.setSubject('Sugarcane, recycled household, cleaning and hygiene product specifications')
page_number = 0
product_pages = {}
category_pages = {}

def rect(x, top, width, height, color):
    c.setFillColor(HexColor(color)); c.rect(x,H-top-height,width,height,fill=1,stroke=0)

def line(x, top, width=CW, color=LINE):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(.6); c.line(x,H-top,x+width,H-top)

def text(x, top, value, size=10, color=INK, font='Body'):
    c.setFillColor(HexColor(color)); c.setFont(font,size); c.drawString(x,H-top-size,value)

def para(x, top, value, width, size=10, leading=15, color=INK, font='Body'):
    p = Paragraph(html.escape(str(value)), ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,height=p.wrap(width,1000); p.drawOn(c,x,H-top-height); return height

def photo(product, x, top, width, height):
    image=ImageReader(BytesIO(image_bytes(ROOT/product['image'])));iw,ih=image.getSize();scale=min(width/iw,height/ih)
    c.drawImage(image,x+(width-iw*scale)/2,H-top-height+(height-ih*scale)/2,iw*scale,ih*scale,mask='auto')

def base(label, background='#ffffff'):
    global page_number
    page_number+=1
    rect(0,0,W,H,background)
    c.drawImage(str(ROOT/'assets/images/brand-logo.png'),M,H-64,width=167,height=30.25,mask='auto')
    text(396,44,'PRODUCT COLLECTION',8,MUTED,'Bold')
    line(M,82)
    line(M,802)
    text(M,814,'M&A INDUSTRIES  /  '+label.upper(),7,MUTED)
    c.setFillColor(HexColor(MUTED));c.setFont('Body',8);c.drawRightString(W-M,H-814-8,f'{page_number:02}')

def eyebrow(top,value): text(M,top,value.upper(),8.5,GREEN,'Bold')

def introduction_page():
    key=args.collection or 'all'
    content=INTRO_PAGES[key]
    base('Introduction')
    eyebrow(106,content['eyebrow'])
    title_height=para(M,131,content['title'],CW,27,33,INK,'Display')
    copy_top=140+title_height
    copy_height=para(M,copy_top,content['copy'],CW,10.5,15,MUTED)
    grid_top=max(231,copy_top+copy_height+17)
    grid_height=CW*2/3
    grid_image=ImageReader(BytesIO(image_bytes(ROOT/content['image'])))
    c.drawImage(grid_image,M,H-grid_top-grid_height,width=CW,height=grid_height,mask='auto')
    cell_width=CW/3;cell_height=grid_height/2;label_height=34
    for i,label in enumerate(content['labels']):
        column,row= i%3,i//3
        x=M+column*cell_width;top=grid_top+row*cell_height
        bar_top=top+cell_height-label_height
        rect(x,bar_top,cell_width,label_height,GREEN)
        style=ParagraphStyle('industry-label',fontName='Bold',fontSize=8.5,leading=10.5,textColor=HexColor('#ffffff'),alignment=1)
        label_para=Paragraph(html.escape(label),style)
        _,label_text_height=label_para.wrap(cell_width-14,label_height-6)
        label_para.drawOn(c,x+7,H-bar_top-(label_height-label_text_height)/2-label_text_height)
    # Fine white seams keep the six photographs distinct when printed.
    rect(M+cell_width-1,grid_top,2,grid_height,'#ffffff')
    rect(M+cell_width*2-1,grid_top,2,grid_height,'#ffffff')
    rect(M,grid_top+cell_height-1,CW,2,'#ffffff')
    promise_top=grid_top+grid_height+16
    para(M,promise_top,content['promise'],CW,10,14,GREEN,'Bold')
    cards_top=promise_top+25;gap=8;card_width=(CW-gap*2)/3;card_height=63
    title_style=ParagraphStyle('intro-card-title',fontName='Bold',fontSize=7.5,leading=9,textColor=HexColor(GREEN),alignment=1)
    detail_style=ParagraphStyle('intro-card-copy',fontName='Body',fontSize=7.2,leading=9,textColor=HexColor(MUTED),alignment=1)
    for i,(heading,copy) in enumerate(content['cards']):
        x=M+i*(card_width+gap)
        rect(x,cards_top,card_width,card_height,CREAM)
        rect(x,cards_top,card_width,2,GREEN)
        head=Paragraph(html.escape(heading),title_style);_,hh=head.wrap(card_width-12,20)
        head.drawOn(c,x+6,H-(cards_top+10)-hh)
        body=Paragraph(html.escape(copy),detail_style);_,bh=body.wrap(card_width-12,26)
        body.drawOn(c,x+6,H-(cards_top+29)-bh)
    assert cards_top+card_height < 790, (key,'introduction page overflow',cards_top+card_height)
    c.showPage()

def enquiry(product):
    return 'https://wa.me/919819157417?text='+quote('Hello M&A Industries, I would like to enquire about '+product['name']+'. Please share specifications, pack sizes, pricing and availability.')

def details(variant):
    return '; '.join(filter(None,[variant.get('thickness') and 'Thickness: '+variant['thickness'],variant.get('dimensions'),variant.get('capacity') and 'Capacity: '+variant['capacity'],variant.get('notes')]))

def specifications(product):
    return [f"{s['label']}: {s['value']}" if isinstance(s,dict) else s for s in product.get('specifications',[])]

def spec_table(product,top,draw=True):
    ps=ParagraphStyle('cell',fontName='Body',fontSize=9,leading=12,textColor=HexColor(INK))
    bold=ParagraphStyle('cell-bold',parent=ps,fontName='Bold')
    head=ParagraphStyle('cell-head',parent=ps,fontName='Bold',fontSize=8,textColor=HexColor('#ffffff'))
    cell=lambda s,style=ps:Paragraph(html.escape(str(s)),style)
    if product.get('variants'):
        rows=[[cell('VARIANT',head),cell('DIMENSIONS / FORMAT',head),cell('PACK / UNIT',head)]]
        rows += [[cell(v['name'],bold),cell(details(v) or 'Confirm on enquiry'),cell(v['pack'])] for v in product['variants']]
        widths=[158,CW-158-72,72]
    else:
        rows=[[cell('SPECIFICATION',head),cell('DETAIL',head)]]
        for spec in product.get('specifications',[]):
            if isinstance(spec,dict):label,value=spec['label'],spec['value']
            else:label,separator,value=spec.partition(':');value=value.strip() if separator else label;label=label if separator else 'Product information'
            rows.append([cell(label,bold),cell(value)])
        if len(rows)==1:rows.append([cell('Size & pack',bold),cell('Sizes and pack quantities confirmed on enquiry.')])
        widths=[158,CW-158]
    table=Table(rows,colWidths=widths,hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),HexColor(GREEN)),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#f4f6f1'),HexColor('#ffffff')]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LINEBELOW',(0,1),(-1,-1),.4,HexColor(LINE))]))
    _,height=table.wrap(CW,H)
    if not draw: return height
    assert top+height<=728,(product['id'],'specification table overflow',top+height)
    table.drawOn(c,M,H-top-height)
    return top+height

# Cover: clear brand hierarchy with a restrained product composition.
base(collection_name,CREAM)
eyebrow(112,collection_name if args.collection else 'Everyday products. Considered materials.')
para(M,145,'For the work of every day.',CW,40,47,INK,'Display')
para(M,203,collection_name if args.collection else 'Choose around the job.',CW,29,38,GREEN,'Italic')
cover_copy = {
    'clean-republic': 'Browse cleaning, surface-care and hygiene essentials for homes, workplaces and commercial spaces.',
    'sugarcane-recycled': 'Explore sugarcane essentials for serving and packing, alongside recycled household goods for everyday organising.'
}.get(args.collection, 'Find sugarcane and recycled essentials for serving, packing and organising, alongside M&A cleaning products for the spaces you clean.')
para(M,264,cover_copy,440,12,19,MUTED)
rect(M,345,CW,302,'#e5ece0')
hero=next((p for p in products if p['id']=='cr-pine-floor-cleaner'),products[0])
photo(hero,M+18,359,CW-36,274)
text(M,683,f'{len(products):02} PRODUCT FAMILIES',10,GREEN,'Bold')
text(279,683,f'{len(groups):02} CATEGORIES',10,GREEN,'Bold')
line(M,719)
text(M,739,'+91 98191 57417',13,INK,'Bold')
text(M,762,'info@maindustries.in  /  maindustries.in',10,MUTED)
c.linkURL('https://maindustries.in/',(M,H-780,W-M,H-735))
c.showPage()

# Page two introduces the audience and uses a collection-specific image grid.
introduction_page()

# Collection directory, with internal links and explicit page locations.
base('Collection directory')
eyebrow(108,'Explore the collection')
para(M,134,'Find the right starting point.',CW,29,37,INK,'Display')
para(M,183,'Browse by collection, then compare product details and available variants.',CW,11,17,MUTED)
next_page = 4
gap = 14
tile_width = (CW - gap) / 2
tile_height = 105
for i, g in enumerate(groups):
    members = [p for p in products if p['group'] == g['id']]
    category_pages[g['id']] = next_page
    row, column = divmod(i, 2)
    x = M + column * (tile_width + gap)
    top = 225 + row * (tile_height + gap)
    assert top + tile_height < 736, 'Collection directory needs another page'
    rect(x, top, tile_width, tile_height, CREAM)
    photo(members[0], x + 8, top + 15, 72, 72)
    text(x + 91, top + 13, f'{len(members):02} PRODUCTS', 8, GREEN, 'Bold')
    para(x + 91, top + 30, g['name'], tile_width - 102, 13, 16, INK, 'Bold')
    text(x + 91, top + 83, f'VIEW CATEGORY / PAGE {next_page:02}', 7, GREEN, 'Bold')
    c.linkRect('', g['id'], (x, H - top - tile_height, x + tile_width, H - top), thickness=0)
    next_page += len(members) + 1

para(M,742,'All dimensions follow the listed variant. Confirm composition, suitability and order availability with our team.',CW,9,14,MUTED)
c.showPage()

# Collection dividers and product pages use one consistent grid.
ordinal=0
for gi,g in enumerate(groups):
    members=[p for p in products if p['group']==g['id']]
    base(g['name'],CREAM)
    c.bookmarkPage(g['id']);c.addOutlineEntry(g['name'],g['id'],0)
    assert page_number==category_pages[g['id']]
    text(M,119,f'0{gi+1}',64,GREEN,'Display')
    title_height=para(M,214,g['name'],CW,37,44,INK,'Display')
    para(M,230+title_height,g['desc'],440,12,19,MUTED)
    rect(M,360,CW,291,'#ffffff');photo(members[0],M+15,372,CW-30,267)
    text(M,687,f'{len(members):02} PRODUCT FAMILIES',10,GREEN,'Bold')
    para(M,719,'Compare the options. Share your requirement.',CW,21,28,INK,'Display')
    c.showPage()
    for p in members:
        ordinal+=1;base(g['name'])
        c.bookmarkPage(p['id']);c.addOutlineEntry(p['name'],p['id'],1);product_pages[p['id']]=page_number
        eyebrow(105,f'{g["name"]}  /  {ordinal:02} OF {len(products):02}')
        title_height=para(M,127,p['name'],CW,28,33,INK,'Bold')
        assert title_height<=66,(p['id'],'title too long')
        desc_top=133+title_height
        desc_height=para(M,desc_top,p.get('overview',p['desc']),CW,10,15,MUTED)
        image_top=max(201,desc_top+desc_height+12)
        table_height=spec_table(p,0,draw=False)
        table_top=min(550,(685 if p.get('technicalNotes') else 724)-table_height)
        material=p.get('material','Composition confirmed on enquiry')
        applications=' / '.join(p['uses'])
        measure=lambda value: Paragraph(html.escape(value),ParagraphStyle('measure',fontName='Body',fontSize=9,leading=12)).wrap(CW-85,1000)[1]
        material_height=measure(material)
        applications_height=measure(applications)
        image_height=table_top-image_top-material_height-applications_height-42
        assert image_height>=120,(p['id'],'insufficient image space')
        rect(M,image_top,CW,image_height,CREAM);photo(p,M+16,image_top+8,CW-32,image_height-16)
        material_top=image_top+image_height+14
        text(M,material_top,'MATERIAL',7.5,GREEN,'Bold')
        para(M+85,material_top-1,material,CW-85,9,12,MUTED)
        applications_top=material_top+material_height+10
        text(M,applications_top,'APPLICATIONS',7.5,GREEN,'Bold')
        para(M+85,applications_top-1,applications,CW-85,9,12,MUTED)
        assert applications_top+applications_height+8<=table_top
        bottom=spec_table(p,table_top)
        note=p.get('technicalNotes')
        if note:
            h=para(M,bottom+10,note,CW,8,11,MUTED)
            assert bottom+10+h<=748,(p['id'],'technical note overflow')
        rect(M,757,235,31,GREEN)
        text(M+12,767,'ENQUIRE ABOUT THIS PRODUCT',8.5,'#ffffff','Bold')
        c.linkURL(enquiry(p),(M,H-788,M+235,H-757))
        text(M+257,761,'Options & availability on enquiry',8,MUTED)
        text(M+257,775,'maindustries.in',8,GREEN)
        c.linkURL('https://maindustries.in/products.html?category='+p['group']+'#paper-'+p['id'],(M+250,H-790,W-M,H-755))
        c.showPage()

base('Contact',CREAM)
eyebrow(118,'Let us discuss your requirement')
para(M,155,'The right product.',CW,39,49,INK,'Display')
para(M,208,'The details that matter.',CW,33,44,GREEN,'Italic')
para(M,287,'Tell us the product, selected variant, quantity and delivery location. We will help you confirm the specification and prepare your enquiry.',CW-20,13,21,MUTED)
for i,(title,copy) in enumerate([
    ('Choose the product','Share the product name and size or format.'),
    ('Define the order','Include the pack quantity and delivery location.'),
    ('Confirm the details','Discuss composition, suitability and availability.')]):
    top=411+i*86;line(M,top);text(M,top+19,f'0{i+1}',24,GREEN,'Display');text(M+58,top+20,title,13,INK,'Bold');para(M+58,top+43,copy,CW-58,10,15,MUTED)
rect(M,706,CW,70,GREEN)
text(M+18,720,'+91 98191 57417',19,'#ffffff','Bold')
text(M+18,750,'info@maindustries.in  /  maindustries.in',10,'#ffffff')
c.linkURL('https://wa.me/919819157417',(M,H-776,W-M,H-706))
c.showPage();c.save()

# Validate final output text, links, pagination and bounds, then render every page.
doc=pymupdf.open(DEST)
assert len(doc)==len(products)+len(groups)+4
normalize=lambda value:' '.join(value.replace('\u00b5','\u03bc').split())
for p in products:
    page=doc[product_pages[p['id']]-1];content=normalize(page.get_text())
    assert normalize(p['name']) in content,(p['id'],'Missing title')
    assert normalize(p.get('overview',p['desc'])) in content,(p['id'],'Missing overview')
    for use in p['uses']: assert normalize(use) in content,(p['id'],'Missing application',use)
    assert any(link.get('uri')==enquiry(p) for link in page.get_links()),(p['id'],'Missing enquiry link')
    for v in p.get('variants',[]):
        for field in ['name','dimensions','thickness','capacity','pack','notes']:
            if v.get(field):assert normalize(v[field]) in content,(p['id'],'Missing variant field',field,v[field])
    if not p.get('variants'):
        for spec in specifications(p):
            if 'Confirm packaging with supplier' in spec:
                continue
            assert normalize(spec.replace(': ', ' ')) in content.replace(': ', ' ') or all(normalize(t.strip()) in content for t in spec.split(':',1)),(p['id'],'Missing specification',spec)
for i,page in enumerate(doc):
    assert page.get_images(),('Page missing image',i+1)
    for block in page.get_text('blocks'):
        assert 0<=block[0] and 0<=block[1] and block[2]<=W+1 and block[3]<=H+1,(i+1,'Text outside page',block)
    page.get_pixmap(matrix=pymupdf.Matrix(1.05,1.05),alpha=False).save(TMP/f'focused-{i+1:02}.png')
if args.collection:
    public_copy=ROOT/'assets/catalogues'/DEST.name
    public_copy.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(DEST,public_copy)
else:
    for folder in [ROOT/'assets/catalogues',ROOT/'dist/assets/catalogues']:
        folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(DEST,folder/'MA-Industries-Catalogue.pdf')
    cols,tw,th=6,220,322
    sheet=Image.new('RGB',(cols*tw,math.ceil(len(doc)/cols)*th),'#dce3d8');draw=ImageDraw.Draw(sheet)
    for i in range(len(doc)):
        with Image.open(TMP/f'focused-{i+1:02}.png') as preview:
            preview.thumbnail((210,295));x=(i%cols)*tw+5;y=(i//cols)*th+5;sheet.paste(preview,(x,y));draw.text((x,y+298),f'Page {i+1}',fill=INK)
    sheet.save(OUT/'MA-Industries-Catalogue-Overview.png')
    (TMP/'catalogue-page-map.json').write_text(json.dumps(product_pages,indent=2))
    browser=OUT/'MA-Industries-Interactive-Catalogue.html'
    create_browser_catalogue(ROOT,browser,products,groups,enquiry)
    print(DEST);print(browser)
print(f'Created {len(doc)} verified pages: {len(products)} products across {len(groups)} categories.')
print(DEST)
