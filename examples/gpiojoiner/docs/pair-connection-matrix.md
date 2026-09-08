# GPIO joiner pair connection matrix

Derived from the user-designated wiring specification,
[`gpiojoiner spec.md`](../gpiojoiner%20spec.md), and the physical pin assignments
in [`PINOUTS.md`](../PINOUTS.md).

A and B identify the two devices taking part in a test. Rev A assigns
west FW2 (J1/J2) and north OG (J5) to Side A, and east FW2 (J3/J4) and
south OG (J6) to Side B. Use only one device on each side.
All arrows below represent physical connections; the signal names describe
the intended test direction. GPIO and SPI directions must be configured
for the chosen test before enabling their output drivers.

## 20-position connectors

| Function | Device A pin | Device B pin | Requirement |
| --- | ---: | ---: | --- |
| SPI A TX to B RX | 13 | 12 | RX/TX swap specified by user |
| SPI B TX to A RX | 12 | 13 | RX/TX swap specified by user |
| SPI chip select | 1 | 1 | Straight-through interpretation of SPI connection |
| SPI clock | 15 | 15 | Straight-through interpretation of SPI connection |
| UART A TX to B RX | 9 | 5 | RX/TX swap |
| UART B TX to A RX | 5 | 9 | RX/TX swap |
| UART A RTS to B CTS | 11 | 7 | RTS/CTS swap |
| UART B RTS to A CTS | 7 | 11 | RTS/CTS swap |
| I2C0 SCL | 8 | 8 | Direct connection |
| I2C0 SDA | 10 | 10 | Direct connection |
| GPIO27 A to GPIO26 B | 3 | 14 | GPIO26/GPIO27 pairing |
| GPIO27 B to GPIO26 A | 14 | 3 | Reciprocal interpretation of pairing |
| CAN L | 16 | 16 | FW2-to-FW2 only; disconnected for OG or mixed pairs |
| CAN H | 18 | 18 | FW2-to-FW2 only; disconnected for OG or mixed pairs |
| VREF | 4 | 4 | Connected for a pair containing FW2; one FW2 supplies IO voltage |
| Ground | 19, 20 | 19, 20 | Common return for the paired GPIO interfaces |
| 5 V outputs | 2 | 2 | No direct A-to-B connection specified; keep separate |
| 3.3 V outputs | 6 | 6 | Keep supplies separate; local use for OG VREF and EEPROM power |
| GPIO25 | 17 | 17 | No test connection specified |

SPI clock/chip select sharing requires compatible drive modes. The user
explicitly specifies crossed SPI data; this table preserves that test
wiring. It must not be silently changed to conventional peripheral wiring.

### VREF configuration

- **FW2/FW2 or FW2/OG:** connect pin 4 between the selected devices. Configure
  one FW2 as the IO-voltage source and the other device to use that reference.
- **OG/OG:** disconnect the pin-4 link and connect each OG's pin 4 to its own
  pin 6 (3.3 V), following the specification's local-supply instruction.
  This avoids paralleling the two 3.3 V outputs through VREF.
- Provide a clearly labeled board selection mechanism for these modes.
  The spec explicitly requires checking this change when switching device
  combinations. Source choice and signal connectivity must agree.

## 10-position connectors (FW2-to-FW2)

| Function | Device A pin | Device B pin | Requirement |
| --- | ---: | ---: | --- |
| I2C1 SCL | 7 | 7 | Direct connection required by specification |
| I2C1 SDA | 9 | 9 | Direct connection required by specification |
| A AOUT0 to B AIN0 | 5 | 8 | Output-to-input test |
| B AOUT0 to A AIN0 | 8 | 5 | Reciprocal interpretation of test |
| A AOUT1 to B AIN1 | 3 | 6 | Output-to-input test |
| B AOUT1 to A AIN1 | 6 | 3 | Reciprocal interpretation of test |
| A PROG VOUT to B AIN2 | 10 | 4 | Through a 10k/10k divider; measurement = 2 x B AIN2 |
| B PROG VOUT to A AIN2 | 4 | 10 | Through a 10k/10k divider; measurement = 2 x A AIN2 |
| Ground | 1 | 1 | Common return |
| AIN3 | 2 | 2 | Source specification says `xxx`; no destination assigned |

AIN3 is brought to one test pad per FW2, with no cross-connection. The
programmable output can reach 5.5 V while the published ADC range is 0-5 V;
rev A adds the two dividers above. Verify ADC loading, settling, and scaling
on the bench. See [the circuit design](../hardware/gpiojoiner/DESIGN.md).

## ORCA EEPROM on the shared I2C1 bus

Preserve the required 24LC02BT and the specified direct I2C1 connection.
Rev A uses **one EEPROM on the shared bus**, with EEPROM
SCL on both FW2 10-position pin-7 nets and SDA on both pin-9 nets. The
EEPROM is powered through a BAT54C common-cathode diode OR from the two
FW2 3.3 V outputs, with 100 nF decoupling and WP grounded. The diode OR
avoids directly joining host supply outputs; shared signal pins still
require both connected hosts to be powered before driving the bus.

For the SOT-23 `24LC02BT-E/OT` package: pin 1 SCL, pin 2 GND, pin 3 SDA,
pin 4 VCC, and pin 5 WP. Provide decoupling and a defined WP state.
The reference example incorrectly labels pin 5 NC. Two of these EEPROMs
cannot be assigned independent I2C addresses on the same bus because the
three low address bits are ignored. If separate per-host identification
is later required, it needs a circuit that still supports the specified
direct I2C1 test connection.

These are component requirements from
[Microchip DS20001709L, sections 2 and 5](https://ww1.microchip.com/downloads/en/DeviceDoc/24AA02-24LC02B-24FC02-Data-Sheet-20001709L.pdf).
Use verified 3.3 V pull-ups, reserve 0x50-0x57, use at most 400 kHz, and
coordinate host bus ownership. R5/R6 pull-ups are DNP pending measurement.
EEPROM identification contents and host behavior still need bench validation.

## Four-position, two-device application

The user clarified that generally two devices are connected. Rev A uses
the fixed sides defined above, supporting FW2/FW2, OG/OG, FW2 A/OG B, and
OG A/FW2 B. The alternative connectors on a side share signals. Four
simultaneously attached devices or two on the same side are unsupported;
that would require a separate switching/isolation design.
