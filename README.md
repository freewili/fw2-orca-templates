# fw2-orca-templates

Example project templates for the FreeWili 2 ORCA module.

Currently supports:

- [KiCad](./kicad) — schematic/PCB template (`ORCATemplate`)
- [Connector pinouts](./PINOUTS.md) — Free Wili OG and Free Wili 2 20-position and 10-position connector pin tables
- [ORCA_NRF example](./examples/ORCA_NRF) — example ORCA module board carrying an NRF24L01 radio

## KiCad template

The `kicad/` directory contains a starter KiCad 7 project (`ORCATemplate`) for
building ORCA module boards, including a 3D `.step` model and a custom
`EEPROM.pretty` footprint library.

The ORCA module connects via two headers, `CN1` and `CN2`:

![ORCA connector symbols](./assets/KiCADsymbols.png)

> **Note:** `kicad/fp-lib-table` currently references footprint libraries
> (`IDC_10`, `IDC_20`) by absolute path on another machine. Update these
> library paths (or replace them with the project-relative `${KIPRJMOD}`
> style used for `EEPROM`) before relying on the template on a fresh
> checkout.

## ORCA_NRF example

The `examples/ORCA_NRF/` directory contains a complete example ORCA module
project built from the template: an NRF24L01 radio carrier with the `CN1`
(20-pin) and `CN2` (10-pin) headers and the ID EEPROM.

> **Note:** The symbols and footprints are embedded in the schematic and PCB,
> so the project opens without extra libraries. The 3D model references in
> `ORCA_NRF.kicad_pcb` use absolute paths from another machine and will show
> as missing in the 3D viewer until you repoint them.
