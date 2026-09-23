# Resume content

Wording for this project on a resume, CV or portfolio. Pick the version that
fits the space. Every number here is checked against the board, the firmware
and the fab outputs in this repo.

## Project entry

**NeuralCard, an ESP32-S3 business card that runs a neural network**
Hardware, firmware and design. KiCad, ESP-IDF, Blender.

- Designed a credit card sized PCB (85.6 by 54 mm, ISO/IEC 7810 ID-1) built
  around an ESP32-S3, a 6-axis IMU and 24 LEDs placed as the network the board
  runs: 6 input neurons, 8 hidden, 10 output.
- Wrote the firmware in C on ESP-IDF, including an int8 quantised MNIST network
  that runs inference on the microcontroller. The user draws a digit in the air,
  the IMU captures the gesture, and the LEDs show the real per-neuron
  activations while inference runs rather than a canned animation.
- Drove all 24 LEDs from 6 GPIO using charlieplexing. That removed a driver IC
  from the BOM and freed the pins the IMU and the NFC tag needed.
- Etched the 13.56 MHz NFC coil antenna into the board copper instead of fitting
  a module, and tuned it to resonance with an NP0 trim capacitor. The tag is
  passive, so tapping a phone serves a vCard even with a dead battery or no
  battery fitted.
- Designed the supply for two sources. USB-C reaches a shared VSYS node through
  a Schottky, a rechargeable LIR2450 joins it through a P-FET wired for load
  sharing, an MCP73831 charges the cell at 50 mA, and an LDO brings VSYS down to
  3.3 V.
- Routed 171 nets on two layers with 56 vias using Freerouting, with every
  segment on a 0, 45 or 90 degree grid. Closed the revision at 0 unconnected
  items and 0 ERC violations.
- Produced the fab package (Gerbers, drill, pick and place) and BOMs for two fab
  houses, with approved alternates where a swap is safe and do-not-substitute
  notes where it is not.
- Built a rendering pipeline in Blender driven by KiCad layer masks and the
  board's own 3D export, so product images come from the real layout rather than
  a mock-up.

## Short version

One line, for a skills-heavy CV or a portfolio caption:

> Credit card sized ESP32-S3 PCB that runs int8 MNIST inference on-device from
> IMU air-gestures, with 24 charlieplexed LEDs showing live neuron activations
> and an etched 13.56 MHz NFC coil for passive vCard sharing.

Two lines, if you have the room:

> A business card that runs a neural network. Draw a digit in the air and the
> 24 LEDs, laid out as the network itself, light with the real activations as
> inference runs on an ESP32-S3. An NFC coil etched into the copper shares a
> vCard with no battery at all.

## Skills this evidences

Hardware: schematic capture and PCB layout in KiCad, DRC and ERC closure,
antenna design and resonance tuning, battery charging and power-path design,
design for manufacture, BOM sourcing and second-sourcing.

Firmware: embedded C, ESP-IDF, sensor drivers over I2C, quantised neural network
inference on a microcontroller, charlieplex LED driving.

Other: Blender, Python for design automation, technical writing.

## What is built and what is designed

Worth keeping straight in an interview, because the distinction will come up.

The CR2032 revision was fabricated and assembled. The current revision, which
replaces that cell with a rechargeable LIR2450 and adds USB-C charging, is
designed and verified but has not been through a fab run yet. Describe the
latest work as designed rather than built until boards are in hand, and anchor
any claim about shipped hardware to the earlier revision.
