/** Check every deployed HTML asset, page link and static anchor without network requests. */
import { access, readFile, readdir } from 'node:fs/promises';
import { ROOT, PAGES } from './config.mjs';
import { PAGE_META } from './seo.mjs';
import { escapeHtml } from './catalogue-markup.mjs';

const output = new URL('dist/', ROOT);
const files = (await readdir(output)).filter(file => file.endsWith('.html'));
if (files.length !== PAGES.length || files.some(file => !PAGES.includes(file))) {
  throw new Error('Deployment must contain every configured page; product details belong in popups');
}
const pages = new Map(await Promise.all(files.map(async file => [file, await readFile(new URL(file, output), 'utf8')])));
let links = 0;
const titles = new Set();
const descriptions = new Set();
const sitemap = await readFile(new URL('sitemap.xml', output), 'utf8');
const robots = await readFile(new URL('robots.txt', output), 'utf8');
const sitemapUrls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
if (sitemapUrls.length !== pages.size || new Set(sitemapUrls).size !== pages.size) {
  throw new Error('Sitemap must contain every page exactly once');
}
for (const [file, html] of pages) {
  const title = html.match(/<title>\s*([\s\S]*?)\s*<\/title>/)?.[1];
  const description = html.match(/<meta name="description" content="([^"]+)"/)?.[1];
  if (!title || titles.has(title)) throw new Error(`${file}: missing or duplicate title`);
  if (!description || descriptions.has(description)) throw new Error(`${file}: missing or duplicate description`);
  if (title !== escapeHtml(PAGE_META[file].title) || description !== escapeHtml(PAGE_META[file].description)) {
    throw new Error(`${file}: deployed metadata differs from the shared SEO configuration`);
  }
  titles.add(title);
  descriptions.add(description);
  if ([...html.matchAll(/<h1(?:\s[^>]*)?>/g)].length !== 1) throw new Error(`${file}: expected one main heading`);
  const canonicals = [...html.matchAll(/<link rel="canonical" href="([^"]+)"/g)];
  if (canonicals.length !== 1) throw new Error(`${file}: expected one canonical URL`);
  const canonical = new URL(canonicals[0][1]);
  if (canonical.pathname !== (file === 'index.html' ? '/' : `/${file}`) || canonical.search || canonical.hash) {
    throw new Error(`${file}: incorrect canonical URL`);
  }
  if (!sitemapUrls.includes(canonical.href)) throw new Error(`${file}: canonical absent from sitemap`);
  if (!robots.includes(`Sitemap: ${canonical.origin}/sitemap.xml`)) throw new Error('robots.txt sitemap origin differs from canonical');
  if (!html.includes(`<meta property="og:url" content="${canonical.href}">`)) throw new Error(`${file}: social URL differs from canonical`);
  const shareImage = html.match(/<meta property="og:image" content="([^"]+)"/)?.[1];
  if (!shareImage || !shareImage.startsWith(canonical.origin + '/')) throw new Error(`${file}: missing absolute share image`);
  await access(new URL(new URL(shareImage).pathname.slice(1), output));
  if (!html.includes('max-image-preview:large')) throw new Error(`${file}: missing image preview directive`);
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
  if (ids.length !== new Set(ids).size) throw new Error(`${file}: duplicate element ID`);
  for (const [, raw] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const value = raw.replaceAll('&amp;', '&');
    if (/^(?:https?:|mailto:|tel:|data:)/.test(value)) continue;
    const url = new URL(value, `https://local.test/${file}`);
    const path = decodeURIComponent(url.pathname.slice(1)) || 'index.html';
    await access(new URL(path, output)).catch(() => { throw new Error(`${file}: missing local target ${value}`); });
    // Product hashes are rendered by app.js; static section hashes must exist in HTML.
    if (url.hash && !url.hash.startsWith('#paper-') && pages.has(path)) {
      const id = decodeURIComponent(url.hash.slice(1));
      if (id && !pages.get(path).includes(`id="${id}"`)) throw new Error(`${file}: missing anchor ${value}`);
    }
    links++;
  }
  const schemas = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  if (schemas.length !== 1) throw new Error(`${file}: expected one structured-data graph`);
  const graph = JSON.parse(schemas[0][1])['@graph'];
  const pageSchema = graph.find(item => item['@id'] === canonical.href + '#webpage');
  if (!pageSchema || pageSchema.url !== canonical.href) throw new Error(`${file}: structured-data page identity differs from canonical`);
  const graphIds = graph.map(item => item['@id']);
  if (new Set(graphIds).size !== graphIds.length) throw new Error(`${file}: duplicate structured-data identity`);
  for (const id of graphIds) {
    if (!id.startsWith(canonical.origin + '/')) throw new Error(`${file}: structured-data identity uses another origin`);
  }
  if (file !== 'index.html' && !graph.some(item => item['@type'] === 'BreadcrumbList')) throw new Error(`${file}: missing breadcrumbs`);
  const organization = graph.find(item => item['@type'] === 'Organization');
  if (organization?.telephone !== '+91 98191 57417') throw new Error(`${file}: stale organization contact`);
  // Responsive candidates are separate resources, not covered by src/href checks.
  for (const [, candidates] of html.matchAll(/\bsrcset="([^"]+)"/g)) {
    for (const candidate of candidates.split(',')) {
      const path = candidate.trim().split(/\s+/)[0];
      await access(new URL(path, output)).catch(() => { throw new Error(`${file}: missing responsive image ${path}`); });
    }
  }
}
const css = await readFile(new URL('assets/css/style.css', output), 'utf8');
if (/fonts\.(?:googleapis|gstatic)\.com/.test(css)) throw new Error('Deployment CSS contains third-party font requests');
for (const [, path] of css.matchAll(/url\(['"]?(\.\.\/fonts\/[^)'"\s]+)['"]?\)/g)) {
  await access(new URL(path, new URL('assets/css/', output)));
}
if (/@import\s+url\(['"](?!https?:)/.test(css)) throw new Error('Deployment CSS contains unbundled local imports');
console.log(`Verified ${files.length} deployed pages, ${links} local links/assets and structured data.`);
