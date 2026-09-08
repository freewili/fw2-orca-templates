# GPIO Joiner rev A

## Scope and operating arrangement

Build a KiCad schematic and PCB for the user's passive two-device GPIO test
cable, with four physical docking positions. User clarification: generally
only two devices are connected. Use one device on Side A and one on Side B.
West FW2 and north OG are Side A; east FW2 and south OG are Side B. Both
FW2 and both OG devices are opposite their own generation. The two mixed
pairs are west FW2/south OG and north OG/east FW2. Four attached devices,
or two on the same side, are not supported in this passive revision.

The user's `gpiojoiner spec.md` is the wiring authority. The root
`PINOUTS.md` supplies physical pin numbers. Reference connector geometry
comes from freewili/fw2-orca-templates commit
f8f26dfa2b6454a27f454f303fe2a669ac94eca2.

## Circuit

- J1: FW2 A 20-pin; J2: FW2 A 10-pin; J3: FW2 B 20-pin;
  J4: FW2 B 10-pin; J5: OG A 20-pin; J6: OG B 20-pin.
- Side A J1/J5 share GPIO interface signals, with individual 3.3 V outputs.
  Side B J3/J6 likewise. 5 V outputs are unconnected. OG SWD pins 16/18
  are unconnected. FW2 CAN L/H join only J1 and J3 pins 16/18.
- Cross between sides: SPI 13/12, UART 9/5 and 11/7, GPIO 3/14.
  SPI CS 1/1, clock 15/15, I2C0 8/8 and 10/10 are straight-through.
  GPIO25 pin 17 is brought to one test point per side, not cross-connected.
- All paired digital/analog grounds are common.
- A DPDT VREF mode switch SW1 has commons 2=VREF_A and 5=VREF_B.
  Throws 1 and 4 share a link net (FW2/mixed mode); throw 3 connects only
  OG A 3.3 V and throw 6 only OG B 3.3 V (OG/OG mode).
  Part: C&K JS202011CQN with corrected project-local THT footprint
  GPIOJoiner:SW_JS202011CQN. Pins 4/6 are exchanged from the installed
  library footprint so 4 is opposite 1 and 6 opposite 3, following the
  manufacturer's contact diagram. Verify continuity before assembly release.
  Change mode with both devices off. FW2/mixed uses exactly one FW2 IO
  voltage source; OG/OG gives each side its own local 3.3 V reference.
- J2/J4 I2C1 pins 7 and 9 connect directly as requested.
  U1 is one shared 24LC02BT-E/OT: 1=SCL, 2=GND, 3=SDA, 4=VCC, 5=WP.
  WP is tied to GND so the EEPROM can be programmed. Two independent FW2
  3.3 V outputs feed BAT54C common-cathode D1 pins 1/2; pin 3 supplies U1.
  C1=100 nF decouples U1. R5/R6=4.7k I2C1 pull-ups are DNP pending host
  pull-up measurement. Never fit two unisolated 24LC02B parts to this bus.
- Analog connections in both directions: AOUT0 pin 5 to opposite AIN0 pin 8;
  AOUT1 pin 3 to opposite AIN1 pin 6.
- PROG VOUT can reach 5.5 V while the published ADC range is 0–5 V. Use
  a 10k/10k divider for each PROG VOUT to opposite AIN2 pin 4 path:
  R1/R2 for A-to-B and R3/R4 for B-to-A. Firmware recovers VOUT as
  twice the AIN2 reading. Use 0.1% resistors, 0603 footprints.
- AIN3 pin 2 has a test point per FW2; the source says `xxx`, so no
  stimulus is invented. No automatic CAN termination is fitted; provide
  DNP 120-ohm termination footprints R7/R8 near each FW2 connector,
  populated only after checking the devices' existing termination.

## Mechanical draft

Use the template's embedded 20-pin/10-pin right-angle connector footprints
with project-local libraries. Preserve 2.54 mm pitch and template FW2
connector-center separation 26.72 mm. The NRF example differs by 0.03 mm;
use the named starter template consistently and flag mating verification.

Initial outline: a 130 x 130 mm four-arm cross, 80 mm wide arms, two copper
layers, 1.6 mm thickness. Four 3.2 mm support holes in the central area.
Connector centers are 3 mm inside their mating board edges. Route with
0.20 mm tracks, 0.15 mm copper clearance, and 0.30 mm copper-edge clearance;
this permits signal escape through the template's 0.508 mm pad gaps.
Place connector mating faces outward. Clearly mark side, generation,
pin 1, mode switch positions, and ONE DEVICE PER SIDE / TWO DEVICES ONLY.
Connector body and device-case clearance need physical mating validation;
the template STEP model is not a verified complete FW2 or OG enclosure.

## Deliverables and verification

Create project-local symbols/footprints, editable schematic and routed PCB,
BOM, schematic PDF/SVG and board previews, connection audit and ERC/DRC
reports. At the user's request, provide prototype manufacturing/assembly
inputs for JLCPCB and PCBWay with exact part numbers, fit drawings and
independent CAM checks. These are quotation and prototype-order inputs;
they do not establish production readiness. Verify physical mating before
ordering. Validate pull-ups, CAN termination, EEPROM identification contents,
and firmware operation on the prototypes before production release.

Manufacturing presentation uses at least 1.0 mm silkscreen text height and
0.15 mm strokes. Plot/drill/assembly datum is the lower-left board bounding
box corner, KiCad (85, 215) mm. Order specification: 1 oz copper, ENIG,
green mask and white legend. Solder-paste output omits DNP R5-R8 apertures.

Verify every specified A/B pin connection on exported KiCad netlists,
including all four permitted combinations, supply isolation, both switch
modes, EEPROM pins, and analog divider topology. Check PCB/schematic pad
net agreement, ERC, DRC, and visually inspect schematic and PCB exports.

## Sources

- https://github.com/freewili/fw2-orca-templates
- https://ww1.microchip.com/downloads/en/DeviceDoc/24AA02-24LC02B-24FC02-Data-Sheet-20001709L.pdf
- https://assets.nexperia.com/documents/data-sheet/BAT54C.pdf
- https://freewili.com/specs/programmable-power.html
- https://docs.freewili.com/hardware/pinout/

The divider, manual VREF switch, spare-pin test points, DNP pull-ups and
termination pads are design choices made to implement the source safely
and keep the first board useful for validation.
