# CAD source provenance

- Wiring authority: user-provided `gpiojoiner spec.md` in the repository root.
  Physical pin assignments: root `PINOUTS.md`. Design decisions beyond the
  cable notes are identified in [DESIGN.md](DESIGN.md).
- ORCA reference: [freewili/fw2-orca-templates](https://github.com/freewili/fw2-orca-templates),
  commit `f8f26dfa2b6454a27f454f303fe2a669ac94eca2`.
  The two `GPIOJoiner:ORCA_*_RA` footprints derive from the embedded
  connectors in `kicad/ORCATemplate.kicad_pcb`. Pad coordinates, sizes,
  numbering, and drills are preserved. Courtyards, corrected through-hole
  attributes, and local model references were added; original corner marks
  were moved to the fabrication layer.
- `models/ORCA_20_RA.step` and `ORCA_10_RA.step` are connector solids extracted
  from `kicad/ORCATemplate.step` and translated to footprint coordinates.
  They describe connectors, not complete FreeWili enclosures. The upstream
  checkout did not contain a separate license file; no new upstream license
  is asserted here.
- Other footprints and their STEP models originate from the installed
  KiCad 10 library distribution. KiCad library assets use CC BY-SA 4.0
  with the KiCad design exception; see the [KiCad library license](https://www.kicad.org/libraries/license/).
  Symbols in `GPIOJoiner.kicad_sym` were authored for this project using
  the interface pin assignments and manufacturer component pinouts.
- `GPIOJoiner:SW_JS202011CQN` derives from KiCad's
  `Button_Switch_THT:SW_CK_JS202011CQN_DPDT_Straight`, with pad numbers
  4 and 6 exchanged to make rows 1/2/3 and 4/5/6 parallel. This follows
  the manufacturer's contact diagram, reviewed in
  [circuit-review.md](reports/circuit-review.md). Verify on the physical part.

KiCad 10.0.6 exported the schematic netlist, ERC, DRC, and previews.
Freerouting 2.2.4 / Java 25 performed local routing; no remote routing
service was used. Routing inputs and its log are retained under
`reports/routing/`; final KiCad DRC, not the router's score, establishes
the reported CAD connectivity and clearance result.
