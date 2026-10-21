# Performance and asset maintenance

Updated: 21 October 2026.

This is a dependency-free static website. Production publishes five HTML pages and only allowlisted assets. Developer caches, reference artwork, scripts, tests and output previews are not deployed.

## Current implementation

- Browser cards and content images use local WebP derivatives and responsive source hints. Full-size sources remain available where required.
- Local WOFF2 fonts avoid third-party font stylesheet requests. The build preloads the two normal fonts and preserves font-display: optional.
- Component CSS is bundled once; the same bytes are reused for content hashing and deployment. CSS and JavaScript get content-based version URLs.
- Scroll and pointer work is scheduled through requestAnimationFrame. Gallery widths are measured after resizing, rather than on every navigation click. Reduced-motion preferences cancel active animations.
- Contact no longer downloads the unused Material Studio/pointer script.
- Removed 25 unused legacy gallery assets, the old share graphic and three disposable card renders, totaling 1,820,852 bytes. Four superseded logo/product originals are retained under scripts/references/legacy-images/. This is repository disk savings, not a measured reduction in website transfer size; these files were already outside the deployment allowlist.
- Responsive image generation now includes only the active recycling gallery, preventing removed legacy variants from returning.
- PDF and offline browser catalogues share one cached JPEG conversion per image, with a 1400-pixel maximum edge and quality 86. The PDF fell from 17.76 MB to 3.94 MB (about 78% smaller); original source artwork remains intact.

## Maintenance

Run npm run audit for a read-only inventory, npm run validate before deployment, and npm run catalogue after product data changes. Install authoring packages from scripts/catalogue/requirements.txt when preparing a Python environment. Production itself needs Node.js only.

After changing source photos, run scripts/images/create-responsive-images.py with Pillow and commit the image variants and responsive manifest together. Do not delete source or reference artwork simply because it is not deployed.

No new live PageSpeed score, real-user Core Web Vitals result or search-ranking improvement is claimed. Measure the deployed build before comparing performance scores.
