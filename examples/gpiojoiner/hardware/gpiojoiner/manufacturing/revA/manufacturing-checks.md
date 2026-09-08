# Rev A manufacturing export checks

Generated 2026-09-08T23:23:16+00:00.
Independent Gerbonara CAM parser compared with the verified KiCad geometry.

- PASS: source schematic, PCB and project hashes match fresh CAD verification.
- PASS: eight Gerber graphic layers; twelve outline edges; 130 x 130 mm centerline bounds.
- PASS: all 162 drill positions and diameters match CAD within 0.000501 mm (158 plated, four non-plated).
- PASS: minimum hole edge gap 0.631 mm.
- PASS: 18 stencil apertures match the seven fitted SMD parts; all four DNP resistor positions omitted.
- PASS: IPC-D-356 parses 194 records: 138 electrical pads, 52 vias, four mounting holes.
- PASS: all 138 IPC pad coordinates match CAD within 0.0013 mm; exported net names preserve connectivity groups.
- PASS: both supplier BOMs contain seven exact-MPN lines, 14 fitted references and no DNP/TP/holes.
- PASS: JLCPCB CPL includes 14 fitted parts; PCBWay CPL includes seven SMD parts per its published file requirements. All listed coordinates, sides and rotations match CAD; common Gerber/drill/CPL datum.
- Generated independent top/bottom Gerber SVG previews for visual review. Use render_cam.mjs for PNGs (SVG filters require a compatible renderer).

The native IPC-D-356 uses 0.0001-inch resolution; its datum matches the metric Gerbers.
CPL values remain KiCad footprint datums; manufacturer placement overlays need review,
especially the connector bodies, switch and polarized parts. No assembly-machine
rotation corrections are guessed here. This is prototype quotation data; manufacturer
DFM acceptance, physical mating, EEPROM identity and bench operation are unverified.

## Parser observations

- gpiojoiner-NPTH.drl:12 "G90": G90 header statement found after end of header
- gpiojoiner-PTH.drl:16 "G90": G90 header statement found after end of header

KiCad emits G90 after the Excellon header. Gerbonara accepts and applies this
absolute-coordinate statement, while reporting its header placement. All drill
hits parsed and matched the CAD snapshot; the native KiCad drill files are retained.
