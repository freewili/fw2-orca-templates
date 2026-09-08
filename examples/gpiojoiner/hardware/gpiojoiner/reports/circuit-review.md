# Independent circuit review — 2026-09-08

Scope: DESIGN.md, source wiring specification, PINOUTS.md, exported KiCad
netlist, generated PCB and generators, and manufacturer documentation.
Mechanical mating and firmware/bench behavior remain outside CAD verification.

## Important finding: switch footprint numbering

C&K's JS-series datasheet (22 Sep 2022), page 4 / I-53, explicitly shows
JS202011CQN state b closing **1–2 and 4–5**; the other state closes
**2–3 and 5–6**. DESIGN.md uses these correct manufacturer contact pairs.
The installed KiCad footprint instead places row 6/5/4 opposite row
1/2/3. Reusing that numbering would select opposite throws between poles.
Use the project-local corrected footprint, with 4 opposite 1 and 6 opposite
3. Keep the schematic and contact simulation in manufacturer numbering.
The final project-local footprint and placed board now have this correction:
terminals 1/4 share x=147.5 mm, terminals 3/6 share x=152.5 mm, and commons
2/5 share x=150 mm. Correct throw/common nets were independently inspected.
Confirm both states by continuity on a physical switch before assembly
release. The datasheet mechanically marks terminal 1 only.

Source: [C&K manufacturer datasheet, distributor mirror](https://datasheet.lcsc.com/datasheet/pdf/418f5deccdcf85a20b545dc49037ad89.pdf?productCode=C221657).
The review visually inspected the rendered page, not just extracted text.

## Findings and operating conditions

- **Port mapping passes.** The four allowed A/B pairings implement the
  prescribed SPI/UART/GPIO crosses, straight I2C0, and FW2-only CAN.
  OG SWD remains disconnected. One device per side is essential because
  alternative docking positions share signal copper.
- **VREF topology is correct once the footprint is corrected.** Linked
  mode requires exactly one FW2 voltage source and the other device in
  external-reference mode. OG/OG mode keeps the two 3.3 V outputs separate.
  Power off before changing the mode or connecting devices.
- **EEPROM pinout and supply polarity pass.** SOT-23 pins are
  1=SCL, 2=GND, 3=SDA, 4=VCC, 5=WP. BAT54C pins 1/2 are anodes and pin 3
  is the shared cathode. Its voltage drop leaves reasonable nominal
  headroom from 3.3 V above the EEPROM's 2.5 V minimum; measure VCC during
  reads and writes from either FW2 alone. Diode OR prevents a direct
  supply-output short but does not isolate shared signal pins.
- **Document I2C1 operating limits.** Use at most 400 kHz. The EEPROM
  responds at every address 0x50–0x57, so reserve the entire range. Verify
  3.3 V bus levels independently of selectable VREF: EEPROM absolute
  maximum input voltage is VCC+1 V. Coordinate the two controllers during
  identification; simultaneous independent boot scans need firmware
  arbitration or sequencing. DNP pull-ups are reasonable for this review
  prototype, but fit/enable verified pull-ups before expecting operation.
- **Analog topology passes with a calibration condition.** Each 10k/10k
  divider gives 2.75 V nominal at 5.5 V PROG VOUT, approximately 5 kohm
  source impedance and 0.275 mA load. Firmware must apply the documented
  factor of two. Verify ADC loading/settling and gain with a known voltage;
  the published interface data does not establish input impedance here.
  AOUT0/1 cross to opposite AIN0/1. AIN3 stays unspecified/test-point only.
- **Firmware directions remain part of safe operation.** Straight SPI
  CS/clock require only one output driver. Both attached hosts should be
  powered before driving the shared interfaces; partial-power behavior
  has not been established. Existing CAN termination and I2C pull-ups
  must be measured as already required by DESIGN.md.

Sources: [Microchip 24LC02B](https://ww1.microchip.com/downloads/en/DeviceDoc/24AA02-24LC02B-24FC02-Data-Sheet-20001709L.pdf),
[Nexperia BAT54C](https://assets.nexperia.com/documents/data-sheet/BAT54C.pdf),
[FreeWili pinout and analog ranges](https://docs.freewili.com/hardware/pinout/),
[FreeWili programmable power](https://freewili.com/specs/programmable-power.html).

## Final CAD review checks

- `python hardware/gpiojoiner/tools/check_connections.py` passed
  **216 assertions**, four pairings, both modeled switch states and
  37 exact copper-net groups.
- KiCad Python `check_pcb.py` passed **138 schematic pad/net assignments**,
  connector spacing/orientation, corrected switch, DNPs, holes and local models.
- Independently compared both local ORCA footprint pad coordinates, sizes
  and drills against normalized upstream template footprints: exact matches.
  FW2 connectors are rotated together and remain 26.72 mm apart. Mating
  faces point west/east for FW2 and north/south for OG, based on the
  template body orientation. These comparisons cannot establish enclosure fit.
- Independently inspected placed D1 and U1 pad/net assignments: correct.
- Existing strict ERC report contains zero violations.

## Final routing and documentation review

The final `drc.json`, dated 2026-09-08 17:24:24, reports **zero violations,
zero unconnected items, and zero schematic-parity discrepancies**. Its
configured ignored checks are listed in that JSON; electrical connectivity
and copper-clearance checks are enabled. Earlier incomplete routing,
edge-clearance errors and thermal issues are resolved, not accepted exceptions.

The board contains 509 track segments at 0.20 mm width and 52 vias. Its
configured minimum copper clearance is 0.15 mm and copper-edge clearance
is 0.30 mm. This agrees with DESIGN.md and allows escape through the
source connector footprints' 0.508 mm pad gaps. Ground is routed explicitly
and has filled zones on both copper layers. Local endpoint, jog and thermal
adjustments are recorded in `tools/finish_routing.py`.

Fresh final-board checks again passed 216 schematic assertions and 138
PCB pad/net assignments. README.md, BOM.md, DESIGN.md and PROVENANCE.md
agree on the four pairings, VREF modes, shared EEPROM, divider calibration,
optional DNP parts and prototype limitations. BOM totals are correct:
14 normally populated parts, four optional resistors, six copper test pads
and four mechanical holes. Connector part numbers match the named upstream
starter; that verifies provenance rather than physical mating.

The board preview was visually inspected. A reversed apparent order in
combined connector labels was identified and corrected: each J1/J2/J3/J4
label now has the corresponding connector-center y coordinate in the CAD.
Regeneration remains a development workflow requiring fresh DRC; its
coordinate-specific finishing helper is not a general routing repair tool.

**Assessment:** no outstanding substantive electrical/CAD findings for
this review prototype. The physical mating, switch continuity and firmware/
bench conditions above remain required before manufacturing release.
