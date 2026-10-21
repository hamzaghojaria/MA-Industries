import test from 'node:test';
import assert from 'node:assert/strict';
import { PAGE_META, syncPageMetadata, buildStructuredData } from '../scripts/site/seo.mjs';
import { loadCatalogue } from '../scripts/site/catalogue-markup.mjs';
import { readFile } from 'node:fs/promises';
import { ROOT } from '../scripts/site/config.mjs';

const catalogue = await loadCatalogue();
test('source metadata stays synchronized for every public page', async () => {
  for (const file of Object.keys(PAGE_META)) {
    const html = await readFile(new URL(file, ROOT), 'utf8');
    assert.equal(syncPageMetadata(html, file), html, file);
  }
});
test('metadata updates source and social descriptions together and escapes the brand', () => {
  const html = '<title>Old</title><meta name="description" content="Old"><meta property="og:title" content="Old"><meta name="twitter:description" content="Old">';
  const result = syncPageMetadata(html, 'index.html');
  assert.ok(result.includes('M&amp;A Industries'));
  assert.ok(!result.includes('Old'));
  assert.equal(syncPageMetadata(result, 'index.html'), result);
});
test('each canonical page has its correct type, identity, local contact and breadcrumbs', () => {
  for (const file of Object.keys(PAGE_META)) {
    const graph = buildStructuredData(file, catalogue, 'https://example.test/')['@graph'];
    const page = graph[1];
    assert.equal(page.name, PAGE_META[file].title);
    assert.equal(page.isPartOf['@id'], 'https://example.test/#website');
    assert.equal(graph[0].telephone, '+91 98191 57417');
    const breadcrumbs = graph.find(item => item['@type'] === 'BreadcrumbList');
    assert.equal(Boolean(breadcrumbs), file !== 'index.html');
    if (breadcrumbs) assert.equal(breadcrumbs.itemListElement[1].item, page.url);
    assert.ok(!JSON.stringify(graph).includes('maindustries.in/'), 'URLs follow the configured origin');
    assert.ok(!graph.some(item => item.offers || item.aggregateRating), 'No invented prices or reviews');
  }
});
test('catalogue schema retains all products and stable popup destinations', () => {
  const graph = buildStructuredData('products.html', catalogue, 'https://example.test/')['@graph'];
  const list = graph.find(item => item['@type'] === 'ItemList');
  assert.equal(list.numberOfItems, catalogue.papers.length);
  for (let i = 0; i < catalogue.papers.length; i++) {
    const product = catalogue.papers[i];
    assert.equal(list.itemListElement[i].url, `https://example.test/products.html?category=${product.group}#paper-${product.id}`);
  }
  assert.ok(graph.some(item => item['@type'] === 'DigitalDocument' && item.encodingFormat === 'application/pdf'));
});
