# GPIO Joiner - rev A review prototype

Open **gpiojoiner.kicad_pro** in KiCad 10 or newer. The schematic, PCB,
symbol library, footprints, and 3D models are included in this folder.
See [schematic PDF](previews/schematic.pdf), [board preview](previews/pcb-top.png),
[design details](DESIGN.md), and [BOM](BOM.md).

[Prototype manufacturing package and order settings](manufacturing/revA/README.md)
are prepared for JLCPCB and PCBWay, including Gerbers, exact-part BOMs,
supplier placement CSVs, and a 1:1 fit/assembly PDF. The working quantity is
five fully assembled boards. No supplier order or live quote has been submitted.

![Angled KiCad preview of GPIO Joiner rev A](previews/pcb-perspective.png)

| Top view | Bottom view |
| --- | --- |
| ![Top of the GPIO Joiner PCB](previews/pcb-top.png) | ![Bottom of the GPIO Joiner PCB](previews/pcb-bottom.png) |

These are CAD previews; full device enclosures and physical mating are not
verified. Optional R5-R8 models appear in the views but are DNP in the
prototype assembly BOM.

This revision implements the test cable described in the root
`gpiojoiner spec.md`. It has four docking positions in a star, intended
for **two attached devices: one on Side A and one on Side B**.

```text
                         OG A - J5
                            |
 FW2 A - J1 + J2 -------- JOINER -------- J3 + J4 - FW2 B
                            |
                         OG B - J6
```

| Test pair | Side A | Side B | SW1 position |
| --- | --- | --- | --- |
| FW2 / FW2 | West: J1 and J2 | East: J3 and J4 | FW2 / MIXED |
| OG / OG | North: J5 | South: J6 | OG / OG |
| FW2 / OG | West: J1 and J2 | South: J6 | FW2 / MIXED |
| OG / FW2 | North: J5 | East: J3 and J4 | FW2 / MIXED |

The two connector choices on a side share signals. Four simultaneously
attached devices, or two attached to the same side, are unsupported.
Supporting four attached devices would require added switching or isolation.

## Setup and tests

1. With both devices off, connect one device per side and set SW1.
2. In FW2 / MIXED mode, configure exactly one FW2 to supply VREF; the other
   device uses that external reference. In OG / OG mode, SW1 connects each
   OG's VREF to its own 3.3 V output. Change the switch with power off.
3. Power both devices before driving the shared interfaces. Configure GPIO
   directions and use one SPI clock/chip-select driver. UART/SPI data,
   UART flow control, and GPIO26/27 are crossed as specified.
4. For FW2 / FW2 analog tests, read AOUT0/1 on the other device's AIN0/1.
   Read programmable VOUT as **2 x the opposite AIN2 reading**. Two 10k/10k
   dividers accommodate the published 5.5 V programmable-output maximum.
   AIN3 and GPIO25 have labeled test pads only.

CAN connects only the two FW2 ports; OG SWD pins are unconnected. R7/R8 CAN
termination and R5/R6 I2C1 pull-ups are **DNP**. Check the devices' existing
termination and pull-ups before populating these optional resistors.

## ORCA identification

One **24LC02BT-E/OT** is permanently connected to the shared I2C1 bus on
both FW2 10-pin connectors (pin 7 SCL, pin 9 SDA). Its WP pin is grounded
for programming. A BAT54C diode OR powers it from either FW2's 3.3 V output
without directly joining those supply outputs.

Use a 3.3 V I2C1 bus, up to 400 kHz, with verified pull-ups. I2C1 voltage is
independent of the selected GPIO VREF. Reserve addresses **0x50 through
0x57**: this EEPROM ignores the three low address bits. Coordinate the two
hosts so only one controller accesses the bus at a time unless their
multi-controller behavior has been verified. The diode OR does not isolate
shared signal pins from an unpowered host.

The EEPROM hardware is included; a product-specific ORCA identification
image and a verified programming/boot procedure are still needed. No
identification contents or working auto-detection are claimed by this project.

## Physical and bench validation

The PCB is a 130 x 130 mm cross, two layers, 1.6 mm thick, with four 3.2 mm
mounting holes. FW2 20/10 connector centers are 26.72 mm apart, matching the
named starter template. The original example differs by 0.03 mm. Connector
centers are 3 mm inside the mating board edges. The included connector
models come from the template assembly; full device enclosures were not
available for clearance verification.

Before ordering the prototype, verify actual mating orientation, connector
gender/keying, spacing, board-to-case clearance, and support with real FW2
and OG devices. Check both SW1 contact states on the purchased part. The
project-local switch footprint corrects the installed library's reversed
second-row numbering using the manufacturer contact diagram.

Bench validation must also cover EEPROM supply voltage/read/write and
identification, both VREF modes, power sequencing, I2C pull-ups/ownership,
CAN termination, analog input loading/settling and divider calibration,
and the required test firmware for all four permitted pairs. Manufacturing
inputs are available for prototype quotation and engineering review; hardware
operation remains unverified and this is not a production release.

## Rechecking or regenerating

The editable KiCad files are the delivered design. For a full recheck,
run `tools/verify_project.py` with KiCad's bundled Python; it refreshes the
netlist, ERC/DRC, audits, and verification report. Alternatively, run the standard Python
`tools/check_connections.py` against a freshly exported KiCad XML netlist,
and run `tools/check_pcb.py` with KiCad's bundled Python (`pcbnew`). Also
run KiCad ERC and DRC with schematic parity enabled. Final reports belong
in `reports/`.

`generate_schematic.py` and `generate_pcb.py --rebuild` recreate the CAD
sources and **overwrite manual edits**. The PCB generator requires the
referenced template checkout and installed KiCad libraries. Rebuilding
removes routing. `route_pcb.py --java <java25> --jar <freerouting.jar>`
routes a board with no existing tracks and fills its ground pours.
`finish_routing.py` applies the local edge/thermal and label edits for the
delivered rev A routing; it is specific to those coordinates. A new router
run can produce different geometry and needs a fresh review and finishing
edits. Final KiCad DRC remains required. These development tools are optional for
opening and editing the delivered project.

Library origins and the source revision are recorded in [PROVENANCE.md](PROVENANCE.md).

Optional regeneration tools default to the Windows KiCad 10 install path.
Set `KICAD_INSTALL` for a different installation, and `KICAD_SYMBOL_DIR` when
the symbols are in a separate location. Verification accepts `--cli` for
the KiCad CLI path and needs Python with `pcbnew`. Opening the delivered
project does not require these development scripts or a template checkout.
