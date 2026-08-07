#!/usr/bin/env python3
"""Dependency-free structural validation for the generated public catalog."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_MAP_FIELDS = {
    "schema_version",
    "id",
    "manufacturer",
    "manufacturer_slug",
    "model",
    "slug",
    "title",
    "description",
    "device_type",
    "protocol",
    "address_display_convention",
    "registers",
    "guide_status",
    "documentation_url",
    "product",
}
REQUIRED_REGISTER_FIELDS = {"name", "display_address", "data_type", "unit", "category"}
PRIVATE_TOKENS = {"source_csv", "preview_registers", "regunitid", "reggain", "regoffset", "regwrite", "\\interim\\", "workbench"}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    seen: set[str] = set()
    for entry in catalog.get("maps", []):
        identifier = entry.get("id", "<missing-id>")
        if identifier in seen:
            errors.append(f"duplicate catalog id: {identifier}")
        seen.add(identifier)
        path = root / entry.get("json_url", "")
        if not path.is_file():
            errors.append(f"{identifier}: missing {path.relative_to(root)}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        missing = REQUIRED_MAP_FIELDS - payload.keys()
        if missing:
            errors.append(f"{identifier}: missing map fields {sorted(missing)}")
        if payload.get("id") != identifier:
            errors.append(f"{identifier}: file id does not match catalog")
        registers = payload.get("registers")
        if not isinstance(registers, list) or not registers:
            errors.append(f"{identifier}: registers must be a non-empty array")
            continue
        if payload.get("register_count") != len(registers):
            errors.append(f"{identifier}: register_count does not match registers")
        if not 6 <= len(registers) <= 12:
            errors.append(f"{identifier}: previews must contain 6-12 registers")
        if payload.get("guide_status") == "published" and not payload.get("documentation_url"):
            errors.append(f"{identifier}: published guide has no documentation_url")
        if payload.get("guide_status") == "upcoming" and payload.get("documentation_url"):
            errors.append(f"{identifier}: upcoming guide must not have a documentation_url")
        if not (root / "pages" / identifier / "index.html").is_file():
            errors.append(f"{identifier}: missing static preview page")
        serialized = json.dumps(payload, ensure_ascii=False).lower()
        exposed = sorted(token for token in PRIVATE_TOKENS if token in serialized)
        if exposed:
            errors.append(f"{identifier}: possible private source field(s) {exposed}")
        for index, register in enumerate(registers):
            missing_register = REQUIRED_REGISTER_FIELDS - register.keys()
            if missing_register:
                errors.append(f"{identifier} register {index}: missing {sorted(missing_register)}")
            if not register.get("display_address"):
                errors.append(f"{identifier} register {index}: empty display_address")

    if catalog.get("map_count") != len(catalog.get("maps", [])):
        errors.append("catalog map_count does not match maps array")
    if "<loc>" not in (root / "sitemap.xml").read_text(encoding="utf-8"):
        errors.append("sitemap has no URLs")
    actual_files = set((root / "maps").rglob("*.json"))
    expected_files = {root / entry["json_url"] for entry in catalog.get("maps", [])}
    for path in sorted(actual_files - expected_files):
        errors.append(f"orphan map file: {path.relative_to(root)}")
    if errors:
        raise SystemExit("Catalog validation failed:\n- " + "\n- ".join(errors))
    print(f"Validated {len(seen)} map files and {sum(len(json.loads(p.read_text(encoding='utf-8'))['registers']) for p in expected_files)} preview registers.")


if __name__ == "__main__":
    main()
