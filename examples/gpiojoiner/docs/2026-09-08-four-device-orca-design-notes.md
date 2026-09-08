# Four-position ORCA GPIO joiner: initial reference audit

**Superseded by the rev A KiCad prototype:** the user clarified that
generally two devices are connected. The implemented board uses one
device on Side A (west FW2 or north OG) and one on Side B (east FW2 or
south OG). See [current design](../hardware/gpiojoiner/DESIGN.md),
[setup instructions](../hardware/gpiojoiner/README.md), and the updated
[pair connection matrix](pair-connection-matrix.md).

The historical notes below record the initial reference audit before the
schematic and PCB were created. Their open choices have since been resolved
in DESIGN.md, except physical mating and the explicitly listed bench tests.

## Requested physical arrangement

One PCB directly mates with up to two FreeWili 2 and two FreeWili OG devices.
Each generation occupies opposite arms of a four-arm star. Conceptual top
view, with devices extending outward from the PCB:

```text
                       FreeWili OG A
                            |
                         20-pin
                            |
 FreeWili 2 A -- 20+10 -- JOINER -- 20+10 -- FreeWili 2 B
                            |
                         20-pin
                            |
                       FreeWili OG B
```

The lines show physical placement, not common electrical nets. This means
four 20-position mating connectors and two 10-position mating connectors.
Connector gender, key orientation, exact part numbers, enclosure clearance,
and mechanical support must be verified before fixing the board dimensions.

## Reference inspection

Inspected upstream commit `f8f26dfa2b6454a27f454f303fe2a669ac94eca2` from
[fw2-orca-templates](https://github.com/freewili/fw2-orca-templates).
Local KiCad CLI version: 10.0.6. Both upstream schematics exported to XML
netlists successfully, and both PCB files loaded through KiCad's Python API.
These are reference readability checks, not electrical or layout approval.

- `kicad/ORCATemplate.kicad_sch` instantiates only CN1 and CN2. The EEPROM
  footprint is supplied separately; the starter does not already contain
  the mandatory EEPROM circuit.
- `examples/ORCA_NRF/ORCA_NRF.kicad_sch` contains a wired EEPROM. Its exported
  netlist confirms the four signal/power connections in the table below.
- Connector footprints are embedded in the reference PCB files. The starter
  footprint table uses unavailable absolute library paths and duplicate
  entries; the project must use self-contained, project-relative libraries.
- Reference 3D model paths also point to another machine. The available
  ORCATemplate STEP file must be inspected before assuming it provides the
  complete device/enclosure mating geometry.
- The starter's 20-pin and 10-pin footprint centers are 26.72 mm apart; the
  NRF example uses 26.69 mm. Their pitch is 2.54 mm with 1.1 mm drills.
  These measured file values need a mechanical source of truth; do not
  silently choose between the differing center spacings.

## Mandatory identification EEPROM

The user requires a 24LC02BT on I2C1 of the 10-position connector, and the
user-designated wiring specification requires direct I2C1 connection
between the FW2 devices. Proposed implementation: one 24LC02BT-E/OT on
that shared bus. The supply circuit must allow the supported device
combinations without paralleling the two hosts' 3.3 V outputs.

| EEPROM SOT-23 pin | Function | Proposed connection |
| --- | --- | --- |
| 1 | SCL | Shared FW2 10-position pin 7, I2C1 SCL |
| 2 | VSS | GND, including 10-position pin 1 and 20-position pins 19/20 |
| 3 | SDA | Shared FW2 10-position pin 9, I2C1 SDA |
| 4 | VCC | Board EEPROM supply; source selection circuit to be designed |
| 5 | WP | Defined logic level; proposed GND for EEPROM programming |

The example labels pin 5 as NC and leaves it unconnected. Microchip's
DS20001709L Table 2-1 specifies WP on SOT-23 pin 5, and section 2.4 requires
WP to be tied to VSS or VCC. Correct the reused symbol and connection.
Provide local supply decoupling and establish the actual host I2C1 pull-up
voltage/resistance before selecting additional pull-ups.

Section 5.0 of the datasheet specifies three ignored address bits. These
EEPROMs therefore respond to the same address range (0x50-0x57); assigning
different software addresses cannot separate two parts on one bus. Use
one shared EEPROM for the proposed shared-bus design. Define host bus
ownership, pull-up supply, and unpowered-host behavior. The earlier
separate-bus recommendation is superseded by the user's wiring specification.

The EEPROM identification data format and programming procedure also need
to be established before claiming ORCA auto-detection works.

Source: [Microchip 24AA02/24LC02B/24FC02 datasheet, sections 2 and 5](https://ww1.microchip.com/downloads/en/DeviceDoc/24AA02-24LC02B-24FC02-Data-Sheet-20001709L.pdf).

## Electrical topology decision

The user-designated `gpiojoiner spec.md` defines two-device GPIO testing, including
UART and SPI RX/TX swaps, UART flow-control swaps, GPIO26/GPIO27 pairing,
and generation-dependent VREF handling. It does not define four-device
routing. Its signal wiring is captured in the
[pair connection matrix](pair-connection-matrix.md). Possible applications
of that established pair wiring to four physical ports are:

1. Select any two connected devices as test partners. This retains mixed
   FW2/OG testing. Manual selection or an active switch network would need
   its own design decision.
2. Run two fixed pairs, FW2-to-FW2 and OG-to-OG. This is the simplest passive
   routing but does not provide mixed-generation testing.
3. Have all four communicate together. This needs a protocol-specific
   arrangement and output ownership, rather than treating every signal
   as a shared four-device bus.

The initial recommendation for the existing test-cable use case is option
1, subject to the user's intended test workflow. No option is selected yet.

## Constraints on the eventual circuit

- Keep independent 5 V, 3.3 V, and programmable supply outputs from being
  directly paralleled. A VREF source/selection scheme must follow the
  selected pair and the device configurations.
- FW2 20-position pin 16 is CAN L and pin 18 is CAN H in the project's
  connector drawings and upstream example. The corresponding OG pins are
  SWCLK and SWDIO. Keep CAN routing exclusive to the FW2 ports.
- Configure signal directions before testing. UART TX, RTS, GPIO outputs,
  and SPI clock/chip-select drivers cannot be blindly joined across hosts.
  Confirm the original SPI RX/TX swap against the intended firmware test
  modes before adopting it as schematic wiring.
- The existing cable notes request analog output-to-input and programmable
  output-to-input tests. Verify voltage limits and necessary scaling before
  connecting PROG VOUT to an analog input. AIN3 and GPIO25 test coverage
  remain to be defined.
- Correct inherited symbol naming: 20-position pin 11 is UART RTS even
  though the example calls it UART1_Tx; 10-position pin 10 is PROG VOUT in
  the project pinout but INT_IO_VREF in the example symbol.
- Establish ground and return paths, including the FW2 CAN interface's
  isolation/grounding and termination requirements, from the device hardware.

Project pin assignments: [PINOUTS.md](../PINOUTS.md).
Additional context: [FreeWili pinout documentation](https://docs.freewili.com/hardware/pinout/)
and [ORCA module documentation](https://docs.freewili.com/hardware/orca-modules/).

## Verification before fabrication

The eventual KiCad project needs a checked connection matrix, schematic
ERC, PCB DRC, schematic/PCB consistency checks, connector mating and
enclosure clearance verification, and reviewed manufacturing outputs.
Bench validation must cover each supported populated-device combination,
power sequencing, ORCA identification, and the selected GPIO/bus tests.
No such fabrication or hardware validation is claimed by this audit.
