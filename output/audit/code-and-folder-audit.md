> Historical audit: cleanup recommendations below were completed. See [current maintenance status](maintenance-status.md) and [cleanup completion](cleanup-completion.md). Old counts and folder sizes describe the earlier snapshot.

# Directory and catalogue audit

25 October 2026. Changes completed in the local workspace.

## Collection cleanup

The website now contains 34 product families in four categories. Removed the discontinued collection's 36 products and eight subcategories, product photos, category images and responsive variants, reference records, image prompts, category image generator, obsolete product redirects and category-specific specification branches. Removed unused material-guide styles and adjusted collection gateways for one collection.

Updated all five pages, category controls, enquiry suggestions, recommendation tool, static product fallback, search/social metadata and generated structured data. Remaining product IDs and reference numbers are preserved. The separate Sugarcane Paper category remains available.

## Printed and downloadable assets

Regenerated all five two-sided visiting cards with the current range line. Reviewed their front/back previews. Regenerated the 41-page catalogue and portable browser catalogue from the retained products; reviewed cover, directory, sample product pages across the four categories and the contact page. The generator validates specification text and links. The public PDF is assets/catalogues/MA-Industries-Catalogue.pdf and website/download/build references use that filename.

Both supplied product specification PDFs were inspected: neither contains the discontinued collection. They remain unchanged.

## Validation

- 46 regression tests passed, including category filtering, paging, dialogs, keyboard interaction, enquiries, navigation, SEO and asset paths.
- Seven browser scripts passed syntax checks.
- Catalogue markup and metadata are synchronized across all five source pages.
- Production build: five indexable pages and 184 public assets.
- Build verifier: 252 local links/assets plus structured data verified.
- Asset inventory: no unreferenced candidates or exact duplicates.
- Source and generated deployment text searched for discontinued product IDs, category references and outdated product/category totals.

The updated site is prepared in dist/. Publishing to the live host has not been performed.

## Manufacturer specification update

Reconciled 85 quotation variants across 22 existing and four new product families. Product details now use accessible variant tables. The PDF and browser catalogues use the same technical data, with the redesigned PDF using collection dividers, larger product photos, aligned tables and linked directory entries. See manufacturer-reconciliation.md for the full mapping, source ambiguities and image provenance. Supplier costs and unverified barcodes are excluded from public outputs.
