# fw2-orca-templates

Example project templates for the FreeWili 2 ORCA module.

Currently supports:

- [KiCad](./kicad) — schematic/PCB template (`ORCATemplate`)

## KiCad template

The `kicad/` directory contains a starter KiCad 7 project (`ORCATemplate`) for
building ORCA module boards, including a 3D `.step` model and a custom
`EEPROM.pretty` footprint library.

> **Note:** `kicad/fp-lib-table` currently references footprint libraries
> (`IDC_10`, `IDC_20`) by absolute path on another machine. Update these
> library paths (or replace them with the project-relative `${KIPRJMOD}`
> style used for `EEPROM`) before relying on the template on a fresh
> checkout.
