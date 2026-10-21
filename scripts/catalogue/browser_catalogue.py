"""Portable browser catalogue, sharing the PDF's product source and specifications."""
import base64
import html
from pathlib import Path
from catalogue_images import image_bytes


def create_browser_catalogue(root, destination, products, groups, enquiry):
    escape = html.escape
    slides = []
    for i, product in enumerate(products):
        image = root / product['image']
        source = 'data:image/jpeg;base64,' + base64.b64encode(image_bytes(image)).decode()
        group = next(g for g in groups if g['id'] == product['group'])
        rows = [f"{s['label']}: {s['value']}" if isinstance(s, dict) else s
                for s in product.get('specifications', [])]
        specifications = ''.join(f'<li>{escape(row)}</li>' for row in rows)
        if not specifications:
            specifications = '<li>Sizes and pack quantities confirmed on enquiry.</li>'
        slides.append(f'''<section class="slide" aria-label="{escape(product['name'])}">
<div class="visual"><span class="folio">{i+1:02} / {len(products):02}</span><img src="{source}" alt="{escape(product['name'])}"></div>
<div class="copy"><p class="eyebrow">{escape(group['name'])}</p><h1>{escape(product['name'])}</h1>
<p class="description">{escape(product['desc'])}</p><div class="spec"><b>THE MATERIAL</b>
<p>{escape(product.get('material', 'Specifications on enquiry'))}</p><b>DIMENSIONS &amp; SPECIFICATIONS</b>
<ul>{specifications}</ul><b>SUITED TO</b><p>{escape(' / '.join(product['uses']))}</p></div>
<a class="cta" href="{escape(enquiry(product))}" target="_blank" rel="noopener">Enquire about this product <span>↗</span></a>
<small>Confirm the selected variant, composition and availability on enquiry.</small></div></section>''')
    options = ''.join(f'<option value="{i}">{escape(p["name"])}</option>' for i, p in enumerate(products))
    template = Path(__file__).with_name('interactive.html').read_text(encoding='utf-8')
    destination.write_text(template.replace('SLIDES', ''.join(slides)).replace('OPTIONS', options), encoding='utf-8')
