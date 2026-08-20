"""Apply the common Dataset ownership and licensing metadata to static pages.

The public site is deployed as prebuilt HTML. Run this script after generating
or updating catalog and device preview pages so their JSON-LD stays consistent.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LICENSE_URL = "https://modbus-monitor.github.io/modbus-device-maps/data-license/"
ORGANIZATION = {
    "@type": "Organization",
    "name": "Quantum Bit Solutions",
    "url": "https://quantumbitsolutions.com/",
}
LICENSE = {
    "@type": "CreativeWork",
    "name": "Modbus Device Maps Data Terms",
    "url": LICENSE_URL,
}
JSON_LD_PATTERN = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)', re.DOTALL
)


def update_dataset(dataset: dict) -> bool:
    """Set the Dataset fields recommended by Google Search Console."""
    changed = False
    for property_name, value in (
        ("creator", ORGANIZATION),
        ("publisher", ORGANIZATION),
        ("license", LICENSE),
        ("isAccessibleForFree", True),
    ):
        if dataset.get(property_name) != value:
            dataset[property_name] = value
            changed = True
    return changed


def update_html(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    changed = False
    dataset_count = 0

    def replace_json_ld(match: re.Match) -> str:
        nonlocal changed, dataset_count
        payload = json.loads(match.group(2))
        if payload.get("@type") == "Dataset":
            dataset_count += 1
            changed |= update_dataset(payload)
        elif payload.get("@type") == "DataCatalog":
            dataset = payload.get("dataset")
            if isinstance(dataset, dict) and dataset.get("@type") == "Dataset":
                dataset_count += 1
                changed |= update_dataset(dataset)
        return match.group(1) + json.dumps(payload, separators=(",", ":")) + match.group(3)

    result = JSON_LD_PATTERN.sub(replace_json_ld, source)
    if dataset_count != 1:
        raise ValueError(f"Expected exactly one Dataset JSON-LD object in {path}; found {dataset_count}.")

    result = result.replace('href="DATA_LICENSE.md"', 'href="data-license/"')
    result = result.replace('href="../../../DATA_LICENSE.md"', 'href="../../../data-license/"')
    if result != source:
        path.write_text(result, encoding="utf-8", newline="\n")
        return True
    return changed


def main() -> None:
    pages = [ROOT / "index.html", *sorted((ROOT / "pages").glob("*/*/index.html"))]
    updated = sum(update_html(page) for page in pages)
    print(f"Processed {len(pages)} Dataset pages; updated {updated}.")


if __name__ == "__main__":
    main()
