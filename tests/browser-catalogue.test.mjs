import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { ROOT, loadCatalogue } from '../scripts/site/catalogue-markup.mjs';

const template = await readFile(new URL('../scripts/catalogue/interactive.html', import.meta.url), 'utf8');
const script = template.match(/<script>([\s\S]*?)<\/script>/)[1];

test('portable catalogue navigation clamps endpoints and supports selector and keyboard input', () => {
  const slides = Array.from({length: 34}, () => ({ active: false, classList: { toggle(name, active) { this.active = active; } }, setAttribute() {} }));
  const elements = Object.fromEntries(['jump', 'prev', 'next', 'count', 'progress'].map(id => [id, {style: {}, value: '', disabled: false}]));
  let keydown;
  const context = vm.createContext({document: {
    querySelectorAll: () => slides,
    querySelector: selector => elements[selector.slice(1)],
    addEventListener: (type, callback) => { if (type === 'keydown') keydown = callback; }
  }});
  vm.runInContext(script, context);
  assert.equal(elements.prev.disabled, true);
  assert.equal(elements.count.textContent, '01 / 34');
  elements.next.onclick();
  assert.equal(elements.count.textContent, '02 / 34');
  elements.jump.value = '33'; elements.jump.onchange();
  assert.equal(elements.next.disabled, true);
  assert.equal(elements.count.textContent, '34 / 34');
  assert.equal(slides.filter(slide => !slide.inert).length, 1);
  keydown({key: 'ArrowRight', target: {tagName: 'BODY'}, preventDefault() {}});
  assert.equal(elements.count.textContent, '34 / 34');
  keydown({key: 'ArrowLeft', target: {tagName: 'BODY'}, preventDefault() {}});
  assert.equal(elements.count.textContent, '33 / 34');
  keydown({key: 'ArrowLeft', target: {tagName: 'SELECT'}});
  assert.equal(elements.count.textContent, '33 / 34');
  elements.jump.value = '-10'; elements.jump.onchange();
  assert.equal(elements.count.textContent, '01 / 34');
});

// Saved catalogues are reviewed releases; website edits may proceed while catalogue updates are deferred.
test('saved portable catalogue has consistent slides, images, selector entries and variant tables', async () => {
  const output = await readFile(new URL('output/pdf/MA-Industries-Interactive-Catalogue.html', ROOT), 'utf8');
  const slides = [...output.matchAll(/<section class="slide" aria-label="([^"]+)">([\s\S]*?)<\/section>/g)];
  const options = [...output.matchAll(/<option value="(\d+)">([\s\S]*?)<\/option>/g)];
  const current = await loadCatalogue();
  assert.equal(slides.length, current.papers.length);
  for (const product of current.papers) {
    const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
    assert.ok(output.includes(escape(product.overview || product.desc)), product.id);
  }
  assert.doesNotMatch(output, /<figcaption>|Illustrative product image|Product image for reference/);
  assert.equal(options.length, slides.length);
  assert.equal([...output.matchAll(/<img src="data:image\/(?:jpeg|png);base64,/g)].length, slides.length);
  assert.equal([...output.matchAll(/<th scope="row">/g)].length, 85);
  slides.forEach((slide, index) => {
    assert.equal(Number(options[index][1]), index);
    assert.equal(options[index][2], slide[1]);
    assert.ok(slide[2].includes('<h1>' + slide[1] + '</h1>'));
    assert.match(slide[2], /class="cta" href="https:\/\/wa\.me\//);
  });
  assert.doesNotMatch(output, /FOB Korea|EAN Code|3923\.21-0000/);
});
