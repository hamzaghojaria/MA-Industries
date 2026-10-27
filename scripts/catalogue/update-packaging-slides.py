"""Replace product artwork in existing decks without rebuilding their layouts."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[2]
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
ART = {'cups': ROOT/'assets/images/products/sugarcane-paper-cups-wrapped.png',
       'bowls': ROOT/'assets/images/products/sugarcane-bowls-pack.png'}
report = []
for deck in sorted((ROOT/'output/presentations').glob('*.pptx')):
    if deck.stem.endswith('.updated'):
        continue
    with ZipFile(deck) as z:
        files = {name: z.read(name) for name in z.namelist()}
    original = dict(files)
    changes = []
    for name, content in list(files.items()):
        if not re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
            continue
        slide = ET.fromstring(content)
        text = ' '.join(t.text or '' for t in slide.findall('.//a:t', NS)).lower()
        kind = 'cups' if 'paper cups' in text else 'bowls' if 'sugarcane bowls' in text else None
        if not kind:
            continue
        relname = posixpath.join(posixpath.dirname(name), '_rels', posixpath.basename(name)+'.rels')
        rels = ET.fromstring(files[relname])
        for pic in slide.findall('.//p:pic', NS):
            if pic.find('.//p:cNvPr', NS).get('name') != 'HERO_IMAGE':
                continue
            rid = pic.find('.//a:blip', NS).get(RID)
            relation = next(r for r in rels if r.get('Id') == rid)
            target = f'../media/custom-packaging-{kind}.png'
            old = relation.get('Target')
            # Change only the selected relationship, keeping the slide XML intact.
            reltext = files[relname].decode('utf-8')
            pattern = r'(<(?:\w+:)?Relationship\b[^>]*\bId="'+re.escape(rid)+r'"[^>]*\bTarget=")([^"]+)(")'
            updated, count = re.subn(pattern, lambda m: m[1]+target+m[3], reltext)
            if count != 1:
                relation.set('Target', target)
                updated = ET.tostring(rels, encoding='unicode')
            files[relname] = updated.encode('utf-8')
            files[f'ppt/media/custom-packaging-{kind}.png'] = ART[kind].read_bytes()
            changes.append({'slide': name, 'product': kind})
    if not changes:
        continue
    types = ET.fromstring(files['[Content_Types].xml'])
    if not any(e.get('Extension') == 'png' for e in types):
        ET.SubElement(types, '{http://schemas.openxmlformats.org/package/2006/content-types}Default',
                      Extension='png', ContentType='image/png')
        files['[Content_Types].xml'] = ET.tostring(types, encoding='utf-8', xml_declaration=True)
    temp = deck.with_suffix('.updated.pptx')
    with ZipFile(temp, 'w', ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    with ZipFile(temp) as z:
        assert z.testzip() is None
        for name, content in original.items():
            if re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
                assert z.read(name) == content, 'Slide layout or text changed'
        for kind in {c['product'] for c in changes}:
            assert z.read(f'ppt/media/custom-packaging-{kind}.png') == ART[kind].read_bytes()
    try:
        temp.replace(deck)
        destination = deck
    except PermissionError:
        destination = temp
    report.append({'deck': destination.name, 'changes': changes})
    print(destination.name, len(changes), 'images updated')
(ROOT/'tmp/ppt-update/packaging-update-report.json').write_text(json.dumps(report, indent=2))
