/** Shared search metadata and structured data for the five canonical pages. */
import { escapeHtml } from './catalogue-markup.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { ROOT } from './config.mjs';

export const PAGE_META = {
  'index.html': {
    title: 'Sugarcane, Recycled & Cleaning Products | M&A Industries',
    description: 'Find sugarcane tableware, food packaging, paper, recycled household essentials and M&A cleaning products from M&A Industries in Mumbai.'
  },
  'about.html': {
    title: 'About M&A Industries | Product Sourcing, Mumbai',
    description: 'Meet the Mumbai team behind M&A Industries and see how we help businesses compare materials, product formats and pack sizes.'
  },
  'categories.html': {
    title: 'Product Collections | M&A Industries',
    description: 'Browse two collections from M&A Industries. Explore M&A cleaning and hygiene essentials or sugarcane and recycled essentials.'
  },
  'products.html': {
    title: 'Product Catalogue | M&A Industries',
    description: 'Compare uses, dimensions and pack options for sugarcane essentials, recycled household goods and M&A cleaning products.'
  },
  'contact.html': {
    title: 'Contact M&A Industries, Mumbai | Product & Bulk Enquiries',
    description: 'Contact M&A Industries in Mumbai on +91 98191 57417 to discuss product options, pack sizes, pricing or bulk supply.'
  }
};

export function syncPageMetadata(html, file) {
  const { title, description } = PAGE_META[file];
  return html.replace(/<title>[\s\S]*?<\/title>/, `<title>${escapeHtml(title)}</title>`)
    .replace(/(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*(")/g, `$1${escapeHtml(title)}$2`)
    .replace(/(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*(")/g, `$1${escapeHtml(description)}$2`);
}

export function buildStructuredData(file, catalogue, origin) {
  const base = new URL('/', origin);
  const url = new URL(file === 'index.html' ? '' : file, base).href;
  const { title, description } = PAGE_META[file];
  const organizationId = new URL('#organization', base).href;
  const websiteId = new URL('#website', base).href;
  const contactId = new URL('#sales-contact', base).href;
  const documentUrl = new URL('assets/catalogues/MA-Industries-Catalogue.pdf', base).href;
  const page = {
    '@type': file === 'contact.html' ? 'ContactPage' : file === 'about.html' ? 'AboutPage' :
      ['products.html', 'categories.html'].includes(file) ? 'CollectionPage' : 'WebPage',
    '@id': url + '#webpage', url, name: title, description, inLanguage: 'en-IN',
    publisher: { '@id': organizationId }, isPartOf: { '@id': websiteId },
    primaryImageOfPage: { '@type': 'ImageObject', url: new URL('assets/images/share-preview-sugarcane.jpg', base).href, width: 1200, height: 630 }
  };
  const graph = [{
    '@type': 'Organization', '@id': organizationId, name: 'M&A Industries', url: base.href,
    logo: new URL('assets/images/brand-logo.png', base).href,
    email: 'info@maindustries.in', telephone: '+91 98191 57417',
    address: { '@type': 'PostalAddress', addressLocality: 'Mumbai', addressCountry: 'IN' },
    description: 'Mumbai supplier of sugarcane essentials, recycled household goods and M&A cleaning products.',
    knowsAbout: catalogue.categories.map(category => category.name),
    contactPoint: { '@id': contactId }
  }, page, {
    '@type': 'WebSite', '@id': websiteId, url: base.href, name: 'M&A Industries',
    inLanguage: 'en-IN', publisher: { '@id': organizationId }
  }, {
    '@type': 'ContactPoint', '@id': contactId, contactType: 'sales',
    telephone: '+91 98191 57417', email: 'info@maindustries.in',
    url: new URL('contact.html', base).href
  }];
  if (file !== 'index.html') {
    const labels = { 'about.html': 'About us', 'categories.html': 'Product categories', 'products.html': 'Product catalogue', 'contact.html': 'Contact us' };
    page.breadcrumb = { '@id': url + '#breadcrumb' };
    graph.push({ '@type': 'BreadcrumbList', '@id': url + '#breadcrumb', itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: base.href },
      { '@type': 'ListItem', position: 2, name: labels[file], item: url }
    ] });
  }
  if (file === 'contact.html') page.mainEntity = { '@id': contactId };
  if (file === 'categories.html' || file === 'products.html') {
    const categories = file === 'categories.html';
    const entries = categories ? catalogue.categories : catalogue.papers;
    page.mainEntity = { '@id': url + '#catalogue' };
    graph.push({ '@type': 'ItemList', '@id': url + '#catalogue',
      name: categories ? 'Product categories' : 'M&A Industries product catalogue',
      numberOfItems: entries.length,
      itemListElement: entries.map((item, index) => ({ '@type': 'ListItem', position: index + 1,
        name: item.name, description: item.desc,
        url: new URL(categories ? `products.html?category=${item.id}#collection` :
          `products.html?category=${item.group}#paper-${item.id}`, base).href
      })) });
  }
  if (file === 'index.html' || file === 'products.html') {
    page.subjectOf = { '@id': documentUrl };
    graph.push({ '@type': 'DigitalDocument', '@id': documentUrl, url: documentUrl,
      name: 'M&A Industries Sugarcane & Recycled Product Catalogue',
      description: 'Product photographs and available product information for sugarcane, recycled and M&amp;A cleaning ranges.',
      encodingFormat: 'application/pdf', inLanguage: 'en-IN', publisher: { '@id': organizationId }
    });
  }
  return { '@context': 'https://schema.org', '@graph': graph };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let stale = 0;
  for (const file of Object.keys(PAGE_META)) {
    const path = new URL(file, ROOT);
    const before = await readFile(path, 'utf8');
    const after = syncPageMetadata(before, file);
    if (before === after) continue;
    stale++;
    if (process.argv.includes('--write')) await writeFile(path, after);
    else console.error(`${file}: stale metadata; run npm run sync:metadata`);
  }
  if (stale && !process.argv.includes('--write')) process.exitCode = 1;
  else console.log(`SEO metadata synchronized across ${Object.keys(PAGE_META).length} pages.`);
}
