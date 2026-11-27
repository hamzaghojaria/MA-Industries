/** Keep deployed category labels/counts tied to catalogue data. */
import { readFile, writeFile } from 'node:fs/promises';
import { runInNewContext } from 'node:vm';
import { pathToFileURL } from 'node:url';
import { ROOT, PAGES } from './config.mjs';

export { ROOT, PAGES };
export const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

export async function loadCatalogue() {
  const context = { window: {} };
  runInNewContext(await readFile(new URL('assets/js/catalogue-data.js', ROOT), 'utf8'), context);
  return context.window.MACatalogueData;
}

export function syncCatalogueMarkup(html, { papers, categories }) {
  const newline = html.includes('\r\n') ? '\r\n' : '\n';
  const counts = new Map(categories.map(category => [category.id, 0]));
  for (const product of papers) counts.set(product.group, counts.get(product.group) + 1);
  const count = id => counts.get(id);
  const collections = [
    { id: 'clean-republic', name: 'Cleaning & Hygiene', className: 'directory-clean-republic', description: 'Find considered cleaning essentials for home routines, shared washrooms and commercial spaces.', cover: 'assets/images/responsive/products/clean-republic-pine-floor-cleaner-320.webp' },
    { id: 'sugarcane-recycled', name: 'Sugarcane & Recycled', className: 'directory-green', description: 'Set the table, pack the next portion or make more of a cupboard. Compare sugarcane products, paper formats and recycled household essentials by the job they need to do.', cover: 'assets/images/ranges/sugarcane-kitchenware-photo.jpg' }
  ];
  const groups = collections.map(collection => ({
    ...collection,
    categories: categories.filter(category => category.collection === collection.id)
  }));
  const folder = 'assets/images/ranges/';
  const catalogueImage = category => {
    if (category.collection === 'sugarcane-recycled') return folder + category.id + '-photo.jpg';
    const featured = papers.find(product => product.group === category.id);
    return featured?.cardImage || featured?.image;
  };
  // Own the entire grouped control so desktop order cannot drift from mobile/data.
  html = html.replace(/(<aside class="catalogue-sidebar"[^>]*>)[\s\S]*?(<\/aside>)/,
    (_, start, end) => start + '<div class="category-desktop"><h2>Browse categories</h2>' +
      `<button type="button" class="category-all active" data-filter="all">Show all products <small>${papers.length}</small></button>` +
      groups.map(group => `<div class="category-group"><h3>${escapeHtml(group.name)}</h3>` +
        group.categories.map(category => `<button type="button" data-filter="${category.id}"><span>${escapeHtml(category.name)}</span><small>${count(category.id)}</small></button>`).join('') + '</div>').join('') + '</div>' + end);
  // IDs stay stable: URLs and product deep links continue to resolve.
  html = html.replace(/(<select\b[^>]*id="category-select"[^>]*>)[\s\S]*?(<\/select>)/,
    (_, start, end) => start + newline + [
      `              <option value="all">All products (${papers.length})</option>`,
      ...groups.flatMap(group => group.categories).map(category => `              <option value="${category.id}">${escapeHtml(category.name)} (${count(category.id)})</option>`)
    ].join(newline) + newline + '            ' + end);
  const productCount = total => total === 1 ? '1 product' : total + ' products';
  const gateways = groups.map(group => {
    const total = group.categories.reduce((sum, category) => sum + count(category.id), 0);
    return [
      '<a class="collection-jump" href="#' + group.id + '">',
      '<img class="collection-jump-image" src="' + group.cover + '" alt="" width="320" height="320">',
      '<span class="collection-jump-copy"><strong>' + escapeHtml(group.name) + '</strong>',
      '<span class="collection-jump-count">' + productCount(total) + ' &middot; ' + group.categories.length + ' categories</span></span>',
      '<span class="collection-jump-arrow" aria-hidden="true">&#8595;</span></a>'
    ].join('');
  }).join(newline + '        ');
  html = html.replace(/(<div class="directory-jumps"[^>]*>)[\s\S]*?(<\/div>)/,
    (_, start, end) => start + newline + '        ' + gateways + newline + '      ' + end);

  const sections = groups.map(group => {
    const cards = group.categories.map(category => {
      const image = catalogueImage(category);
      return [
        '<a class="directory-card" href="products.html?category=' + category.id + '#collection">',
        image ? '<div class="directory-image"><span class="watermarked-image"><img src="' + escapeHtml(image) + '" alt="" width="640" height="640" loading="lazy" decoding="async"></span></div>' : '',
        '<div class="directory-copy"><span class="directory-count">' + productCount(count(category.id)) + '</span>',
        '<h3><span class="directory-title">' + escapeHtml(category.name) + '</span><span class="directory-arrow" aria-hidden="true">&#8599;</span></h3>',
        '<p class="directory-card-lead"><em>' + escapeHtml(category.line) + '</em></p>',
        '<p>' + escapeHtml(category.desc) + '</p></div></a>'
      ].join('');
    }).join(newline + '        ');
    return [
      '<section class="directory-section ' + group.className + '" id="' + group.id + '" aria-labelledby="' + group.id + '-title">',
      '      <div class="section-heading"><h2 id="' + group.id + '-title">' + escapeHtml(group.name) + '</h2><p>' + escapeHtml(group.description) + '</p><a class="button collection-download" href="assets/catalogues/MA-Industries-' + (group.id === 'clean-republic' ? 'Cleaning-Hygiene' : 'Sugarcane-Recycled') + '-Catalogue.pdf" download>Download category catalogue <span aria-hidden="true">↓</span></a></div>',
      '      <div class="directory-grid">',
      '        ' + cards,
      '      </div>',
      '    </section>'
    ].join(newline);
  });
  html = html.replace(/\s*<section class="directory-section[^>]*>[\s\S]*?(?=<section class="about-section about-cta category-cta">)/,
    newline + '    ' + sections.join(newline + '    ') + newline + '    ');
  return html;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const catalogue = await loadCatalogue();
  const write = process.argv.includes('--write');
  let stale = 0;
  for (const page of PAGES) {
    const url = new URL(page, ROOT);
    const before = await readFile(url, 'utf8');
    const after = syncCatalogueMarkup(before, catalogue);
    if (before !== after) {
      stale++;
      if (write) await writeFile(url, after);
      else console.error(`${page}: catalogue labels/counts are stale; run npm run sync:catalogue`);
    }
  }
  if (stale && !write) process.exitCode = 1;
  else console.log(write ? `Synchronized ${stale} source pages.` : 'Catalogue page labels and counts are synchronized.');
}
