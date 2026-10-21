# Code, folders, catalogue and SEO audit

21 October 2026. This records changes completed in the local workspace.

## Catalogue

The 34-page PDF has 31 product pages plus cover, directory and contact pages. All 43 published specification rows from 15 products are copied from assets/js/catalogue-data.js. They include dimensions, thickness, pack counts, weight and formats where the website supplies them. Products without published measurements retain an enquiry note. The PDF checks each row against text extracted from its own product page and checks product enquiry URLs, page count, logo presence and text bounds. All pages were rendered and reviewed, including the six-variant sanitary bags and micrometre symbols.

The browser edition uses the same data and specification rows. Its 31 embedded images, specification coverage, script syntax and next/previous/selector boundary behavior were checked. This was a scripted navigation check, not a full browser rendering audit.

Embedded-image optimization reduced the specification-bearing PDF from 17,755,257 bytes to 3,937,032 bytes (about 78% smaller). Source images are preserved. The published PDF path is unchanged and the refreshed file is included in dist/.

## Cleanup and maintenance

| Completed change | Reason |
| --- | --- |
| Removed 25 unused legacy gallery assets, the old share graphic and 3 disposable card renders | No active manifest/site references; 1,820,852 bytes removed |
| Removed create-range-catalogue.py | Superseded multi-product-per-page generator; the catalogue command now uses the focused generator |
| Archived four superseded logo/product originals under scripts/references/legacy-images/ | Keeps inactive source artwork out of the website asset folders without losing it |
| Extracted browser_catalogue.py and interactive.html | Browser markup and CSS no longer sit inside the PDF layout generator |
| Added catalogue_images.py | One cached conversion shared by PDF and browser output |
| Reused loadCatalogue and escapeHtml helpers | Removed duplicate data-loading and escaping implementations |
| Removed studio.js from Contact | That page has no material studio or pointer-effect targets |
| Limited responsive gallery generation to recycling photos | Prevents obsolete derivatives from returning |
| Added npm run audit and dependency documentation | Repeatable read-only inventory and authoring setup |
| Replaced contradictory SEO/performance notes | Documentation now matches the five-page build |

Reference artwork, original product photos, final visiting cards and other user deliverables are retained. The ignored .uv-cache/, .uv-python/ and tmp/pdf-venv/ provide the local authoring runtime; they are not deployed. Reference images still tracked under tmp/pdfs/ were retained as source artwork rather than deleted as disposable output. No unrelated user PDFs were modified.

The deployed website remains a small static site with no frontend package dependencies. Existing CSS modules, responsive images, local fonts, progressive motion, popup navigation and enquiry behavior are retained. A framework migration or broad speculative rewrite would not improve this task.

## SEO

All five source pages now have synchronized, page-specific titles and descriptions across search and social metadata. scripts/site/seo.mjs owns metadata and structured data. The generated graph contains Organization, WebSite, page-specific schema, sales ContactPoint, BreadcrumbList and relevant ItemList/DigitalDocument entries. IDs use the configured origin. The current phone is consistent across the graph. No prices, reviews, stock levels or certifications were fabricated.

Canonicals, the five-page sitemap, robots.txt, responsive image URLs and font assets are verified in the production build. Existing product popup destinations and retired-product redirects are preserved. Added /index.html to / redirect configuration. Product information and supplied specifications remain available in the no-JavaScript fallback.

See SEO-PLAN.md for official guidance and deployment steps. Changes are local: production deployment, Render route synchronization, Search Console submission, live indexing and real-user performance measurements remain outstanding.

## Final validation

- 41 regression tests passed.
- All 7 browser scripts passed syntax checks.
- Catalogue counts/labels and all five source metadata sets are synchronized.
- Production build: 5 HTML pages, 252 allowlisted public assets.
- Deployment verifier: 305 local links/assets checked, with canonical/sitemap consistency, structured-data identities, current contact, breadcrumbs, responsive candidates and local fonts verified.
- PDF: 34 pages, 31 products, all 43 specification rows verified against source data and rendered for inspection.
