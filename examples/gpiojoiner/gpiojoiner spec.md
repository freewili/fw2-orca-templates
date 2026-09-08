i have a cable that connects two freewili devices. Its for automated testing of the FreeWili GPIO. Two FreeWili OG or Two FreeWili 2 or One OG connected to a FreeWili 2.

There is a 20 position connector and a 10 position connector. The twenty position is the same for Free Wili except the CANFD signals which are not present on FreeWili one.

To power the GPIO. the VREF is connected together. in this mode  one free wili2 would power both FreeWili devices. When two free wili ogs are connected VREF comes from 3.3V of each devices.

**20 Position Connector Info between two Wilis**

SPI is connected between the two with a rx and tx swap.

I2C is directly connected

UART is connects with rx/tx and cts/rts swap

CANFD is directly connected. (should be disconnected if either are OG)

GPIO26 is connected to GPIO 27

VREF is connected together OR if its two WILI OG it uses 3.3. The agent should make sure the user does this swap on the cable.

**10 Position Connector Info**

i2c is directly connected

analog output 0 is connected to analog input 0

analog output 1 is connected to analog input 1

prog vout is connected to analog input 2

analog input 3 is connected to xxx
