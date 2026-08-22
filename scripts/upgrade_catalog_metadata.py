#!/usr/bin/env python3
"""Add the v1 canonical-catalog metadata without changing public map IDs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"
CATALOG_JS_PATH = ROOT / "data" / "catalog.js"
EXPLICIT_PROTOCOLS = {
    "Modbus RTU / Modbus TCP": ["RTU", "TCP"],
    "Modbus": [],
}


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    catalog["$schema"] = "https://modbus-monitor.github.io/modbus-device-maps/schemas/catalog.schema.json"
    catalog.setdefault("catalog_version", "1.0")
    catalog["catalog_generated_utc"] = generated_utc
    catalog.pop("generated_utc", None)
    catalog.setdefault("id_policy", "manufacturer-slug/device-slug")
    catalog.setdefault(
        "deprecated_fields",
        {"register_count": "Deprecated compatibility alias for preview_register_count."},
    )

    for entry in catalog["maps"]:
        # Keep register_count for existing website/API consumers. The new field
        # makes its preview-only meaning explicit; full inventory is unknown.
        preview_register_count = entry["register_count"]
        payload = json.loads((ROOT / entry["json_url"]).read_text(encoding="utf-8"))
        protocol = payload.get("protocol")
        if protocol not in EXPLICIT_PROTOCOLS:
            raise ValueError(f"{entry['id']}: unsupported protocol source value {protocol!r}")

        entry.setdefault("map_version", "1.0")
        entry["map_schema_version"] = entry.pop("schema_version", 1)
        entry.pop("updated_utc", None)
        entry.setdefault("source_type", "qbs")
        entry.setdefault("verification_level", "not-reviewed")
        entry["supported_protocols"] = EXPLICIT_PROTOCOLS[protocol]
        entry.setdefault("availability", "preview")
        entry.setdefault("aliases", [])
        entry["preview_register_count"] = preview_register_count
        entry.setdefault("full_register_count", None)

        if protocol == "Modbus":
            review_flags = entry.setdefault("review_flags", [])
            if "supported_protocols" not in review_flags:
                review_flags.append("supported_protocols")

    CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CATALOG_JS_PATH.write_text(
        "window.MODBUS_MAP_CATALOG = " + json.dumps(catalog, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Upgraded {len(catalog['maps'])} catalog entries; {generated_utc}")


if __name__ == "__main__":
    main()
