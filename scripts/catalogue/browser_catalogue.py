"""Portable client catalogue using the same variants as the PDF and website."""
import base64
import html
from pathlib import Path
from catalogue_images import image_bytes


def create_browser_catalogue(root, destination, products, groups, enquiry):
    escape = html.escape
    slides = []
    for i, product in enumerate(products):
        source = 'data:image/jpeg;base64,' + base64.b64encode(image_bytes(root / product['image'])).decode()
        group = next(g for g in groups if g['id'] == product['group'])
        if product.get('variants'):
            rows = []
            for v in product['variants']:
                details = '; '.join(filter(None, [v.get('thickness') and 'Thickness: ' + v['thickness'], v.get('dimensions'), v.get('capacity') and 'Capacity: ' + v['capacity'], v.get('notes')]))
                rows.append(f'<tr><th scope="row">{escape(v["name"])}</th><td>{escape(details or "Confirm on enquiry")}</td><td>{escape(v["pack"])}</td></tr>')
            specifications = '<div class="table-wrap" tabindex="0" role="region" aria-label="Available variants"><table><caption>Dimensions &amp; pack options</caption><thead><tr><th scope="col">Variant</th><th scope="col">Dimensions / format</th><th scope="col">Pack / unit</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
        else:
            rows = []
            for spec in product.get('specifications', []):
                if isinstance(spec, dict): label, value = spec['label'], spec['value']
                else:
                    label, separator, value = spec.partition(':')
                    if not separator: label, value = 'Information', label
                rows.append(f'<div><dt>{escape(label)}</dt><dd>{escape(value.strip())}</dd></div>')
            specifications = '<dl class="spec-list">' + ''.join(rows) + '</dl>' if rows else '<p class="availability">Sizes and pack quantities confirmed on enquiry.</p>'
        note = f'<p class="technical-note">{escape(product["technicalNotes"])}</p>' if product.get('technicalNotes') else ''
        slides.append(f'''<section class="slide" aria-label="{escape(product['name'])}">
<div class="visual"><span class="folio">{i+1:02} / {len(products):02}</span><figure><img src="{source}" alt="{escape(product['name'])}"></figure></div>
<div class="copy"><p class="eyebrow">{escape(group['name'])}</p><h1>{escape(product['name'])}</h1>
<p class="description">{escape(product.get('overview',product['desc']))}</p><div class="material"><h2>Material</h2><p>{escape(product.get('material', 'Composition confirmed on enquiry'))}</p></div>
<p class="uses"><b>Applications</b> {escape(' / '.join(product['uses']))}</p>{specifications}{note}
<a class="cta" href="{escape(enquiry(product))}" target="_blank" rel="noopener">Enquire about this product <span aria-hidden="true">&#8599;</span></a>
<small>Confirm the selected variant, suitability and availability on enquiry.</small></div></section>''')
    options = []
    for group in groups:
        options.append(f'<optgroup label="{escape(group["name"])}">')
        options.extend(f'<option value="{i}">{escape(p["name"])}</option>' for i,p in enumerate(products) if p['group']==group['id'])
        options.append('</optgroup>')
    template = Path(__file__).with_name('interactive.html').read_text(encoding='utf-8')
    destination.write_text(template.replace('SLIDES', ''.join(slides)).replace('OPTIONS', ''.join(options)), encoding='utf-8')
