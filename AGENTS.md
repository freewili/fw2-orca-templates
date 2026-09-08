# ORCA KiCad agent instructions

These instructions adapt the ORCA KiCad project-type brief into a workflow
for this repository. Follow additional AGENTS.md files inside each example
for its project-specific electrical and mechanical requirements.

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
