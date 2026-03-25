# Modbus Device Maps

[![Compatible with Modbus Monitor XPF](https://img.shields.io/badge/Modbus%20Monitor-XPF-blue)](https://www.modbusmonitor.com/download)
[![Documentation](https://img.shields.io/badge/docs-device--maps-green)](https://docs.quantumbitsolutions.com/products/xpf/device-maps/)
[![License](https://img.shields.io/github/license/Modbus-Monitor/modbus-device-maps)](LICENSE)

Pre-built Modbus device maps for industrial energy meters and equipment, designed for use with **[Modbus Monitor XPF](https://www.modbusmonitor.com/download)**.

---

## What Are Modbus Device Maps?

A **Modbus device map** defines the register layout of an industrial device — specifying which registers correspond to which measurements (voltage, current, power, energy, etc.), along with data types, scaling factors, and units.

Without a device map, engineers must manually cross-reference vendor documentation, determine register addresses, configure data types, and apply the correct scaling — a time-consuming and error-prone process.

With a device map, Modbus Monitor XPF automatically handles all of this, letting you connect to a device and start reading real data in seconds.

---

## Supported Manufacturers

This repository includes preview and reference device maps for equipment from leading industrial manufacturers:

| Manufacturer | Device Types |
|---|---|
| **Schneider Electric** | Power meters, energy analyzers |
| **Siemens** | Power monitoring devices, PAC series |
| **ABB** | Energy meters, M2M/M4M series |
| **SolarEdge** | Solar inverters, monitoring platforms |
| **Eaton** | Power quality meters, protection relays |

> **Note:** The maps in this repository are **preview and reference maps**. The full library — including additional registers, scaling, and device-specific configurations — is available directly within **Modbus Monitor XPF**.

---

## Popular Device Maps

| Device | Manufacturer | Description |
|---|---|---|
| **PM8000** | Schneider Electric | Advanced power and energy metering |
| **PAC4200** | Siemens | Power monitoring with integrated display |
| **M4M** | ABB | Modular multi-function energy meter |
| **SE5000** | SolarEdge | Single-phase solar inverter |

---

## Why Use Device Maps?

- ✅ **Skip manual register mapping** — no need to manually decode vendor datasheets
- ✅ **Standardized format** — consistent structure across all supported devices
- ✅ **Instant connectivity** — load a map and start reading data immediately
- ✅ **Reduced configuration errors** — pre-validated register definitions and scaling
- ✅ **Engineer-friendly** — designed for field engineers and systems integrators

---

## Using Device Maps with Modbus Monitor XPF

These maps are intended for use with **[Modbus Monitor XPF](https://www.modbusmonitor.com/download)**, a professional Modbus diagnostic and monitoring tool.

To get started:

1. [Download Modbus Monitor XPF](https://www.modbusmonitor.com/download)
2. Load a device map from this repository or from the built-in library within XPF
3. Connect to your device and begin monitoring registers immediately

For the complete device map library and full documentation, visit:  
📖 [docs.quantumbitsolutions.com/products/xpf/device-maps/](https://docs.quantumbitsolutions.com/products/xpf/device-maps/)

---

## Editions

Modbus Monitor XPF is available in multiple editions. To see a full comparison of features including device map support:  
🔍 [www.modbusmonitor.com/compare](https://www.modbusmonitor.com/compare)

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in this repository.
