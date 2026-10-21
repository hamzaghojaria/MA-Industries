"""Create a focused PDF and a portable animated browser catalogue."""
import base64
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

import pymupdf
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

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

def text(x,y,s,size=10,color=INK,font='Helvetica'):
    c.setFillColor(HexColor(color)); c.setFont(font,size); c.drawString(x,y,s)

def para(x,y,s,w,size=12,leading=18,color=INK,font='Helvetica'):
    p=Paragraph(html.escape(s),ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,h=p.wrap(w,1000); p.drawOn(c,x,y-h); return h

def rect(x,y,w,h,color):
    c.setFillColor(HexColor(color)); c.rect(x,y,w,h,fill=1,stroke=0)

def photo(p,x,y,w,h):
    image=ImageReader(str(ROOT / p['image'])); iw,ih=image.getSize(); scale=min(w/iw,h/ih)
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
    rect(40,305,515,320,'#ffffff')
    photo(p,57,322,481,286)
    text(40,278,'THE MATERIAL',8,GREEN,'Helvetica-Bold')
    para(40,263,p.get('material','Specifications confirmed on enquiry'),500,10,14,MUTED)
    para(40,217,p['desc'],490,12,17)
    text(40,154,'SUITED TO',8,GREEN,'Helvetica-Bold')
    para(40,140,' / '.join(p['uses']),490,10,14,MUTED)
    rect(40,70,230,36,RED)
    text(55,83,'ENQUIRE ABOUT THIS PRODUCT  >',9,'#ffffff','Helvetica-Bold')
    c.linkURL(enquiry(p),(40,70,270,106))
    text(298,84,'Sizes & pack quantities on enquiry',8,MUTED)
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

# A self-contained browser edition: no network dependencies or remote images.
slides=[]
for i,p in enumerate(products):
    image_path=ROOT/p['image']
    mime='image/webp' if image_path.suffix=='.webp' else 'image/jpeg'
    src='data:'+mime+';base64,'+base64.b64encode(image_path.read_bytes()).decode()
    g=next(g for g in groups if g['id']==p['group'])
    e=html.escape
    slides.append(f'''<section class="slide" aria-label="{e(p['name'])}"><div class="visual"><span class="folio">{i+1:02} / {len(products):02}</span><img src="{src}" alt="{e(p['name'])}"></div><div class="copy"><p class="eyebrow">{e(g['name'])}</p><h1>{e(p['name'])}</h1><p class="description">{e(p['desc'])}</p><div class="spec"><b>THE MATERIAL</b><p>{e(p.get('material','Specifications on enquiry'))}</p><b>SUITED TO</b><p>{e(' / '.join(p['uses']))}</p></div><a class="cta" href="{e(enquiry(p))}" target="_blank" rel="noopener">Enquire about this product <span>↗</span></a><small>Composition, sizes and availability confirmed on enquiry.</small></div></section>''')
options=''.join(f'<option value="{i}">{html.escape(p["name"])}</option>' for i,p in enumerate(products))
template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>M&A Industries | Sugarcane & Recycled</title><style>
*{box-sizing:border-box}body{margin:0;background:#faf9f4;color:#203d35;font-family:Arial,sans-serif}header{height:88px;padding:24px 4vw;border-bottom:1px solid #ccd4c9;display:flex;justify-content:space-between;align-items:center;gap:20px}.brand{font-weight:bold;font-size:20px}.brand span{color:#a70027}header p{font-size:10px;letter-spacing:2px}main{min-height:calc(100svh - 170px)}.slide{display:none;grid-template-columns:1.12fr 1fr;min-height:calc(100svh - 170px)}.slide.active{display:grid}.visual{position:relative;background:#edf0e7;display:flex;align-items:center;justify-content:center;padding:65px}.visual img{width:100%;height:55vh;object-fit:contain;mix-blend-mode:multiply;animation:arrive .8s ease both}.folio{position:absolute;top:30px;left:4vw;font-size:12px;letter-spacing:3px}.copy{padding:5vh 5vw;align-self:center;animation:reveal .6s ease both}.eyebrow{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#58705d}h1{font:clamp(32px,3.4vw,60px)/1.05 Georgia,serif;margin:24px 0}.description{font-size:16px;line-height:1.65;color:#5b685f}.spec{border-top:1px solid #ccd4c9;margin-top:25px;padding-top:20px}.spec b{font-size:9px;letter-spacing:2px}.spec p{font-size:12px;line-height:1.6;color:#65716a}.cta{display:flex;justify-content:space-between;background:#203d35;color:white;text-decoration:none;padding:19px 23px;margin-top:25px;font-size:12px;transition:background .2s,transform .2s}.cta:hover{background:#345c49;transform:translateY(-3px)}small{display:block;font-size:9px;color:#65716a;margin-top:15px}footer{display:flex;align-items:center;gap:14px;min-height:82px;padding:16px 4vw;border-top:1px solid #ccd4c9}button,select{font:12px Arial;padding:12px;border:1px solid #b9c5b8;background:transparent;color:#203d35;cursor:pointer}button:disabled{opacity:.3;cursor:default}select{max-width:45vw}#progress{height:3px;background:#a70027;position:fixed;bottom:0;left:0;transition:width .5s}#count{margin-left:auto;font-size:11px;white-space:nowrap}@keyframes arrive{from{opacity:0;transform:scale(.95) translateY(20px)}to{opacity:1;transform:none}}@keyframes reveal{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}@media(max-width:750px){header{height:auto}.brand{font-size:16px}header p{max-width:130px;line-height:1.5}.slide.active{grid-template-columns:1fr}.visual{padding:50px 25px 25px}.visual img{height:32vh}.copy{padding:25px}.folio{top:20px}.copy h1{margin:16px 0}footer{flex-wrap:wrap;gap:8px}select{max-width:100%;flex:1}#count{display:none}}@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}@media print{header,footer,#progress{display:none}.slide,.slide.active{display:grid;break-after:page;min-height:95vh}.copy,.visual img{animation:none}.cta{color:#203d35;background:white}}
</style><header><div class="brand"><span>M&A</span> INDUSTRIES</div><p>SUGARCANE & RECYCLED<br>THE CONSIDERED COLLECTION</p></header><main>SLIDES</main><footer><button id="prev" aria-label="Previous product">← Previous</button><select id="jump" aria-label="Choose product">OPTIONS</select><button id="next" aria-label="Next product">Next →</button><span id="count"></span></footer><div id="progress"></div><script>
const slides=[...document.querySelectorAll('.slide')],jump=document.querySelector('#jump'),prev=document.querySelector('#prev'),next=document.querySelector('#next');let index=0;function show(n){index=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>{s.classList.toggle('active',i===index);s.setAttribute('aria-hidden',i!==index)});jump.value=index;prev.disabled=index===0;next.disabled=index===slides.length-1;document.querySelector('#count').textContent=String(index+1).padStart(2,'0')+' / '+slides.length;document.querySelector('#progress').style.width=((index+1)/slides.length*100)+'%'}prev.onclick=()=>show(index-1);next.onclick=()=>show(index+1);jump.onchange=()=>show(Number(jump.value));document.addEventListener('keydown',e=>{if(/SELECT|INPUT|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowRight')show(index+1);if(e.key==='ArrowLeft')show(index-1)});show(0);
</script></html>'''
browser=OUT/'MA-Industries-Interactive-Catalogue.html'
browser.write_text(template.replace('SLIDES',''.join(slides)).replace('OPTIONS',options),encoding='utf-8')
print(f'Created {len(doc)} PDF pages: {len(products)} products across {len(groups)} collections.')
print(DEST); print(browser)
