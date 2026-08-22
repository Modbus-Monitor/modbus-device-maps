#!/usr/bin/env node
"use strict";

// Local Node equivalent of upgrade_catalog_metadata.py for workstations that
// publish the static site without Python installed.
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const catalogPath = path.join(root, "catalog.json");
const catalogJsPath = path.join(root, "data", "catalog.js");
const explicitProtocols = new Map([
  ["Modbus RTU / Modbus TCP", ["RTU", "TCP"]],
  ["Modbus", []],
]);
const generatedUtc = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));

catalog.$schema = "https://modbus-monitor.github.io/modbus-device-maps/schemas/catalog.schema.json";
catalog.catalog_version ??= "1.0";
catalog.catalog_generated_utc = generatedUtc;
delete catalog.generated_utc;
catalog.id_policy ??= "manufacturer-slug/device-slug";
catalog.deprecated_fields ??= {
  register_count: "Deprecated compatibility alias for preview_register_count.",
};

for (const entry of catalog.maps) {
  const payload = JSON.parse(fs.readFileSync(path.join(root, entry.json_url), "utf8"));
  const protocols = explicitProtocols.get(payload.protocol);
  if (!protocols) {
    throw new Error(entry.id + ": unsupported protocol source value " + JSON.stringify(payload.protocol));
  }

  entry.map_version ??= "1.0";
  entry.map_schema_version = entry.schema_version ?? 1;
  delete entry.schema_version;
  delete entry.updated_utc;
  entry.source_type ??= "qbs";
  entry.verification_level ??= "not-reviewed";
  entry.supported_protocols = protocols;
  entry.availability ??= "preview";
  entry.aliases ??= [];
  entry.preview_register_count = entry.register_count;
  entry.full_register_count ??= null;
  if (payload.protocol === "Modbus") {
    entry.review_flags ??= [];
    if (!entry.review_flags.includes("supported_protocols")) {
      entry.review_flags.push("supported_protocols");
    }
  }
}

fs.writeFileSync(catalogPath, JSON.stringify(catalog, null, 2) + "\n", "utf8");
fs.writeFileSync(catalogJsPath, "window.MODBUS_MAP_CATALOG = " + JSON.stringify(catalog) + ";\n", "utf8");
console.log("Upgraded " + catalog.maps.length + " catalog entries; " + generatedUtc);
