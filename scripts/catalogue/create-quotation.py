"""Create the M&A-branded, image-first quotation without pricing/source columns."""
import argparse
import math
import re
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf
from PIL import Image as PILImage, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak

from quotation_source import load_quotation

parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,default=Path(r'C:\Users\Hamza\Downloads\Ecomass_Quotation_261019 (1).xlsx'))
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/Ecomass_Quotation_without_USD_pricing.pdf'
TMP=ROOT/'tmp/pdfs/quotation-review'
TMP.mkdir(parents=True,exist_ok=True)
cells,images=load_quotation(args.source)
pdfmetrics.registerFont(TTFont('Arial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
style=ParagraphStyle('cell',fontName='Arial',fontSize=8.6,leading=11.6,textColor=colors.HexColor('#262922'))
head=ParagraphStyle('head',parent=style,fontName='ArialBold',fontSize=8.4,leading=11,textColor=colors.white)

def value(column,row):
    text=cells.get(f'{column}{row}','')
    return re.sub(r'^(\d+)\.0$',r'\1',text) if column=='A' else text

def paragraph(text,sty=style):
    text=escape(text)
    text=re.sub(r'([\uac00-\ud7af]+)',r'<font name="HYSMyeongJo-Medium">\1</font>',text)
    return Paragraph(text,sty)

rows=list(range(5,90))
assert all(value('A',r)==str(r-4) for r in rows)
assert len(images)==84
columns=list('ABCDEFGH')
widths=[29,50,72,150,180,56,83,173.8897637795277]
page_count=math.ceil(len(rows)/6)
minimum,extra=divmod(len(rows),page_count)
story=[]
offset=0
for index in range(page_count):
    count=minimum+(index<extra)
    batch=rows[offset:offset+count]
    offset+=count
    if index: story.append(PageBreak())
    data=[[paragraph(value(c,4),head) for c in columns]]
    for row in batch:
        line=[paragraph(value(c,row)) for c in columns]
        if row in images:
            raw=images[row]
            with PILImage.open(BytesIO(raw)) as source:
                width,height=source.size
            scale=min(138/width,62/height)
            line[3]=Image(BytesIO(raw),width=width*scale,height=height*scale)
        else:
            line[3]=paragraph('')
        for i,item in enumerate(line):
            _,height=item.wrap(widths[i]-12,1000)
            assert height<=62.01,(row,columns[i],height,'Cell overflow')
        data.append(line)
    table=Table(data,colWidths=widths,rowHeights=[28]+[74]*len(batch),hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#a70027')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#fff5f3')]),
        ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#a70027')),
        ('LINEBELOW',(0,1),(-1,-1),.4,colors.HexColor('#e7d5d3')),
        ('LINEAFTER',(0,0),(-2,-1),.25,colors.HexColor('#e7d5d3')),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('ALIGN',(3,1),(3,-1),'CENTER'),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)
    ]))
    story.append(table)

W,H=landscape(A4)
def brand(canvas,doc):
    canvas.saveState()
    canvas.drawImage(str(ROOT/'assets/images/brand-logo.png'),24,H-53,width=190,height=34.4,mask='auto')
    canvas.setFont('Arial',8)
    canvas.setFillColor(colors.HexColor('#727168'))
    canvas.drawRightString(W-24,H-33,'PRODUCT QUOTATION')
    canvas.setStrokeColor(colors.HexColor('#dbaba7'))
    canvas.setLineWidth(.6)
    canvas.line(24,H-66,W-24,H-66)
    canvas.setFont('Arial',7.5)
    canvas.drawString(24,17,'M&A Industries')
    canvas.drawRightString(W-24,17,f'{doc.page:02} / {page_count:02}')
    canvas.restoreState()

# Build to a temporary file; replace the requested output only after validation.
draft=TMP/'quotation-updated.pdf'
doc=SimpleDocTemplate(str(draft),pagesize=(W,H),rightMargin=18,leftMargin=18,
    topMargin=78,bottomMargin=30,title='M&A Industries | Product Quotation',author='M&A Industries')
doc.build(story,onFirstPage=brand,onLaterPages=brand)
pdf=pymupdf.open(draft)
assert len(pdf)==page_count,(len(pdf),page_count)
all_text=' '.join(' '.join(page.get_text().split()) for page in pdf)
for forbidden in ['Quotation - Ecomass','Source:','FOB Korea','USD','PDF Page','Unit Price']:
    assert forbidden not in all_text,forbidden
offset=0
for index,page in enumerate(pdf):
    count=minimum+(index<extra)
    text=' '.join(page.get_text().split())
    for row in rows[offset:offset+count]:
        for col in 'BCEFGH':
            assert re.sub(r'\s+','',value(col,row)) in re.sub(r'\s+','',text),(row,col,value(col,row))
    offset+=count
    assert any(tuple(image[2:4])==PILImage.open(ROOT/'assets/images/brand-logo.png').size for image in page.get_images())
    for block in page.get_text('blocks'):
        assert block[0]>=0 and block[1]>=0 and block[2]<=W+1 and block[3]<=H+1,(index,block)
    page.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4),alpha=False).save(TMP/f'page-{index+1:02}.png')
sheet=PILImage.new('RGB',(4*430,4*325),'#e7d5d3')
draw=ImageDraw.Draw(sheet)
for i in range(len(pdf)):
    with PILImage.open(TMP/f'page-{i+1:02}.png') as preview:
        preview.thumbnail((420,297))
        x=(i%4)*430+5;y=(i//4)*325+5
        sheet.paste(preview,(x,y));draw.text((x,y+300),f'Page {i+1}',fill='#262922')
sheet.save(TMP/'overview.png')
pdf.close()
OUT.write_bytes(draft.read_bytes())
print(f'Updated {OUT}: {len(rows)} items, {len(images)} original images, {page_count} pages. All item fields verified.')
