"""Read quotation cells and embedded images without an Excel dependency."""
import posixpath
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import ZipFile

S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
D = '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


def load_quotation(path):
    with ZipFile(path) as archive:
        def xml(name):
            return ET.fromstring(archive.read(name))

        def relationships(part):
            p = PurePosixPath(part)
            rel = str(p.parent / '_rels' / (p.name + '.rels'))
            return {e.attrib['Id']: posixpath.normpath(posixpath.join(str(p.parent), e.attrib['Target'])).lstrip('/')
                    for e in xml(rel)}

        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(t.text or '' for t in si.iter(S + 't')) for si in xml('xl/sharedStrings.xml')]
        workbook = xml('xl/workbook.xml')
        sheet = next(e for e in workbook.iter(S + 'sheet') if e.attrib['name'] == 'Quotation')
        sheet_path = relationships('xl/workbook.xml')[sheet.attrib[R + 'id']]
        tree = xml(sheet_path)
        cells = {}
        for cell in tree.iter(S + 'c'):
            value = cell.find(S + 'v')
            value = value.text if value is not None else ''
            if cell.attrib.get('t') == 's':
                value = shared[int(value)]
            elif cell.attrib.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.iter(S + 't'))
            cells[cell.attrib['r']] = value or ''
        images = {}
        for drawing in tree.iter(S + 'drawing'):
            drawing_path = relationships(sheet_path)[drawing.attrib[R + 'id']]
            image_paths = relationships(drawing_path)
            for anchor in xml(drawing_path):
                row = anchor.find(f'{D}from/{D}row')
                blip = anchor.find(f'.//{A}blip')
                if row is not None and blip is not None:
                    images[int(row.text) + 1] = archive.read(image_paths[blip.attrib[R + 'embed']])
        return cells, images
