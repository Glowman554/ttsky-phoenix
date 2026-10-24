<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

[Phoenix v2](https://git.toxicfox.de/toxicfox/phoenix-v2) is an 8-bit CPU with 16 registers, GPIO, interrupts, a timer, and UART.
At startup, it copies a 64 KiB program image from external flash into PSRAM,
then executes from address zero. The memories use single-bit SPI. The original design can be found [here](https://git.toxicfox.de/toxicfox/phoenix-v2-rtl). The core has been tested using a [Tang Primer 20k fpga](https://git.toxicfox.de/toxicfox/phoenix-v2-rtl-tt)

## How to test

1. Connect the QSPI Pmod to the demo board's **BIDIR** connector.
2. Program a 64 KiB Phoenix image at flash offset zero, for example using the
   [Tiny Tapeout Flasher](https://github.com/TinyTapeout/tinytapeout-flasher).
3. Select the project, supply a 27 MHz clock, and pulse `rst_n` low.
4. After boot, check the program's GPIO output on `uo_out[1]`–`uo_out[7]` or
   UART TX on `uo_out[0]` at 115,200 baud, 8N1. UART RX is `ui_in[1]`.

GPIO inputs are `ui_in[0]`, then `ui_in[2]`–`ui_in[7]`. They are synchronized.
Jumping to `0xffff` halts the CPU; reset restarts the boot sequence.

## External hardware

The [Tiny Tapeout QSPI Pmod](https://store.tinytapeout.com/products/QSPI-Pmod-p716541602)
contains 16 MB of flash and two 8 MB PSRAM chips. Phoenix uses the flash and
RAM A; RAM B remains inactive. Connections follow the
[QSPI Pmod pinout](https://github.com/mole99/qspi-pmod):

| Pins | Function |
| --- | --- |
| `uio[0]` | Flash chip select |
| `uio[1]` | MOSI / SD0 |
| `uio[2]` | MISO / SD1 |
| `uio[3]` | Clock |
| `uio[4]`, `uio[5]` | SD2 / SD3, held high |
| `uio[6]` | RAM A chip select |
| `uio[7]` | RAM B chip select, held high |
