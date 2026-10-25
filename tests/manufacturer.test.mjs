import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { loadCatalogue, ROOT } from '../scripts/site/catalogue-markup.mjs';
import { createPageFixture } from './page-fixture.mjs';
import vm from 'node:vm';

const catalogue = await loadCatalogue();
const source = JSON.parse(await readFile(new URL('scripts/references/manufacturer-product-specs.json', ROOT), 'utf8'));
const byId = new Map(catalogue.papers.map(product => [product.id, product]));

test('all 85 manufacturer variants map once to website products without supplier costs', () => {
  const variants = catalogue.papers.flatMap(product => (product.variants || []).map(variant => ({ productId: product.id, ...variant })));
  assert.equal(variants.length, 85);
  assert.equal(new Set(variants.map(variant => `${variant.sourcePage}:${variant.sourceRow}`)).size, 85);
  assert.equal(catalogue.papers.filter(product => product.variants).length, 30);
  for (const row of source.rows) {
    const product = byId.get(row.productId);
    assert.ok(product, row.item);
    const variant = product.variants.find(variant => variant.sourcePage === row.page && variant.sourceRow === row.row);
    assert.ok(variant, row.item);
    for (const [field, value] of Object.entries(row.variant)) assert.equal(variant[field], value, `${row.item}: ${field}`);
    assert.equal(product.specificationSource, source.id);
    const spec = product.specifications.find(spec => spec.label === variant.name);
    for (const field of ['dimensions', 'thickness', 'capacity', 'pack', 'notes']) {
      if (variant[field]) assert.ok(spec.value.includes(variant[field]), `${row.item}: missing ${field}`);
    }
  }
  assert.doesNotMatch(JSON.stringify(catalogue), /FOB Korea|unitPrice|EAN Code|3923\.21-0000/);
});

test('corrected measurements and supplier ambiguities retain their exact meanings', () => {
  assert.equal(byId.get('double-zipper-bags').variants[0].thickness, '60 μm');
  assert.equal(byId.get('double-zipper-bags').variants.length, 3);
  assert.equal(byId.get('cutting-boards').variants[1].dimensions, '0.9 cm x 20.7 cm x 33.5 cm');
  assert.equal(byId.get('food-storage-roll-bags').variants[2].dimensions, '27 cm x 37 cm');
  assert.equal(byId.get('disposable-gloves').variants[3].dimensions, '23.8 cm x 19.5 cm');
  assert.equal(byId.get('sugarcane-toothbrushes').variants.at(-1).pack, '20 pcs');
  assert.equal(byId.get('glass-airtight-containers').variants.length, 8);
  assert.equal(byId.has('recycled-cleaning-tools'), false);
  assert.equal(byId.has('sugarcane-a3-paper'), false);
  assert.equal(byId.get('sugarcane-copy-paper').variants.length, 2);
  const cleaningIds = ['household-squeegee', 'shoe-brush', 'desk-brush-dustpan-set', 'brush-squeegee-set', 'iron-handle-scrub-brush', 'bathroom-floor-brush', 'toilet-tpr-brush-set', 'toilet-plunger', 'rotating-head-broom-dustpan-set'];
  assert.equal(cleaningIds.reduce((count, id) => count + byId.get(id).variants.length, 0), 9);
  assert.equal(byId.get('reusable-drinking-straws').variants[0].dimensions, '21 cm long');
  assert.equal(byId.get('reusable-drinking-straws').variants[1].dimensions, '25 cm long');
  assert.doesNotMatch(JSON.stringify(byId.get('reusable-drinking-straws')), /unit not specified|without a unit/);
  assert.equal(byId.get('reusable-drinking-straws').variants[0].notes, 'Diameter: 6ø');
  assert.equal(byId.has('reusable-cups'), false);
  assert.equal(byId.get('ribbed-travel-tumbler').variants[0].dimensions, '9 cm x 9 cm x 18.5 cm');
  assert.equal(byId.get('ribbed-travel-tumbler').variants[0].pack, '1 pc');
  assert.equal(byId.has('recycled-hangers'), false);
  assert.equal(byId.get('sugarcane-hangers').variants.length, 5);
  assert.ok(byId.get('sugarcane-hangers').variants.every(variant => variant.pack === '5 pcs'));
  assert.equal(byId.has('grippy-cutting-board'), false);
  assert.equal(byId.has('solid-cutting-boards'), false);
  assert.equal(byId.get('cutting-boards').variants.length, 5);
  assert.ok(byId.get('cutting-boards').variants.every(variant => variant.pack === '1 pc'));
  const jumbo = byId.get('jumbo-tissue-rolls');
  assert.equal(jumbo.variants[0].pack, 'Per kg');
  assert.match(jumbo.variants[0].notes, /reel weight not specified/);
  assert.equal(jumbo.illustration, true);
  assert.match(byId.get('baby-tableware').variants.at(-1).notes, /dimensions not specified/);
});

test('manufacturer variants render in accessible website tables with all pack options', async () => {
  const page = createPageFixture();
  for (const file of ['catalogue-data.js', 'catalogue-utils.js', 'app.js']) {
    vm.runInNewContext(await readFile(new URL('assets/js/' + file, ROOT), 'utf8'), page.globals);
  }
  const escape = value => String(value).replaceAll('&', '&amp;').replaceAll("'", '&#39;');
  for (const product of catalogue.papers.filter(product => product.variants)) {
    page.location.hash = '#paper-' + product.id;
    page.window.listeners.hashchange[0]();
    const markup = page.get('detail-body').innerHTML;
    assert.match(markup, /<table class="variant-table">/);
    assert.match(markup, /<th scope="col">Dimensions \/ format<\/th>/);
    for (const variant of product.variants) {
      assert.ok(markup.includes(escape(variant.name)), product.id);
      assert.ok(markup.includes(escape(variant.pack)), product.id);
    }
  }
  page.location.hash = '#paper-reusable-cups';
  page.window.listeners.hashchange[0]();
  assert.match(page.get('detail-body').innerHTML, /Ribbed travel tumbler/);
  assert.match(page.get('detail-body').innerHTML, /9 cm x 9 cm x 18.5 cm/);

  page.location.hash = '#paper-recycled-hangers';
  page.window.listeners.hashchange[0]();
  assert.match(page.get('detail-body').innerHTML, /Clothes hangers/);
  assert.match(page.get('detail-body').innerHTML, /Sugarcane round/);
  assert.match(page.get('detail-body').innerHTML, /Recycled non-slip/);

  for (const legacyId of ['grippy-cutting-board', 'solid-cutting-boards']) {
    page.location.hash = '#paper-' + legacyId;
    page.window.listeners.hashchange[0]();
    assert.match(page.get('detail-body').innerHTML, /Standard - large/);
    assert.match(page.get('detail-body').innerHTML, /Grippy - large/);
    assert.match(page.get('detail-body').innerHTML, /Solid - medium/);
  }

  page.location.hash = '#paper-sugarcane-a3-paper';
  page.window.listeners.hashchange[0]();
  assert.match(page.get('detail-body').innerHTML, /Sugarcane office paper/);
  assert.match(page.get('detail-body').innerHTML, /A3 sheets/);
  assert.match(page.get('detail-body').innerHTML, /A4 sheets/);

  page.location.hash = '#paper-recycled-cleaning-tools';
  page.window.listeners.hashchange[0]();
  assert.equal(page.get('category-select').value, 'recycled-household');
  assert.match(page.get('results-count').textContent, /of 10 products/);

});
