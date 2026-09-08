# Rev A CAD verification

Fresh verification: 2026-09-08T23:21:20+00:00.
KiCad 10.0.6. All commands exited 0.

- Schematic connection audit: **216 assertions passed**, including all four
  allowed device pairings, both VREF modes, EEPROM/supply isolation,
  analog dividers, CAN isolation, and required DNP parts.
- PCB audit: **138 schematic pad/net assignments passed**, plus connector
  geometry, corrected switch numbering, local models, board construction,
  design rules and absence of DRC exclusions.
- ERC: **0 violations**.
- DRC: **0 violations, 0 unconnected items, 0 schematic parity issues**.
  Reports use the project's enabled error/warning checks. KiCad's ignored
  check categories are explicitly listed in the JSON reports.

These automated checks do not establish visual review. Inspect the schematic
and current top, bottom and perspective previews separately before release.
Independent circuit and footprint review is recorded in
[circuit-review.md](circuit-review.md).

Configured minimums: 0.20 mm tracks, 0.15 mm copper clearance, 0.30 mm
copper-edge clearance, 0.15 mm silk clearance, 1.0 mm text height and
0.15 mm text thickness.
The board uses two copper layers, 1.6 mm thickness and a 130 x 130 mm
cross outline. There are 28 footprints including four mechanical holes.

These checks establish CAD connectivity and the configured design rules.
They do not establish enclosure fit, manufactured-board quality, signal
integrity at a specified speed, EEPROM identification or hardware operation.
The [setup and bench requirements](../README.md) remain prerequisites to release.

## Reproduce

Run `tools/verify_project.py` with KiCad's bundled Python. It re-exports
the actual schematic netlist, runs both independent audits, runs ERC in
JSON and text formats, and runs DRC with zone refill and schematic parity.
It stops on a failing command and refreshes this report only on success.

## Verified file SHA-256

- `gpiojoiner.kicad_sch`: `eea3e45c28ea3d7d3a0ca2fb27f6ecfe00bd261af3fdb921f23457043e6cb70f`
- `gpiojoiner.kicad_pcb`: `28bcf821207bb0a78fc67c70718cc22cc994a2f24c78a07c4d349115c0c0c7f3`
- `gpiojoiner.kicad_pro`: `51b380ce64545851a422f7cbc25708f096ab6f13b1da3c1fffd300cb95f5d95e`

## Command output

```text

PASS: 216 connection/value assertions; four device pairings, both VREF modes, 37 exact copper-net groups.
Found 0 violations
Saved ERC Report to reports/erc.json
Found 0 violations
Saved ERC Report to reports/erc.rpt
Found 0 violations
Found 0 unconnected items
Found 0 schematic parity issues
Saved DRC Report to reports/drc.json
Saved board
PASS: 138 schematic pad/net assignments; 6 docking connectors; FW2 spacing/orientation; corrected switch; DNPs; 4 holes; local models.
```
