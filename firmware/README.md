# NeuralCard firmware

Bring-up scaffold for the v2.3 board. What works today:

- **Charlieplex driver** for all 24 LEDs, 8 brightness levels, mapping
  extracted from the board netlist (D1-D24 -> CP pin pairs)
- **LSM6DS3 driver** over I2C (SDA=IO8, SCL=IO17, addr 0x6B)
- **Gesture recorder** - motion-triggered capture printed as CSV over the
  USB-C serial console, for building the training dataset
- Boot self-test: LED sweep + IMU WHO_AM_I check

What is deliberately not here yet: the neural network. It gets trained from
gestures recorded with this firmware, then lands as a quantised C array in a
later step.

## Build & flash

Requires ESP-IDF v5.x (`idf.py` on PATH, target esp32s3).

    cd firmware
    idf.py set-target esp32s3
    idf.py build
    idf.py flash monitor        # plain USB-C cable, no adapter

First flash of a blank board: hold BOOT, tap RST, release BOOT (printed on
the silk), then run the flash command.

## Serial commands

| Key | Action |
|---|---|
| `t` | LED sweep test |
| `s` | stream raw IMU CSV (any key stops) |
| `0`-`9` | record one gesture labelled with that digit |

## Collecting a training set

Run `idf.py monitor`, press the digit you are about to write, write it in the
air, and the gesture prints as CSV between `GESTURE,<n>` and `END` markers.
Pipe the log to a file; ~100 gestures per digit is a solid starting dataset.

## One thing to verify on first light-up

`cp_set_outputs()` assumes D16-D24 are the output-column LEDs beside the 0-9
silk labels in order. The netlist cannot confirm visual order - check it
against the physical board and permute the mapping if needed.
