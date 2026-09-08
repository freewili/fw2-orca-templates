# ORCA KiCad agent instructions

These instructions adapt the user's ORCA KiCad project-type brief into a
repository workflow. Preserve the project-specific requirements below.

## ORCA workflow

- Use KiCad for FreeWili 2 GPIO expansion boards. Use
  https://github.com/freewili/fw2-orca-templates for reference examples,
  symbols and connector geometry. Check the actual device pinouts and
  component datasheets before reusing a symbol or footprint.
- Always include an ORCA identification EEPROM on I2C1 at the FreeWili 2
  10-position connector. The recommended part is 24LC02BT; verify its exact
  package pinout, power supply, pull-ups, write protection and bus ownership.
  Keep EEPROM hardware and its programming/identification status documented.
- Before starting routing, show the user the proposed circuit, board outline
  and component placement and let them review the board. Do not route until
  that review is complete. Existing reviewed routing does not need to be
  restarted when documenting or publishing an example.
- Launch a critic subagent to independently verify the work. Give it the
  requirements, source files and validation evidence. Resolve disagreements
  and material findings, and obtain agreement before advancing to the next
  stage or publishing. Record what was checked and any remaining limitations.
- Establish whether the user wants JLCPCB, PCBWay or both, and whether they
  want bare PCBs, partial assembly or fully assembled boards. Reuse choices
  already supplied in the conversation; ask only for missing preferences.
- Build the files needed for the chosen fabrication/assembly process:
  editable KiCad sources, local libraries and models, Gerbers, separate
  plated/non-plated drills, BOM, placement data, assembly/fit drawings and
  relevant programming/test instructions. Clearly identify DNP parts.
- Generate a board summary with the answers needed for a manufacturing
  quotation. For PCBWay, check https://www.pcbway.com/quotesmt.aspx and
  distinguish component counts per board from pads, pins and order totals.
  Include exact upload filenames, PCB specifications and assembly notes.
- Run ERC, DRC with schematic parity, and meaningful connection/footprint
  checks on the files being delivered. Inspect the schematic, board views
  and exported manufacturing data. Refresh exports after relevant CAD edits.
- Include useful board images in the example README: an angled view plus
  top/bottom views, with relative links that work after cloning the repository.
- Preserve third-party attribution and license notices. Keep machine-specific
  paths, personal instructions, caches, locks and editor backups out of the
  published example. Document any optional development-tool prerequisites.
- Distinguish CAD verification, supplier quotation, physical mating tests,
  EEPROM programming and bench validation. Do not describe an untested
  example as a proven production design or imply that an order was placed.

## GPIO Joiner requirements

- Use KiCad for the schematic and PCB.
- Provide four physical docking positions: two FreeWili 2 and two FreeWili OG.
  The user clarified that generally just two devices are connected. Rev A
  implements one device per electrical side; four simultaneously attached
  devices are unsupported without a future switching/isolation design.
- Arrange the devices as a four-arm star: the two FreeWili 2 devices opposite
  each other on one axis, and the two OG devices opposite each other on the
  perpendicular axis.
- Always include the ORCA identification EEPROM, using a 24LC02BT connected
  to I2C1 on the FreeWili 2 10-position connector: SCL on pin 7 and SDA on pin 9.
  Preserve this requirement through schematic, PCB, and BOM revisions.
- Use https://github.com/freewili/fw2-orca-templates as the reference, but
  verify symbols, footprints, and electrical connections against pinouts and
  component datasheets before reuse.
- Treat `gpiojoiner spec.md` as the source of truth for device-to-device
  wiring. `PINOUTS.md` defines connector pin assignments. Preserve the
  specified direct I2C1 connection when designing EEPROM identification.
- Rev A Side A is west FW2 or north OG; Side B is east FW2 or south OG.
  Use one device on each side. Preserve all four allowed generation pairings.
- Read `hardware/gpiojoiner/DESIGN.md` and the prototype setup instructions
  before changing the circuit. Preserve VREF source selection, independent
  supply isolation, and the documented 2:1 programmable-output readback.

Recorded from the user's requirements on 2026-09-08.

## Current example state

- Rev A is a routed prototype, with fabrication and assembly inputs for both
  JLCPCB and PCBWay. The current quote example uses five fully assembled
  boards; it is a working quantity, not a submitted purchase.
- See `hardware/gpiojoiner/manufacturing/PCBWAY-QUOTE-ANSWERS.md` for the
  form answers and `hardware/gpiojoiner/manufacturing/revA/README.md` for
  manufacturing settings, upload files and the remaining fit/bench checks.
- The EEPROM is fitted blank in the assembly BOM. No validated ORCA ID image
  or functional-test firmware is supplied. Do not imply automatic detection
  has been demonstrated.
