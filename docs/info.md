<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

[Phoenix v2](https://git.toxicfox.de/toxicfox/phoenix-v2) is an 8-bit CPU with 16 registers, GPIO, interrupts, a timer, and UART.
At startup, it copies a 64 KiB program image from external flash into PSRAM,
then executes from address zero. The memories use single-bit SPI. The original design can be found [here](https://git.toxicfox.de/toxicfox/phoenix-v2-rtl). 
<!--- The core has been tested using a [Tang Primer 20k fpga](https://git.toxicfox.de/toxicfox/phoenix-v2-rtl-tt) --->

## How to test

1. Connect the QSPI Pmod to the demo board's **BIDIR** connector.
2. Program a 64 KiB image at flash offset zero, for example using the
   [Tiny Tapeout Flasher](https://github.com/TinyTapeout/tinytapeout-flasher).
3. Select the project, supply a 27 MHz clock, and pulse `rst_n` low.
4. Check the GPIO / UART output

GPIO inputs are `ui_in[0]`, then `ui_in[2]`–`ui_in[7]`. They are synchronized. The GPIO inputs `ui_in[0]` - `ui_in[4]` can be used for interrupts.

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

## Available development tools

- [Assembler, disassembler & emulator](https://git.toxicfox.de/toxicfox/phoenix-v2/src/branch/main/tools)
- [B compiler (predecessor to c)](https://git.toxicfox.de/toxicfox/b-compiler)
- [Brainfuck compiler](https://git.toxicfox.de/toxicfox/BrainASM)

## Architecture

### Overview

Phoenix is an 8-bit architecture with 16-bit memory and io addressing. The architecture has dedicated memory and io address spaces. Instructions and data are mixed.

### Instruction encoding

An instruction has a fixed size of 24-bit. An instruction can contain 2 registers and an 8-bit intermediate value or a 16-bit intermediate value.

```text
00000000 0000 0000 00000000
└ opcode ┘ │    │  └ 8-bit intermediate
           │    └ first register
           └ second register
```

| Field | Width | Encoding |
| --- | ---: | --- |
| Instuction opcode | 8 bits | `00000000` |
| Second register | 4 bits | `0000` |
| First register | 4 bits | `0000` |
| 8-bit Intermediate | 8 bits | `00000000` |

To store a 16-bit intermediate value you need to combine the register section and the 8-bit intermediate section.

### Halting execution

To halt execution, you must either jump to `0xffff` (the end of the memory space) or set the HALT flag.

### Registers

#### General purpose registers

There are 16 general purpose registers with a size of 8-bit. Those are named R0 – R15. Those registers can be used with all instructions accepting a register.

#### Index registers

There are 2 index registers with a size of 16 bits. These are called A and B. An index register consists of 2 general purpose registers. These registers are encoded in the instruction opcode instead of the register part.

- Index register A consists of r0 (low byte) and r1 (high byte).
- Index register B consists of r2 (low byte) and r3 (high byte).

The index registers are used to store indexes either in memory or in IO space.

#### Special purpose registers

##### Flags

The flags register stores state the architecture uses to make decisions. The flags register is 4-bits big.

- Bit 0: ZERO
- Bit 1: EQ (Equals)
- Bit 2: OV (Overflow)
- Bit 3: HALT

##### Interrupt handler

16-bit register used to store the interrupt handler address.

##### Stack pointer

16-bit register used to store the stack pointer. The recommended location is at `0xffff`.

### I/O space mapping

| Address | Name |
| --- | --- |
| `0x0000` | GPIO 0 port |
| `0xf000` | UART transmit data / transmit status |
| `0xf001` | UART received data |
| `0xf002` | UART status |
| `0xf003` | UART baud-rate scaler (low byte) |
| `0xf004` | UART baud-rate scaler (high byte) |
| `0xff00` | Interrupt controller |
| `0xff01` | Timer 0 prescaler |
| `0xff02` | Timer 0 compare |
| `0xff03` | Timer 0 control |

### GPIO

A GPIO port has 8 inputs and 8 outputs. Simply writing to the io address will output the value written to the GPIO port. Reading the io address returns the state of the input pins.

### Interrupts

When an interrupt is triggered, the core jumps to the address stored in the interrupt handler register. After the handler has finished executing the routine, the `ire` instruction is used to return to the previous program code. While an interrupt is being executed, an interrupt lock is set and no other interrupt can occur. The lock is released when the interrupt is finished.

**IMPORTANT:** The interrupt handler must maintain the state of all registers (general, index and special registers).

#### Interrupt controller

The interrupt controller contains an interrupt mask that can be set by writing to the IO device. The number of the bit in the interrupt mask corresponds to the interrupt ID you want to mask / unmask. Setting a bit to 1 unmasks the interrupt.

During the execution of the interrupt handler, the handler can read the io device to get a mask of the interrupts triggering the interrupt.

#### Interrupt map

| Interrupt number | Function |
| --- | --- |
| 0 | User defined |
| 1 | User defined |
| 2 | User defined |
| 3 | User defined |
| 4 | User defined |
| 5 | UART receive interrupt |
| 6 | Timer 0 interrupt |
| 7 | Software interrupt |

### Timer

The timer consists of 3 io devices. The prescaler io device is used to set the prescaler, which can change the rate at which the timer counts. The timer will count when `prescaler == prescaler_count`. The compare io device is used to set the value to which the timer will compare. The timer will trigger the desired action if `compare == timer_count`. If the prescaler is disabled, the timer will count with the unmodified core clock.

The control io device is used to control the functions of the timer. The following bits can be used:

- Bit 0: if set, timer is enabled.
- Bit 1: if set, prescaler is enabled.
- Bit 2: if set, the timer triggers interrupts.
- Bit 3: if set, the timer pulses the timer output pin.
- Bit 4: when set, the timer toggles the timer output pin.


### UART interface

The UART interface is used for serial communication. It uses 8N1 framing (8 data bits, no parity, 1 stop bit). The default baud rate is 115200.

The UART interface has 5 io devices:

| Address | Name | Description |
| --- | --- | --- |
| `0xf000` | Transmit | Write data to transmit. Reading returns 0 when idle or non zero when busy. |
| `0xf001` | Receive | Read the last received byte. Reading clears the receive valid flag. |
| `0xf002` | Status | Contains the UART status flags. |
| `0xf003` | Scaler low | Lower 8 bits of the baud rate scaler. |
| `0xf004` | Scaler high | Upper 8 bits of the baud rate scaler. |

#### Transmitting

To transmit a byte, write it to `0xf000`. Data can only be transmitted when the UART interface is not busy. Writes while busy are ignored.

The status register at `0xf002` can be used to check if the UART interface is ready.

#### Receiving

When a byte is received, it is stored at `0xf001` and the receive valid flag is set. Reading this register clears the flag.

The UART triggers interrupt ID 5 when a byte is received.

Only the last received byte is stored. New data overwrites the previous byte.

#### Status

The status register at `0xf002` contains the following bits:

- Bit 0: If set, the transmitter is busy.
- Bit 1: If set, a received byte is available.

#### Baud rate

The baud rate can be set by writing the 16-bit scaler to `0xf003` and `0xf004`.

The scaler is calculated as follows:

`scaler = CLK_FREQ / UART_FREQ - 1`


### Instruction set

#### Arithmetic Operations

- **`add <register>, <register | intermediate>`**

  Add the left and the right and store in the left register.

  If the addition overflows set the OV flag

- **`sub <register>, <register | intermediate>`**

  Subtract the right from the left and store in the left register.

  If the subtraction overflows set the OV flag.

- **`ado <register>, <register | intermediate>`**

  If OV is set add the left and the right and store in the left register.

- **`sbo <register>, <register | intermediate>`**

  If OV is set Subtract the right from the left and store in the left register.

- **`nad <register>, <register | intermediate>`**

  Performs logic NAND with the left and the right and stores in left register.

- **`nor <register>, <register | intermediate>`**

  Performs logic NOR with the left and the right and stores in left register.

- **`cmp <register>, <register | intermediate>`**

  Compares left and right, resets flags.

  Sets EQ if left and right are equal.

  Sets ZERO if left is equal to zero.

#### Control flow

- **`jeq <index | intermediate>`**

  Jump to address if EQ flag is set.

- **`jnq <index | intermediate>`**

  Jump to address if EQ flag is not set.

- **`jzr <index | intermediate>`**

  Jump to address if ZERO flag is set.

- **`jnz <index | intermediate>`**

  Jump to address if ZERO flag is not set.

- **`jof <index | intermediate>`**

  Jump to address if OV flag is set.

- **`jno <index | intermediate>`**

  Jump to address if OV flag is not set.

- **`jmp <index | intermediate>`**

  Jump to address.

#### Stack operations

- **`lsp <index | intermediate>`**

  Load stack pointer into stack register.

- **`rsp <index>`**

  Save stack pointer into index register.

- **`put <register | intermediate>`**

  Push the value onto the stack.

- **`pop <register>`**

  Pop from the stack into the register.

#### Data operations

- **`mov <register>, <register>`**

  Mov the right register into the left register.

- **`lod <register>, <intermediate>`**

  Load the intermediate value into the register.

- **`out <index>, <register>`**

  Save register into io space at index.

- **`inp <register>, <index>`**

  Load value stored at index in io space into register.

- **`wtr <index>, <register>`**

  Save register into ram at index.

- **`ldr <register>, <index>`**

  Load value stored at index in ram into register.

- **`lad <index>, <intermediate>`**

  Save intermediate into index.

#### Interrupts

- **`ire`**

  Return from interrupt.

- **`int`**

  Trigger software interrupt.

- **`lih`**

  Load interrupt handler address into interrupt handler register.

#### Flags

- **`cfg`**

  Clear all flags.

- **`wfg <register>`**

  Store register into flags.

- **`rfg <register>`**

  Load flags into register.

#### Other

- **`nop`**

  Do nothing
