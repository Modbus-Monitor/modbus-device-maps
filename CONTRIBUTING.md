# Contributing

Corrections and device requests are welcome.

## Report a register correction

Use the register-correction issue form and include the manufacturer, model, firmware or document revision, affected signal, current value, proposed value, and a public manufacturer source URL when available. Do not attach confidential manuals or files you are not permitted to redistribute.

## Request a device map

Use the map-request issue form. Search existing issues and the catalog first, then provide the exact manufacturer/model and a public technical-manual link.

## Pull requests

Generated files under `maps/`, `catalog.json`, `data/catalog.js`, `README.md`, and `sitemap.xml` come from a private publishing pipeline. For a data correction, open an issue so the source documentation record can be corrected before regeneration. Pull requests for the schema, validator, documentation, and website code are welcome.

Run `python scripts/validate_catalog.py` before submitting a change. Contributions must not add vendor PDFs, proprietary spreadsheets, credentials, customer data, or unsafe write instructions.
