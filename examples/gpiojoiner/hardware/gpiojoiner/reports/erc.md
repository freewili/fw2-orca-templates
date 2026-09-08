# Schematic verification — rev A prototype

Verified with KiCad CLI 10.0.6 on 2026-09-08.

- `sch erc --exit-code-violations`: **0 violations**, exit 0.
  Machine-readable results are in `erc.json`; readable results are in `erc.rpt`.
- `python tools/check_connections.py`: **216 assertions passed** against the
  KiCad-exported `netlist.xml`, covering four permitted device pairs, both
  VREF switch modes, 37 exact connected-net memberships, all 24 physical
  components and footprints, EEPROM pins, supply/CAN isolation, both analog
  divider paths, and required DNP parts. Eight no-connect connector pins are
  also checked for isolation.
- The audit was written before the schematic and initially failed with the
  expected missing-netlist message. Independent mutation checks rejected a
  reversed diode connection, missing UART crossing, wrong divider resistance,
  wrong switch footprint, and populated CAN termination.
- The local symbol library independently loaded and exported all 10 symbols.
- The A3 PDF, SVG, and raster preview were exported and visually inspected;
  connector assignments, notes, divider topology, EEPROM, mode switch, and
  DNP/test-point groups are readable without overlapping labels.

The manufacturer JS202011CQN contact states are 1–2/4–5 and 2–3/5–6.
The schematic uses the corrected project-local `GPIOJoiner:SW_JS202011CQN`
footprint. The parent PCB task verified its parallel terminal-row numbering;
the installed generic footprint's serpentine second-row numbering was not
reused. Link throws are 1/4, common VREF terminals 2/5, and OG supply throws 3/6.

The schematic contains two non-board power flags for ERC and 24 board
components/etched pads. TP1 through TP6 are excluded from the purchasing BOM
and remain on the board, matching their standard copper-pad footprints.
The other 18 components retain their BOM inclusion (four resistors are DNP).
The PCB adds its mechanical mounting holes separately.

After this BOM parity adjustment, the schematic was regenerated and comparison
confirmed exactly six `in_bom` changes with every exported net membership
unchanged. The 216-assertion connection audit and strict ERC both passed again;
PDF/SVG/PNG previews and both ERC reports were refreshed.

These results verify the CAD circuit. Physical mating, I2C pull-ups, existing
CAN termination, EEPROM identification contents, and firmware operation still
require the bench validation described in `../DESIGN.md` before release.
