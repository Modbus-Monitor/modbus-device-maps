# Safety and accuracy disclaimer

These files are reference previews, not manufacturer-approved configuration or safety documentation. They may contain errors, omit registers, or differ by model, option, region, and firmware revision.

Modbus addressing is especially easy to misinterpret. A displayed register reference such as `40001` is not always the protocol offset sent on the wire. Confirm the manufacturer's current manual, function code, address base, data length, byte order, word order, scaling, access mode, and device firmware before polling.

Never write to a register based solely on this repository. An incorrect write can stop equipment, change protection settings, damage property, or create a safety hazard. Use appropriate isolation, authorization, backups, commissioning procedures, and qualified engineering review.

Quantum Bit Solutions is not affiliated with or endorsed by the listed manufacturers unless explicitly stated. Product names and trademarks belong to their respective owners. The files are provided without warranty; see `LICENSE` and `DATA_LICENSE.md`.
