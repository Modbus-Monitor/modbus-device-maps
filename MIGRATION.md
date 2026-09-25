# Public HTML migration

The maintained data source remains `catalog.json` and `maps/*.json` in this repository. IDs, schemas, relative preview URLs, raw-file URLs and data terms are compatibility contracts. Browser redirects do not change these contracts.

The reviewed manifest maps the exact hub and each catalog HTML preview to docs. The Pages workflow first normalizes Dataset metadata, assembles the existing site, then overlays static redirects. Source preview HTML is retained for rollback; only the deployed artifact changes. The overlay removes the retired HTML URLs from the artifact sitemap and removes their obsolete structured data by replacing the complete HTML document.

## Release order

1. Deploy the docs changes first. Verify every manifest target returns 200, contains the correct model and preview, has one self-canonical, and has no refresh or noindex. New preview-only pages must be live before redirect deployment.
2. Build this repository's Pages artifact and run `python scripts/apply_html_redirects.py --site-dir _site`. Check all exact source URLs and ensure `catalog.json`, `maps/`, `schemas/`, `data/` and `data-license/` are unchanged.
3. Deploy this repository. Check every redirect and representative app catalog/preview/import operations, including legacy clients.
4. Deploy the separate organization homepage redirect only after the hub's documentation, product, company and GitHub navigation is live.
5. Update WordPress navigation links directly to final docs destinations. Record the deployment date and monitor matched Search Console cohorts weekly for 6–8 weeks without double-counting overlapping properties.

These are static instant meta refreshes with canonical and visible links, not HTTP 301 responses. No DNS, CNAME, host-wide redirect, robots block, or Search Console removal is involved. Keep redirects for at least one year and machine endpoints indefinitely while clients depend on them.

## Updating previews

Run the docs repository's `tools/device-maps/build_public_previews.py --catalog-root ../modbus-device-maps` against the reviewed public catalog. Commit its generated Markdown and provenance manifest, and copy that manifest to `html-redirects.json` here. Review ID-to-target matches. The overlay rejects changed catalog/map hashes until the manifest is reviewed and refreshed; it must not silently redirect newly added maps to a generic hub.

For rollback, remove the overlay workflow step to restore source HTML, or revert the migration commit. Do not delete data endpoints or disable Pages. The docs pages may remain available throughout rollback.
