> Historical audit: cleanup recommendations below were completed. See [current maintenance status](maintenance-status.md) and [cleanup completion](cleanup-completion.md). Old counts and folder sizes describe the earlier snapshot.

# Final website directory review

25 October 2026. Read-only audit of the current website, build, authoring files and local folders, plus the requested tumbler packaging-colour update.

## Result

- Website: 33 product cards in 4 categories. All 85 manufacturer variants remain mapped to current cards.
- All 46 regression tests pass. Seven browser scripts pass syntax checks. Website markup and metadata are synchronized.
- Production build passes checks for five pages, 251 local links/assets, responsive image paths, sitemap/canonical consistency and structured data.
- No missing required website asset or broken current internal link was found by these checks.
- Tumbler carton illustration now uses cream stock and lavender colour blocks matching the zipper-bag and cling-wrap packaging. Cup colours and specifications are unchanged.
- Both saved catalogues remain unchanged, per the requested hold.

## Remaining content / release work

| Priority | Finding | Recommended action |
| --- | --- | --- |
| High | The saved catalogue has 34 product families; the website has 33, with multiple merges, removals and nine separately listed cleaning products. Several saved product links/names are obsolete. | Regenerate and visually review the PDF and browser catalogue when catalogue work is explicitly resumed. |
| High | Intended website changes are uncommitted and several new images, the renamed public PDF, source records and tests are untracked. | Include all intended source/assets in the Git commit before a deployment from Git. |
| Medium | Plates, Sugarcane bowls and Sugarcane paper rolls have no manufacturer variant dimensions or pack quantities in the supplied quotation. | Keep their enquiry notes until the manufacturer supplies those details; do not invent values. |
| Medium | The source lists straw diameter as 6ø without a unit. Its on-site warning was removed at your request. | Confirm the diameter unit privately before preparing a client specification. No unit was guessed. |
| Medium | Instagram and LinkedIn are still disabled “coming soon” placeholders; the Industries Google Business Profile action is also inactive. | Supply the real URLs when these profiles are ready, or retain the disabled controls intentionally. |
| Low | SEO-PLAN.md and older audit/performance notes include previous product totals and build-size claims. | Update maintenance notes after the final cleanup and catalogue refresh. |

The supplier image/packaging edits are illustrative. The lavender tumbler carton is a visual mock-up of the requested palette; confirm actual supplied printing if a client needs an exact packaging colour.

## Unnecessary files still copied into the website build

The current allowlists publish **41 old product images/derivatives, totaling 1.78 MB**, with no reference from the current HTML, JavaScript image choices or current product data. They are residual photographs replaced by the newer packaging artwork, or retired individual cards merged into a single card. This increases deployment size; it is not a claim that visitors download all those files on every page.

Recommended cleanup order:

1. Remove these inactive originals from scripts/site/manifests/product-images.json.
2. Remove their responsive-image entries from scripts/site/manifests/responsive-images.json.
3. Preserve useful manufacturer/reference originals under scripts/references/ before deleting any source artwork. Generated responsive copies can be recreated.
4. Rebuild dist/ and run the existing checks.

Keep assets/fonts/dm-sans-OFL.txt and assets/fonts/playfair-display-OFL.txt. They are font-license files, not disposable unused content.

| Candidate image path | Size |
| --- | ---: |
| `assets/images/products/disposable-gloves-photo.jpg` | 109.3 KB |
| `assets/images/products/double-zipper-bags-photo.jpg` | 132.9 KB |
| `assets/images/products/easy-cut-cling-wraps-photo.jpg` | 89.6 KB |
| `assets/images/products/food-storage-pop-up-bags-photo.jpg` | 79.8 KB |
| `assets/images/products/food-storage-roll-bags-photo.jpg` | 84.4 KB |
| `assets/images/products/grippy-cutting-board-photo.webp` | 106.4 KB |
| `assets/images/products/recycled-cleaning-tools-photo.webp` | 186.3 KB |
| `assets/images/products/recycled-hangers-photo.webp` | 97.6 KB |
| `assets/images/products/solid-cutting-boards.webp` | 33.2 KB |
| `assets/images/products/sugarcane-a3-paper-photo.webp` | 65.7 KB |
| `assets/images/products/sugarcane-bath-tissues-photo.jpg` | 115.2 KB |
| `assets/images/products/sugarcane-packaging-paper-photo.jpg` | 112.0 KB |
| `assets/images/products/sugarcane-paper-cups-photo.jpg` | 64.4 KB |
| `assets/images/products/sugarcane-soup-bowls-photo.jpg` | 87.8 KB |
| `assets/images/responsive/products/disposable-gloves-photo-320.webp` | 5.7 KB |
| `assets/images/responsive/products/disposable-gloves-photo-640.webp` | 18.4 KB |
| `assets/images/responsive/products/disposable-gloves-photo-960.webp` | 36.6 KB |
| `assets/images/responsive/products/double-zipper-bags-photo-320.webp` | 5.0 KB |
| `assets/images/responsive/products/double-zipper-bags-photo-640.webp` | 13.3 KB |
| `assets/images/responsive/products/double-zipper-bags-photo-960.webp` | 24.4 KB |
| `assets/images/responsive/products/easy-cut-cling-wraps-photo-320.webp` | 4.8 KB |
| `assets/images/responsive/products/easy-cut-cling-wraps-photo-640.webp` | 14.7 KB |
| `assets/images/responsive/products/easy-cut-cling-wraps-photo-960.webp` | 28.0 KB |
| `assets/images/responsive/products/food-storage-pop-up-bags-photo-320.webp` | 3.4 KB |
| `assets/images/responsive/products/food-storage-pop-up-bags-photo-640.webp` | 10.2 KB |
| `assets/images/responsive/products/food-storage-pop-up-bags-photo-960.webp` | 19.6 KB |
| `assets/images/responsive/products/food-storage-roll-bags-photo-320.webp` | 4.2 KB |
| `assets/images/responsive/products/food-storage-roll-bags-photo-640.webp` | 12.3 KB |
| `assets/images/responsive/products/food-storage-roll-bags-photo-960.webp` | 24.6 KB |
| `assets/images/responsive/products/sugarcane-bath-tissues-photo-320.webp` | 5.5 KB |
| `assets/images/responsive/products/sugarcane-bath-tissues-photo-640.webp` | 21.4 KB |
| `assets/images/responsive/products/sugarcane-bath-tissues-photo-960.webp` | 42.8 KB |
| `assets/images/responsive/products/sugarcane-packaging-paper-photo-320.webp` | 3.7 KB |
| `assets/images/responsive/products/sugarcane-packaging-paper-photo-640.webp` | 16.1 KB |
| `assets/images/responsive/products/sugarcane-packaging-paper-photo-960.webp` | 41.7 KB |
| `assets/images/responsive/products/sugarcane-paper-cups-photo-320.webp` | 2.3 KB |
| `assets/images/responsive/products/sugarcane-paper-cups-photo-640.webp` | 6.2 KB |
| `assets/images/responsive/products/sugarcane-paper-cups-photo-960.webp` | 12.1 KB |
| `assets/images/responsive/products/sugarcane-soup-bowls-photo-320.webp` | 3.4 KB |
| `assets/images/responsive/products/sugarcane-soup-bowls-photo-640.webp` | 10.3 KB |
| `assets/images/responsive/products/sugarcane-soup-bowls-photo-960.webp` | 22.6 KB |

## Code and authoring helpers

- Static selector inspection found **40 CSS class candidates** with no literal use in the five pages or six runtime controller/helper scripts. These are candidates, not a guaranteed deletion count: state classes, dynamic selectors and shared selector blocks require review. Focus first on legacy artwork/category styles such as `.art-grid`, `.paper-object`, `.sample-row`, `.category-grid`, `.category-swatch` and `.home-categories` in assets/css/shared.css.
- Keep the current runtime modules (catalogue data/helpers, app, gallery, navigation, experience and studio), build/SEO/verification scripts, fonts, current images and tests. They are used by the current workflow.
- scripts/site/audit.mjs has a limitation: it counts a path mentioned in a manifest as a reference. It reports zero unreferenced assets even when the manifest itself is stale. The list above uses actual page/runtime/product usage instead.
- scripts/images/optimize-product-images.py is a legacy PNG-import helper. Its tmp/product-images/ source is currently empty, so it is not part of the active build; archive/remove it only if that PNG-import workflow is no longer needed.
- scripts/catalogue/create-quotation.py and quotation_source.py are for an older XLSX quotation workflow, separate from the current catalogue generator. Their default external XLSX path does not exist on this machine. Keep them only if needed with an explicit valid --source path; they are not required for website deployment.
- scripts/catalogue/create-catalogue.mjs, create-focused-catalogue.py, browser_catalogue.py, interactive.html, catalogue_images.py and requirements.txt are still required to produce the final catalogues. Keep them.
- scripts/cards/create-visiting-card.py is not needed by the hosted website, but is needed to reproduce visiting cards. Keep it if future card edits are expected.

### CSS review candidates by file

- `catalogue.css`: `.catalogue-note`
- `footer.css`: `.social-coming-soon`, `.footer-link-group`
- `motion.css`: `.collection-scroll-hint`, `.reveal`
- `ranges.css`: `.range-image-caption`, `.offering-intro`, `.product-gsm`, `.about-offerings`, `.product-image-note`, `.directory-note`, `.detail-gsm`, `.feature`
- `shared.css`: `.art-grid`, `.s1`, `.s2`, `.s3`, `.s4`, `.s5`, `.art-caption`, `.circle-label`, `.paper-object`, `.feature`, `.sample-row`, `.category-grid`, `.category-swatch`, `.detail-section-title`, `.reveal`, `.is-visible`, `.home-categories`, `.image-note`, `.footer-links`, `.category-photo-box`, `.category-photo`, `.about-hero-image`, `.product-gsm`, `.detail-gsm`, `.social-icon`, `.footer-link-group`, `.nav-products`

## Folder recommendations

| Folder | Measured size | Recommendation |
| --- | ---: | --- |
| `.uv-cache/` | 330.36 MB | Download/package cache. Removable if the extra disk space is wanted; not deployed. |
| `.uv-python/` | 127.63 MB | Keep while using the current PDF tools. tmp/pdf-venv/ explicitly points to this Python installation. |
| `tmp/` | 206.75 MB | Mixed temporary renders, browser profiles, source references and the PDF environment. Clean selectively; do not remove the whole folder before preserving tracked reference inputs and the PDF environment. |
| `dist/` | 13.16 MB | Generated deployment output. Rebuildable with the build command; do not edit it as source. |
| `output/` | 14.42 MB | User deliverables and audit reports. Keep the final visiting cards, quotation PDFs and saved catalogues. Previews can be regenerated, but may be useful for review. |
| `scripts/` | 7.19 MB | Build/authoring tools and reference artwork. Not deployed. Keep current generators and evidence-backed manufacturer records. |
| `assets/` | 13.03 MB | Current website assets plus the old image candidates listed above. Keep active images, fonts, licenses and the public PDF. |
| `.git/` | 229.91 MB | Repository history. Keep it; not a cleanup target. |

### Temporary subfolders

| Folder | Size | Recommendation |
| --- | ---: | --- |
| `tmp/card-deps/` | 0.00 MB | Empty/placeholder helper folder; can be removed if not reusing its import workflow. |
| `tmp/category-images/` | 0.00 MB | Empty/placeholder helper folder; can be removed if not reusing its import workflow. |
| `tmp/gallery/` | 11.39 MB | Intermediate images/cache/source material; review and archive anything unique before removing. |
| `tmp/gallery-browser/` | 6.74 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/gallery-browser-mobile/` | 6.74 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/manufacturer/` | 3.42 MB | Quotation extracts and manufacturer reference photos; keep privately or archive useful references before deleting. |
| `tmp/manufacturer-catalogue-preview/` | 5.67 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/manufacturer-cdp/` | 6.60 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/manufacturer-cdp-v2/` | 5.80 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/manufacturer-web-preview/` | 6.74 MB | Disposable headless-browser test profile; can be removed after its browser process is closed. |
| `tmp/pdf-venv/` | 83.11 MB | Keep until catalogue work is complete; current working PDF dependencies. |
| `tmp/pdfs/` | 18.09 MB | Generated page renders and working files; preserve tracked reference PNGs before cleaning. |
| `tmp/performance-deps/` | 0.00 MB | Empty/placeholder helper folder; can be removed if not reusing its import workflow. |
| `tmp/product-images/` | 0.00 MB | Empty/placeholder helper folder; can be removed if not reusing its import workflow. |
| `tmp/references/` | 0.80 MB | Intermediate images/cache/source material; review and archive anything unique before removing. |
| `tmp/sugarcane-additions/` | 15.01 MB | Intermediate images/cache/source material; review and archive anything unique before removing. |
| `tmp/sugarcane-images/` | 29.32 MB | Intermediate images/cache/source material; review and archive anything unique before removing. |
| `tmp/uv-cache/` | 0.00 MB | Intermediate images/cache/source material; review and archive anything unique before removing. |

Some files under ignored tmp/ are already tracked by Git. Preserve or move these source references before a broad temporary-folder cleanup:

- `tmp/pdfs/adil-reference.png`
- `tmp/pdfs/mohammed-reference.png`
- `tmp/pdfs/reference.png`

## Suggested next steps

1. Remove obsolete image entries/derivatives from deployment and review the unused CSS candidates.
2. Confirm the three unquoted product specifications and any missing social/profile URLs.
3. Update maintenance documentation to the final website state.
4. When instructed, regenerate and visually review both catalogues from the final product data and imagery.
5. Commit all intended changes and deploy the validated dist/ output.

No broad file/folder deletion was performed as part of this audit. The report identifies candidates and preserves the existing catalogue hold.
