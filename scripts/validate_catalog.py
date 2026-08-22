#!/usr/bin/env python3
"""Dependency-free validation for the public logical device-map catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_CATALOG_FIELDS = {"schema_version", "catalog_version", "catalog_generated_utc", "id_policy", "map_count", "maps"}
REQUIRED_ENTRY_FIELDS = {
    "id", "manufacturer", "manufacturer_slug", "model", "slug", "device_type", "description",
    "categories", "register_count", "preview_register_count", "full_register_count", "map_version",
    "map_schema_version", "source_type", "verification_level", "supported_protocols",
    "availability", "aliases", "guide_status", "json_url", "preview_url", "github_url", "download_url", "request_url",
}
REQUIRED_MAP_FIELDS = {
    "schema_version", "id", "manufacturer", "manufacturer_slug", "model", "slug", "title",
    "description", "device_type", "protocol", "address_display_convention", "registers", "guide_status",
    "documentation_url", "product",
}
REQUIRED_REGISTER_FIELDS = {"name", "display_address", "data_type", "unit", "category"}
SOURCE_TYPES = {"qbs", "manufacturer", "community", "sunspec"}
VERIFICATION_LEVELS = {"not-reviewed", "qbs-verified", "manufacturer-documented", "community-reviewed"}
AVAILABILITY = {"preview", "unavailable", "retired"}
PROTOCOLS = {"RTU", "TCP", "ASCII", "UDP"}
PRIVATE_TOKENS = {
    "source_csv", "preview_registers", "regunitid", "reggain", "regoffset", "regwrite", "\\interim\\",
    "workbench", "blob.core.windows.net", "accountkey", "sharedaccesssignature", "sig=", "se=", "sp=",
}


def is_http_url(value: object) -> bool:
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc)


def is_safe_relative_path(value: object, prefix: str) -> bool:
    return isinstance(value, str) and value.startswith(prefix) and ".." not in Path(value).parts


def add_private_token_errors(identifier: str, payload: object, errors: list[str]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    exposed = sorted(token for token in PRIVATE_TOKENS if token in serialized)
    if exposed:
        errors.append(f"{identifier}: possible private source field(s) {exposed}")


def main() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    catalog_js = (ROOT / "data" / "catalog.js").read_text(encoding="utf-8")
    catalog_js_prefix = "window.MODBUS_MAP_CATALOG = "
    if not catalog_js.startswith(catalog_js_prefix) or not catalog_js.rstrip().endswith(";"):
        errors.append("data/catalog.js must assign window.MODBUS_MAP_CATALOG")
    else:
        try:
            browser_catalog = json.loads(catalog_js[len(catalog_js_prefix):].strip().removesuffix(";"))
            if browser_catalog != catalog:
                errors.append("data/catalog.js does not match catalog.json")
        except json.JSONDecodeError as exc:
            errors.append(f"data/catalog.js contains invalid JSON: {exc}")
    missing_catalog = REQUIRED_CATALOG_FIELDS - catalog.keys()
    if missing_catalog:
        errors.append(f"catalog: missing fields {sorted(missing_catalog)}")
    if catalog.get("id_policy") != "manufacturer-slug/device-slug":
        errors.append("catalog: id_policy must be manufacturer-slug/device-slug")
    if catalog.get("deprecated_fields", {}).get("register_count") != "Deprecated compatibility alias for preview_register_count.":
        errors.append("catalog: register_count deprecation notice is missing")
    maps = catalog.get("maps")
    if not isinstance(maps, list):
        errors.append("catalog: maps must be an array")
        maps = []

    live_ids: set[str] = set()
    aliases: set[str] = set()
    expected_files: set[Path] = set()
    preview_register_total = 0

    for entry in maps:
        identifier = entry.get("id", "<missing-id>")
        missing_entry = REQUIRED_ENTRY_FIELDS - entry.keys()
        if missing_entry:
            errors.append(f"{identifier}: missing catalog fields {sorted(missing_entry)}")
            continue
        if "schema_version" in entry or "updated_utc" in entry:
            errors.append(f"{identifier}: use map_schema_version and catalog_generated_utc instead of ambiguous schema_version/updated_utc")
        if identifier in live_ids:
            errors.append(f"duplicate catalog id: {identifier}")
        live_ids.add(identifier)
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            errors.append(f"{identifier}: id must use manufacturer-slug/device-slug")
        elif identifier != f"{entry['manufacturer_slug']}/{entry['slug']}":
            errors.append(f"{identifier}: id must match manufacturer_slug/slug")
        if entry["source_type"] not in SOURCE_TYPES:
            errors.append(f"{identifier}: invalid source_type")
        if entry["verification_level"] not in VERIFICATION_LEVELS:
            errors.append(f"{identifier}: invalid verification_level")
        if entry["availability"] not in AVAILABILITY:
            errors.append(f"{identifier}: invalid availability")
        protocols = entry["supported_protocols"]
        if not isinstance(protocols, list) or any(protocol not in PROTOCOLS for protocol in protocols):
            errors.append(f"{identifier}: supported_protocols must use normalized values")
        if len(protocols) != len(set(protocols)):
            errors.append(f"{identifier}: supported_protocols contains duplicates")
        review_flags = entry.get("review_flags", [])
        if not isinstance(review_flags, list) or len(review_flags) != len(set(review_flags)):
            errors.append(f"{identifier}: review_flags must be a duplicate-free array")
        if not protocols and "supported_protocols" not in review_flags:
            errors.append(f"{identifier}: empty supported_protocols requires a supported_protocols review flag")
        aliases_for_entry = entry["aliases"]
        if not isinstance(aliases_for_entry, list) or len(aliases_for_entry) != len(set(aliases_for_entry)):
            errors.append(f"{identifier}: aliases must be a duplicate-free array")
        for alias in aliases_for_entry:
            if not isinstance(alias, str) or not ID_PATTERN.fullmatch(alias):
                errors.append(f"{identifier}: invalid alias {alias!r}")
            if alias in aliases:
                errors.append(f"duplicate alias: {alias}")
            aliases.add(alias)
        if entry["preview_register_count"] != entry["register_count"]:
            errors.append(f"{identifier}: legacy register_count must match preview_register_count")
        if not isinstance(entry["preview_register_count"], int) or entry["preview_register_count"] < 1:
            errors.append(f"{identifier}: preview_register_count must be a positive integer")
        full_count = entry["full_register_count"]
        if full_count is not None and (not isinstance(full_count, int) or full_count < entry["preview_register_count"]):
            errors.append(f"{identifier}: full_register_count must be null or at least preview_register_count")
        if not is_safe_relative_path(entry["json_url"], "maps/"):
            errors.append(f"{identifier}: json_url must be a safe maps/ relative path")
        if not is_safe_relative_path(entry["preview_url"], "pages/"):
            errors.append(f"{identifier}: preview_url must be a safe pages/ relative path")
        for field in ("github_url", "download_url", "request_url"):
            if not is_http_url(entry[field]):
                errors.append(f"{identifier}: {field} must be an absolute HTTP(S) URL")
        if entry["documentation_url"] is not None and not is_http_url(entry["documentation_url"]):
            errors.append(f"{identifier}: documentation_url must be null or an absolute HTTP(S) URL")

        path = ROOT / entry["json_url"]
        expected_files.add(path)
        if not path.is_file():
            errors.append(f"{identifier}: missing {entry['json_url']}")
            continue
        preview_page = ROOT / entry["preview_url"] / "index.html"
        if not preview_page.is_file():
            errors.append(f"{identifier}: missing static preview page {entry['preview_url']}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        missing_map = REQUIRED_MAP_FIELDS - payload.keys()
        if missing_map:
            errors.append(f"{identifier}: missing map fields {sorted(missing_map)}")
        if payload.get("id") != identifier:
            errors.append(f"{identifier}: file id does not match catalog")
        registers = payload.get("registers")
        if not isinstance(registers, list) or not registers:
            errors.append(f"{identifier}: registers must be a non-empty array")
            continue
        preview_register_total += len(registers)
        if entry["preview_register_count"] != len(registers) or payload.get("register_count") != len(registers):
            errors.append(f"{identifier}: preview register count does not match map JSON")
        if not 6 <= len(registers) <= 12:
            errors.append(f"{identifier}: previews must contain 6-12 registers")
        if payload.get("guide_status") == "published" and not payload.get("documentation_url"):
            errors.append(f"{identifier}: published guide has no documentation_url")
        if payload.get("guide_status") == "upcoming" and payload.get("documentation_url"):
            errors.append(f"{identifier}: upcoming guide must not have a documentation_url")
        add_private_token_errors(identifier, payload, errors)
        for index, register in enumerate(registers):
            missing_register = REQUIRED_REGISTER_FIELDS - register.keys()
            if missing_register:
                errors.append(f"{identifier} register {index}: missing {sorted(missing_register)}")
            if not register.get("display_address"):
                errors.append(f"{identifier} register {index}: empty display_address")

    for collision in sorted(aliases & live_ids):
        errors.append(f"alias collides with live id: {collision}")
    add_private_token_errors("catalog", catalog, errors)
    if catalog.get("map_count") != len(maps):
        errors.append("catalog map_count does not match maps array")
    if "<loc>" not in (ROOT / "sitemap.xml").read_text(encoding="utf-8"):
        errors.append("sitemap has no URLs")
    actual_files = set((ROOT / "maps").rglob("*.json"))
    for path in sorted(actual_files - expected_files):
        errors.append(f"orphan map file: {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("Catalog validation failed:\n- " + "\n- ".join(errors))
    print(f"Validated {len(live_ids)} map files and {preview_register_total} preview registers.")


if __name__ == "__main__":
    main()
