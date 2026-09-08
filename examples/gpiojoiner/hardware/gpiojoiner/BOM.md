# GPIO Joiner rev A - prototype assembly BOM

| References | Qty | Part / specification | Package | Assembly |
| --- | ---: | --- | --- | --- |
| J1, J3, J5, J6 | 4 | SFH11-PBPC-D10-RA-BK, 20-position right-angle connector from ORCA starter | Project-local ORCA_20_RA | Fit; verify mating before ordering |
| J2, J4 | 2 | SFH11-PBPC-D05-RA-BK, 10-position right-angle connector from ORCA starter | Project-local ORCA_10_RA | Fit; verify mating before ordering |
| SW1 | 1 | C&K JS202011CQN, DPDT slide switch | Project-local corrected SW_JS202011CQN | Fit; verify both contact states |
| U1 | 1 | Microchip 24LC02BT-E/OT, 2-kbit serial EEPROM | SOT-23-5 | Fit blank; ORCA image/programming remains to be validated |
| D1 | 1 | Nexperia BAT54C,215, dual Schottky diode, common cathode | SOT-23 | Fit |
| C1 | 1 | YAGEO CC0603KRX7R9BB104, 100 nF, X7R, 50 V, 10% | 0603 / 1608 metric | Fit |
| R1-R4 | 4 | YAGEO RT0603BRD0710KL, 10 kohm, 0.1%, 0.1 W | 0603 / 1608 metric | Fit; 2:1 analog dividers |
| R5, R6 | 2 | 4.7 kohm, 1%, at least 0.1 W | 0603 / 1608 metric | DNP; optional I2C1 pull-ups |
| R7, R8 | 2 | 120 ohm, 1%, at least 0.1 W | 0603 / 1608 metric | DNP; optional CAN termination |

TP1-TP6 are etched copper test pads, not purchased components. H1-H4 are
3.2 mm non-plated mounting holes; support hardware depends on the final
mechanical installation. There are 14 normally populated components and
four optional resistor positions, excluding copper pads and mounting holes.

Connector part numbers are those named in the upstream starter, not a
verified procurement substitution. Local footprints preserve its pad
coordinates, dimensions, and drill sizes. Confirm parts against actual
devices before ordering the prototype assembly.

Supplier-ready [PCBWay BOM](manufacturing/revA/assembly/pcbway-bom.csv) and
[JLCPCB BOM](manufacturing/revA/assembly/jlcpcb-bom.csv) contain exact orderable
MPNs and catalog identifiers, with source links in the PCBWay file. Catalog
stock, substitutions and assembly charges require confirmation in a live quote.
Use the [manufacturing instructions](manufacturing/revA/README.md).
