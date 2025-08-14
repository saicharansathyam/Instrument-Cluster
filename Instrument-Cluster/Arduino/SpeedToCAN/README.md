# SpeedToCAN (Arduino)

## Purpose
Reads a wheel encoder, calculates speed in cm/s, and sends it over CAN bus (MCP2515).

## Hardware
- Arduino Nano / Uno (or any ATmega328p board)
- MCP2515 CAN module (16 MHz crystal)
- Wheel encoder (20-slot, optical or magnetic)
- Pull-up on encoder line (10k) or use INPUT_PULLUP

## Wiring
- **MCP2515 → Arduino**
  - VCC → 5V
  - GND → GND
  - CS → D10
  - SCK → D13
  - SI  → D11
  - SO  → D12
  - INT → not used here

- **Encoder → Arduino**
  - Signal → D3 (interrupt)
  - VCC → 5V
  - GND → GND

## CAN Frame Format
- **Speed (cm/s × 10)**
  - CAN ID: `0x100`
  - DLC: 2 bytes
  - Unsigned 16-bit big-endian

Example: `50.3 cm/s` → raw = 503 → bytes: `0x01 0xF7`
