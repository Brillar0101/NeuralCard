# NeuralCard — AI Business Card (Design Spec)

> An ESP32-S3 PCB business card shaped like a neural network. You **air-write a digit (0–9)
> holding the card**; an on-device neural net classifies the motion, and the **LEDs at each
> neuron node ripple the real inference** — the brightest output neuron is the recognized digit.

**Owner:** Barakaeli Lawuo — AI & Computer Engineer
**Location:** `~/kicad-projects/NeuralCard/` (moved off the TCC-protected Desktop so tooling
like `easyeda2kicad` doesn't trip macOS file-access protection).
**KiCad:** v9 file format, `kicad-cli 10.0.3`.

---

## 1. Form factor (ISO/IEC 7810 ID-1 — real credit card)

| Spec | Value |
|---|---|
| Outline | **85.60 mm × 53.98 mm** rounded rectangle |
| Corner radius | **3.18 mm** |
| PCB thickness | **0.8 mm** (card-like) |
| Layers | 2-layer |
| Assembly | **100% SMD/SMT. Only non-soldered item = the CR2032 coin.** Fab: **JLCPCB**. |

Board outline is on `Edge.Cuts` in `NeuralCard.kicad_pcb` (render-verified).

---

## 0. DESIGN REVISION (v2 — USB-C removed)
USB-C was dropped in favor of **6 UART programming pads** (3V3, GND, TX, RX, EN, IO0). This
removed 9 parts (USB-C, USBLC6 ESD, ME6211 LDO, AO3401A P-FET, 2× CC res, gate bleeder, 2× LDO
caps), made the card flatter/cheaper, and **eliminated the routing congestion → 100% auto-routed,
0 DRC violations.** Power is now **coin → +3V3 directly** (also feedable from the prog-pad 3V3
during flashing). LEDs are **red** (bright on a 3 V coin). **47 assembled SMD parts** + the prog
pads (bare copper). Flash once with a USB-serial adapter, then it runs on the coin cell.

## 2. Architecture

- **Compute:** ESP32-S3-WROOM-1-N16R8 (vector/DSP for TinyML; native USB; radio OFF for coin life).
- **Input:** LSM6DS3TR-C 6-axis IMU (air-writing). 6 axes map 1:1 to the 6 input neurons.
- **Display:** 24 LEDs at neuron nodes, charlieplexed from 6 GPIO (software PWM = activation glow).
- **Power:** CR2032 coin + USB-C/LDO with **P-FET automatic source selection** (see §3).
- **Program:** USB-C native (ESP32-S3 built-in USB) + BOOT/RESET tact buttons + USBLC6 ESD.
