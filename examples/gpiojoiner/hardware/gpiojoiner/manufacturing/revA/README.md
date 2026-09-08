# GPIO Joiner rev A - prototype manufacturing package

Prepared 2026-09-08 for **five fully assembled prototypes** as a working quote
quantity. These are manufacturing inputs for supplier quotation and engineering
review. No supplier upload, quote, purchase, physical mating test or bench test
has been completed.

The board has four docking positions but supports **two connected devices,
one per electrical side**. The 24LC02BT EEPROM is included on the shared
FW2 I2C1 bus. It will arrive blank unless a separately validated image and
programming service are added to the order.

## Files to use

| File | Use |
| --- | --- |
| `gpiojoiner-revA-gerbers.zip` | Upload to the PCB fabrication Gerber input. Eight Gerber layers, separate PTH/NPTH drill files and IPC-D-356 electrical test netlist. |
| `gpiojoiner-revA-assembly.zip` | Complete quote/reference package. Unzip and use its supplier-specific BOM and CPL files in the assembly inputs. |
| `assembly/pcbway-bom.csv` | PCBWay turnkey BOM: seven line items, 14 components per board. Quantities are per board. |
| `assembly/pcbway-cpl.csv` | PCBWay centroid: seven SMD parts only, as requested by its file guide. Through-hole locations are in the assembly drawing. |
| `assembly/jlcpcb-bom.csv` | JLCPCB BOM with exact MPNs and LCSC catalog numbers. |
| `assembly/jlcpcb-cpl.csv` | JLCPCB placement file: all 14 fitted components. |
| `drawings/gpiojoiner-revA-manufacturing.pdf` | Three-page 1:1 fit sheet, complete assembly layout, component orientation and fabrication notes. |
| `manufacturing-checks.md` | Independent checks of the exported files against the verified CAD. |
| `SHA256SUMS.txt` | Content checksums, including the verified source CAD revision. |

Only the named ZIP is intended for the PCB Gerber uploader. The development
`checks/` directory contains temporary build data and is excluded from both ZIPs.
The Gerber paste layer has **18 apertures** for the seven fitted SMD parts;
there are no stencil apertures at R5-R8 and no bottom-side paste file.

## Quote settings

| Setting | Selection |
| --- | --- |
| Quantity | 5 finished boards; assemble all 5 (working assumption) |
| PCB | Rigid FR-4, 2 copper layers, 1.60 mm finished thickness |
| Size | 130 x 130 mm bounding box; one cross-shaped PCB design |
| Copper | 1 oz / 35 micrometers on each outer layer |
| Finish | Lead-free ENIG |
| Solder mask / legend | Green mask; white legend on both sides |
| Profile | CNC routed; no V-score, castellations, edge plating or controlled impedance |
| Corners | Normal internal routing radii up to 1 mm acceptable |
| Holes | 158 plated: 100 connector pins, 6 switch pins, 52 vias; 4 non-plated 3.2 mm support holes |
| Via treatment | Solder mask as supplied; no resin filling or via-in-pad process |
| Electrical test | Required; use supplied IPC-D-356 and Gerbers |
| Assembly | Lead-free, top side; 7 SMD + 7 through-hole components per board |
| Optional parts | R5, R6, R7, R8: DO NOT POPULATE |
| Programming / functional test | Not included; U1 blank; no test firmware or factory fixture supplied |
| Panelization | Supplier to propose temporary rails, fiducials, tabs and assembly tooling; deliver depanelized boards |

The routed design uses 0.20 mm tracks, 0.15 mm copper clearance, 0.30 mm
copper-to-edge clearance, 0.4 mm via drills in 0.8 mm pads, and a minimum
0.25 mm annulus at the switch pins. Minimum legend size is 1.0 mm with
0.15 mm strokes. Keep the quoted copper at **1 oz**: JLCPCB's published
2 oz spacing requirement is larger than this board's clearance.
[JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities).

For PCBWay, request engineering confirmation of **0.15 mm spacing and
0.25 mm component-hole annulus** against the chosen service; do not assume
its lowest-cost 6 mil spacing / 10 mil annulus process applies. Its capability
table includes finer options. [PCBWay capabilities](https://www.pcbway.com/capabilities.html).

## Supplier workflow

1. Print page 1 of the manufacturing PDF at **100% / Actual size** on US
   Letter paper. Confirm both axes of the 50 mm calibration square. Compare
   actual connectors and FW2/OG devices with the hole pattern: pin 1, gender,
   key, mating direction, 26.72 mm FW2 connector spacing, and enclosure clearance.
   The drawing does not represent the device cases.
2. Upload the Gerber ZIP and select the settings above. Choose PCB assembly
   and upload that supplier's BOM/CPL pair plus the manufacturing PDF.
   For a full-service quote, request all components sourced and fitted.
3. Request mixed SMD/through-hole assembly, including all six outward-facing
   connectors and the switch. Their bodies overhang the outline. Let the
   factory propose hand soldering, selective/wave soldering and any fixture.
   Review the panel/tooling drawing before releasing production.
4. Check every supplier-selected MPN, quantity and placement overlay. Compare
   U1/D1 pin 1 and SW1 numbering with page 3. Native KiCad footprint origins
   are used: through-hole datums are not necessarily plastic-body centers.
   Align connector models to the drilled pad pattern. Do not accept automatic
   substitutions or guessed placement-rotation offsets.
5. Confirm the actual switch has the documented contact states: left 1-2 and
   4-5; right 2-3 and 5-6. This can be checked on a sample switch, or requested
   as an assembler first-article check before fitting the batch. Then review
   the itemized total, parts availability, lead time and shipping before payment.

PCBWay's published file guide supports the supplied RS-274X Gerbers, CSV
turnkey BOM and SMD-only centroid. Additional assembly drawings are expressly
recommended. [PCBWay file requirements](https://www.pcbway.com/assembly-file-requirements.html).
JLCPCB's KiCad guide specifies the BOM/CPL columns used here.
[JLCPCB KiCad export guide](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad).

Exact catalog references are recorded in each PCBWay BOM source cell and in
`parts.json` inside the complete package. Catalog presence does not establish
current stock, service eligibility, price or delivery date. A live quote must
confirm all of these, particularly the through-hole connector fixture/assembly.

## Notes to include with the quote

> Please quote five GPIO Joiner rev A prototypes, fully turnkey, with all
> fourteen listed components fitted per board. This is a 130 x 130 mm cross,
> 2-layer FR-4, 1.6 mm, 1 oz copper, green mask, white legend, ENIG. Seven
> parts are SMD and seven are through-hole. The six right-angle connectors
> overhang the board. Please review 0.15 mm copper spacing, 0.25 mm switch-pad
> annulus, panel/fixture needs, connector orientation and all polarized parts.
> R5-R8 are DNP. Fit the EEPROM blank; programming and functional test are
> not supplied. Please return an itemized quote, availability, engineering
> questions, and placement/panel previews for review before production.

This is prepared text; it has not been sent to either supplier.

## After the prototypes arrive

Inspect one board and check continuity before connecting devices. Validate
VREF selection, EEPROM supply/read/write, I2C pull-ups and ownership, CAN
termination, and analog divider behavior with controlled bench bring-up.
Use one device per side and change SW1 with power off. Programmable VOUT
readback is twice the opposite AIN2 value. A product-specific ORCA ID image
and boot-detection test remain to be developed. Bench validation is required
before treating this revision as a production design.

## Reproduce

Run `tools/verify_project.py` with KiCad Python, then
`tools/export_manufacturing.py` with the same Python. The exporter refuses
CAD hashes not present in the verification report. Run `build_assembly.mjs`
with Node and an artifact-tool runtime, `make_manufacturing_drawings.py`
with ReportLab, `check_manufacturing.py` with Gerbonara, and `render_cam.mjs`
with Node/sharp. Visually inspect the PDF, supplier tables and Gerber views,
then run `package_manufacturing.py` with standard Python. These scripts live
in `hardware/gpiojoiner/tools/`; regeneration replaces generated outputs.
