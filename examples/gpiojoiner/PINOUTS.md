# Free Wili Connector Pinouts

This document lists the physical connector pin assignments for Free Wili OG and Free Wili 2. Directions are stated from the Free Wili device's perspective. GPIO pins are technically bidirectional; the direction shown is their default use.

In the source diagrams, even-numbered pins are on the upper row and odd-numbered pins are on the lower row. The 20-position connector notch is between positions 10 and 12 when viewed in the depicted orientation.

## Free Wili OG - 20-position connector

[Source connector image](assets/freewiliOGconnector.jpg)

| Pin | Signal        | GPIO / Notes | Default direction |
| ---:| ------------- | ------------ | ----------------- |
| 1   | SPI1_CS_OUT   | GPIO13       | Output            |
| 2   | 5V OUT        | -            | Power output      |
| 3   | GPIO_27_OUT   | GPIO27       | Output            |
| 4   | V PINS IN     | -            | Power input       |
| 5   | UART1_Rx_IN   | GPIO9        | Input             |
| 6   | 3.3V OUT      | -            | Power output      |
| 7   | UART1_CTS_IN  | GPIO10       | Input             |
| 8   | I2C 0 SCL     | GPIO17       | Bidirectional     |
| 9   | UART1_Tx_OUT  | GPIO8        | Output            |
| 10  | I2C 0 SDA     | GPIO16       | Bidirectional     |
| 11  | UART1_RTS_OUT | GPIO11       | Output            |
| 12  | SPI1_Rx_IN    | GPIO12       | Input             |
| 13  | SPI1_Tx_OUT   | GPIO15       | Output            |
| 14  | GPIO26_IN     | GPIO26       | Input             |
| 15  | SPI1_SCLK_OUT | GPIO14       | Output            |
| 16  | SWCLK IN      | SWCLK        | Input             |
| 17  | GPIO25_OUT    | GPIO25       | Output            |
| 18  | SWDIO         | SWDIO        | Bidirectional     |
| 19  | GND           | -            | Ground            |
| 20  | GND           | -            | Ground            |

## Free Wili 2 - 20-position connector

[Source connector image](assets/freewili2connector.png)

| Pin | Signal        | GPIO / Notes | Default direction | Breakout color |
| ---:| ------------- | ------------ | ----------------- | -------------- |
| 1   | SPI1_CS_OUT   | GPIO13       | Output            | Green          |
| 2   | 5V OUT        | -            | Power output      | Red            |
| 3   | GPIO_27_OUT   | GPIO27       | Output            | Yellow         |
| 4   | TRIG IN/VREF  | -            | Input             | Gray           |
| 5   | UART1_Rx_IN   | GPIO9        | Input             | Purple         |
| 6   | 3.3V OUT      | -            | Power output      | Red            |
| 7   | UART1_CTS_IN  | GPIO10       | Input             | Purple         |
| 8   | I2C 0 SCL     | GPIO17       | Bidirectional     | Blue           |
| 9   | UART1_Tx_OUT  | GPIO8        | Output            | Purple         |
| 10  | I2C 0 SDA     | GPIO16       | Bidirectional     | Blue           |
| 11  | UART1_RTS_OUT | GPIO11       | Output            | Purple         |
| 12  | SPI1_Rx_IN    | GPIO12       | Input             | Green          |
| 13  | SPI1_Tx_OUT   | GPIO15       | Output            | Green          |
| 14  | GPIO26_IN_BI  | GPIO26       | Input             | Yellow         |
| 15  | SPI1_SCLK_OUT | GPIO14       | Output            | Green          |
| 16  | CANFD L       | -            | Bidirectional     | Orange         |
| 17  | GPIO25_OUT    | GPIO25       | Output            | Yellow         |
| 18  | CANFD H       | -            | Bidirectional     | Orange         |
| 19  | GND           | -            | Ground            | Black          |
| 20  | GND           | -            | Ground            | Black          |

## Free Wili 2 - 10-position connector

[Source connector image](assets/freewili2connector.png)

| Pin | Signal    | GPIO / Notes | Default direction | Breakout color |
| ---:| --------- | ------------ | ----------------- | -------------- |
| 1   | GND       | -            | Ground            | Black          |
| 2   | AIN3      | -            | Input             | White          |
| 3   | AOUT1     | -            | Output            | Orange         |
| 4   | AIN2      | -            | Input             | White          |
| 5   | AOUT0     | -            | Output            | Orange         |
| 6   | AIN1      | -            | Input             | White          |
| 7   | I2C 1 SCL | -            | Bidirectional     | Blue           |
| 8   | AIN0      | -            | Input             | White          |
| 9   | I2C 1 SDA | -            | Bidirectional     | Blue           |
| 10  | PROG VOUT | -            | Output            | Red            |

## 20-position connector comparison

| Pin | Free Wili OG  | OG default direction | Free Wili 2   | Free Wili 2 default direction | Difference                                            |
| ---:| ------------- | -------------------- | ------------- | ----------------------------- | ----------------------------------------------------- |
| 1   | SPI1_CS_OUT   | Output               | SPI1_CS_OUT   | Output                        | Same                                                  |
| 2   | 5V OUT        | Power output         | 5V OUT        | Power output                  | Same                                                  |
| 3   | GPIO_27_OUT   | Output               | GPIO_27_OUT   | Output                        | Same                                                  |
| 4   | VREF          | Power input          | TRIG IN/VREF  | Input                         | VREF -> TRIG IN/VREF (freewili 2 support VREF Output) |
| 5   | UART1_Rx_IN   | Input                | UART1_Rx_IN   | Input                         | Same                                                  |
| 6   | 3.3V OUT      | Power output         | 3.3V OUT      | Power output                  | Same                                                  |
| 7   | UART1_CTS_IN  | Input                | UART1_CTS_IN  | Input                         | Same                                                  |
| 8   | I2C 0 SCL     | Bidirectional        | I2C 0 SCL     | Bidirectional                 | Same                                                  |
| 9   | UART1_Tx_OUT  | Output               | UART1_Tx_OUT  | Output                        | Same                                                  |
| 10  | I2C 0 SDA     | Bidirectional        | I2C 0 SDA     | Bidirectional                 | Same                                                  |
| 11  | UART1_RTS_OUT | Output               | UART1_RTS_OUT | Output                        | Same                                                  |
| 12  | SPI1_Rx_IN    | Input                | SPI1_Rx_IN    | Input                         | Same                                                  |
| 13  | SPI1_Tx_OUT   | Output               | SPI1_Tx_OUT   | Output                        | Same                                                  |
| 14  | GPIO26_IN_BI  | Input                | GPIO26_IN_BI  | Input                         | Same                                                  |
| 15  | SPI1_SCLK_OUT | Output               | SPI1_SCLK_OUT | Output                        | Same                                                  |
| 16  | SWCLK IN      | Input                | CANFD L       | Bidirectional                 | SWCLK IN -> CANFD L                                   |
| 17  | GPIO25_OUT    | Output               | GPIO25_OUT    | Output                        | Same                                                  |
| 18  | SWDIO         | Bidirectional        | CANFD H       | Bidirectional                 | SWDIO -> CANFD H                                      |
| 19  | GND           | Ground               | GND           | Ground                        | Same                                                  |
| 20  | GND           | Ground               | GND           | Ground                        | Same                                                  |
