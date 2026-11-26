# Search and sharing metadata

Updated: 27 November 2026.

The static site has five canonical pages and 52 products across seven subcategories in two collections: 19 Cleaning & Hygiene products and 33 Sugarcane & Recycled products. Product details open from the shared catalogue; the site does not generate individual product pages.

## Implemented

- Page-specific titles and descriptions are maintained in `scripts/site/seo.mjs`. `npm run sync:metadata` writes matching HTML, Open Graph and X card metadata.
- All pages use a shared 1200 x 630 social image composed from the M&A logo and current sugarcane, recycled and cleaning product photos. Its alt text, dimensions and JPEG type are synchronized with each page.
- The production build applies absolute canonical, social-image and Open Graph URLs from `SITE_URL` (default `https://maindustries.in`), then generates a five-page sitemap and `robots.txt`.
- JSON-LD covers the organization, website, page type, sales contact, breadcrumbs, category/product lists and downloadable product catalogue. It uses the same configured public origin.
- Existing product and category links remain stable. Redirects in `render.yaml` map retired product URLs to their catalogue details.
- Product prices, stock guarantees, ratings, reviews and certifications are not invented. The enquiry catalogue does not claim merchant-listing eligibility.

## Verification and deployment

Run `npm run check`, `npm run build` and `npm run verify:build` before deployment. `npm run audit` reports asset references, exact duplicates and tracked generated files.

After deployment, submit `https://maindustries.in/sitemap.xml` in the verified Google Search Console property and inspect the five page URLs. Search Console access, live indexing, rankings and Core Web Vitals have not been measured from this workspace.

## Official guidance

- [Google Search Central: title links](https://developers.google.com/search/docs/appearance/title-link)
- [Google Search Central: snippets and meta descriptions](https://developers.google.com/search/docs/appearance/snippet)
- [Google Search Central: Organization structured data](https://developers.google.com/search/docs/appearance/structured-data/organization)
- [Google Search Central: sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
