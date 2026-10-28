# Search setup and maintenance

Updated: 28 October 2026.

The website has five canonical pages: Home, About, Categories, Products and Contact. All 33 products remain in the existing catalogue with stable popup links. No standalone product or category-guide pages are generated.

## Implemented

- Unique page titles and descriptions, with matching Open Graph and Twitter text, live in scripts/site/seo.mjs. Run npm run sync:metadata after editing them; npm run check detects stale source metadata.
- The production build emits absolute canonical and sharing URLs using SITE_URL (default https://maindustries.in), a five-page sitemap and robots.txt.
- Organization, WebSite, page-specific types, sales ContactPoint, BreadcrumbList and category/product ItemList schema use the current content and Maaz's +91 98191 57417 number. Home and Products also describe the downloadable sugarcane/recycled PDF as a DigitalDocument.
- The homepage title and description identify Mumbai supplier and bulk-order intent. Photos have existing alternative text and responsive candidates; decorative images remain decorative.
- Render redirects /index.html to /. Existing exact redirects preserve retired product URLs and open the matching catalogue popup.
- Product prices, stock guarantees, ratings, reviews and certifications are not invented. This enquiry catalogue does not claim Google shopping rich-result eligibility.

## Verification and deployment

Run npm run validate. It checks browser syntax, source synchronization, regression tests, the clean production build, page links, canonical/sitemap agreement, structured data, local fonts and responsive image candidates.

Deploy dist/ and apply render.yaml route changes. After deployment, submit https://maindustries.in/sitemap.xml in the verified Google Search Console property and inspect all five page URLs. Search Console access and production deployment were not performed in this workspace task. Live indexing, rankings and Core Web Vitals have not been measured for this build.

## Official guidance used

- [Google's developer SEO guide](https://developers.google.com/search/docs/fundamentals/get-started-developers): crawlable links and accessible content.
- [Canonical URL guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls): consistent canonical signals.
- [Sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap): canonical sitemap entries.
- [Product snippet requirements](https://developers.google.com/search/docs/appearance/structured-data/product-snippet): no fabricated prices or reviews to obtain rich results.
