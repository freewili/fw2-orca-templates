# PCBWay quote-form answers — GPIO Joiner rev A

Checked 2026-09-08 against https://www.pcbway.com/quotesmt.aspx.
Working order: five PCBs, all five fully assembled. The component counts below
are per board. No form submission or order has been made.

## Assembly Service

| Field | Enter/select |
| --- | --- |
| Service option | Turnkey — PCBWay supplies all parts |
| Board type | Single pieces |
| Assembly side(s) | Top side |
| Quantity | 5 |
| Contains sensitive components/parts | Yes — use the handling note below |
| Accept alternatives/substitutes made in China? | No — exact BOM parts; review any proposed substitution separately |
| Select PCBWay's PCB Order# | No, unless you have since placed a separate PCB order for this revision |
| Add PO No. | Optional: GPIOJOINER-REVA-PROTOTYPE |
| Number of Unique Parts | 7 |
| Number of SMD Parts | 7 |
| Number of BGA/QFP Parts | 0 |
| Number of Through-Hole Parts | 7 |
| Depanel the boards to delivery | No for this single-piece quote; Yes if PCBWay changes to supplier panelization |
| Function test | No — no functional fixture/firmware supplied |
| Conformal coating | No |
| Firmware loading | No — EEPROM fitted blank |
| Press-fit assembly | No |
| Box build assembly | No |
| Cable wire harness assembly | No |
| Package box | Neutral box |
| Flying Probe Testing (assembly add-on) | No; request bare-PCB open/short electrical test in the notes |
| Number of X-ray test | 0 |

Counts exclude R5-R8 (DNP), copper test pads and mounting holes. The seven
SMD components have 18 solder pads; the seven THT components have 106 pins.
Enter **7 and 7** in the component-count fields, not 18/106 and not the
five-board totals. The form tooltips explicitly define these as parts per board.

Sensitive-component handling note (under the Yes selection):

> J1-J6: Sullins SFH11-PBPC-D10-RA-BK / SFH11-PBPC-D05-RA-BK, PBT housings. Fit after SMD reflow and observe Sullins soldering limits. SW1: C&K JS202011CQN; follow manufacturer soldering/cleaning instructions and verify contact states against the assembly drawing before fitting the batch.

The Sullins series has specified processing-temperature limits; this note
draws attention to the through-hole assembly sequence.
[Manufacturer datasheet](https://s3.amazonaws.com/catalogspreads-pdf/PAGE123%20.100%20SFH11%20SERIES%20FEMALE%20HDR%20ST%20RA.pdf).

Paste into **Detailed information of assembly**:

> GPIO Joiner rev A: quote five fully assembled boards, 14 fitted components per board (7 SMD and 7 through-hole), using the exact BOM. R5-R8 are DO NOT POPULATE. Fit U1 24LC02BT-E/OT blank; no EEPROM programming or functional-test firmware is supplied. Install SMD parts before the six outward-facing right-angle connectors and the slide switch. Connector bodies overhang the PCB: please confirm assembly fixture/temporary rail requirements and any extra charges. Deliver five individual boards. Use the assembly PDF for connector orientation, U1/D1 pin numbering and SW1 contact states. Verify SW1 left contacts 1-2 and 4-5, right contacts 2-3 and 5-6. The CPL lists the seven SMD parts; THT placement is in the drawing. Return placement/tooling previews and any engineering questions before production.

## PCB Specifications

Enable **PCB Specifications**, because no separate PCB order has been placed.

| Field | Enter/select |
| --- | --- |
| Board type | Single pieces |
| Different design in panel | 1, if displayed |
| Size (single) | Length 130 mm × Width 130 mm |
| Quantity (single) | 5 |
| Layers | 2 Layers |
| Copper layer / soldermask / silkscreen sides, if shown | Top and bottom; these controls may only appear for a one-layer board |
| Material | FR-4 |
| FR4-TG | S1000H TG150 / the standard TG150 option |
| Thickness | 1.6 mm |
| Min track/spacing | 5/5 mil |
| Min hole size | 0.3 mm ↑ — actual minimum drill is 0.4 mm |
| Solder mask | Green |
| Silkscreen | White |
| UV printing / Multi-color | None |
| Edge connector | No — this means PCB gold fingers, not the mounted GPIO connectors |
| Bevelling | No / not applicable |
| Surface finish | Immersion gold (ENIG) |
| Thickness of Immersion Gold | 2U" (2 microinches), recommended quote choice |
| Via process | Tenting vias; preserve the supplied mask Gerbers |
| Finished copper | 1 oz Cu |
| Inner Copper | Not applicable to a 2-layer PCB |
| Remove product No. | No — allow PCBWay's manufacturing identifier |
| Peelable soldermask | None |
| Hole copper thickness | Standard (20um) |
| UL marking | None |
| Date code | None — leave the existing design date unchanged |
| Package box | Neutral box |
| Add serial numbers | No / None |
| Serial Number Printing Location | Not applicable |
| Add PO No. | Optional: GPIOJOINER-REVA-PROTOTYPE |

Leave all other special-process boxes unchecked: castellations, edge plating,
impedance control, halogen-free, custom stackup, carbon ink, resin-filled/capped
vias, via-in-pad, press-fit holes, countersink/counterbore, Z-axis milling,
black FR4 core, embedded copper, cavities, semi-flex, hybrid PCB, back drilling,
selective hard-gold special processing and paper between boards.
Rogers/aluminum/copper-base parameters do not apply.

The actual routing is 0.20 mm track / 0.15 mm clearance (about 7.87/5.91 mil),
so choose the 5/5 mil category. The board outline is a cross; 130 × 130 mm is
its bounding box. Its vias are tented in the supplied mask files.

Paste into **Other special request**:

> GPIO Joiner rev A, five individual cross-shaped PCBs, 130 x 130 mm bounding box, 2-layer FR-4, 1.60 mm, 1 oz copper, green mask, white legend, ENIG 2 microinch gold. CNC-route the outline; no V-score. Normal internal router radii up to 1 mm are acceptable. Please review 0.15 mm copper spacing and 0.25 mm switch-pad annulus. There are 158 plated holes and four 3.2 mm NPTH mounting holes; minimum drill 0.4 mm. Bare-PCB open/short electrical test is required; IPC-D-356 is included. For assembly, please advise whether temporary rails, panelization or a fixture is required and return its drawing/cost before production. Do not relocate connectors or change the individual board geometry.

If PCBWay requests panelization after engineering review, change the assembly
Board type to Panelized PCBs and the PCB Board type to Panel by Supplier.
Select break-away rails Yes, one design, depanel for delivery Yes, and
X-out allowance Not Accept for this small prototype run. Ask PCBWay to choose
the panel arrangement/CNC tab routing. Continue to specify **five individual
finished boards**, not five panels; confirm any quantity change before payment.
Panel dimensions and tab locations are to be supplied by their engineer.

## File upload step

The prepared files are under `hardware/gpiojoiner/manufacturing/revA/`.

| Upload field | File |
| --- | --- |
| PCB / Gerber | `gpiojoiner-revA-gerbers.zip` |
| BOM | `assembly/pcbway-bom.csv` |
| Pick-and-place / centroid | `assembly/pcbway-cpl.csv` |
| Assembly drawing / other documents | `drawings/gpiojoiner-revA-manufacturing.pdf` |
| Schematic, if requested | `drawings/gpiojoiner-revA-schematic.pdf` |
| One combined assembly/reference upload, if offered | `gpiojoiner-revA-assembly.zip` |

Use the individual BOM and CPL CSVs in their designated inputs. PCBWay accepts
CSV BOMs and allows THT references to be omitted from the centroid when their
placement is otherwise documented.
[PCBWay assembly file guide](https://www.pcbway.com/smt_ordering_guide.html).

## Your account / shipping choices

- Email: your PCBWay account/contact email.
- Shipping destination/address: your actual receiving address.
- Shipping method: choose the service whose quoted cost and delivery time suit you.
- Build time: standard/non-expedited unless you need a deadline.
- Target price: leave blank.
- Content-policy/export declaration: read and confirm personally; it is not a CAD parameter.
- Review the itemized total including components, fabrication, assembly, tooling,
  shipping and tax. The initial assembly calculation is not the final turnkey price.

Check the 1:1 fit sheet against real devices and review the supplier's final
engineering/placement previews before ordering the prototypes.
