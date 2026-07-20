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

### Neural-net art topology (the visible layout)
```
 INPUT (6) = IMU axes      HIDDEN (8)        OUTPUT (10) = digits 0-9
  ax ay az gx gy gz   ->   o o o o o o o o  ->  0 1 2 3 4 5 6 7 8 9
```
24 neuron LEDs (D1–D24). Brightest output = the guess. Labeled on silk.

---

## 3. Power architecture (resolved)

```
 USB-C VBUS(5V) ──► ME6211 LDO ──► +3V3 rail ──► ESP32-S3 / IMU / LEDs
                                      ▲
 CR2032 (VCOIN) ──► Q1 AO3401A P-FET ─┘   (S=+3V3, D=VCOIN, G=VBUS, R13 100k bleeder)
```
- USB plugged → VBUS=5 V → gate high → **P-FET OFF**, coin disconnected (no back-charge); LDO powers rail.
- USB absent → R13 pulls VBUS(gate)=0 → **P-FET ON**, coin powers rail at **full 3.0 V (no diode drop)**.
- Radio OFF + bulk/ride-out caps (C8 10µF, C9 22µF, C10 100µF) absorb inference/LED peaks.

### Pin map (as built in schematic — Power + MCU sections)
| Function | Net | GPIO (module pin) |
|---|---|---|
| IMU I²C SDA | SDA | GPIO8 (p12) |
| IMU I²C SCL | SCL | GPIO17 (p10) |
| IMU INT1 | IMU_INT | GPIO18 (p11) |
| Charlieplex lines 1–6 | CHX1..6 | GPIO4/5/6/7 (p4–7), GPIO15 (p8), GPIO16 (p9) |
| USB D− / D+ | USB_DM / USB_DP | GPIO19 (p13) / GPIO20 (p14) |
| BOOT / RESET | IO0 / EN | GPIO0 (p27)+SW1 / EN (p3)+SW2 |

> GPIO35/36/37 (p28–30) reserved for octal PSRAM (N16R8) — left unconnected.

---

## 4. BOM
> See [`BOM.md`](./BOM.md) (with JLC/LCSC confirm links) and [`BOM_JLCPCB.csv`](./BOM_JLCPCB.csv).
> JLC-exact footprints in `JLC.pretty`; symbols in `JLC.kicad_sym` (via `easyeda2kicad`).
> 56 placements. ⚠ LSM6DS3TR-C = JLC Standard-PCBA-only + fixture; blue LEDs are dim on coin
> (swap to red for brightness — same footprint).

---

## 5. Build status (section-by-section, ERC-gated)
1. ✅ **Scaffold** — project, board outline, lib tables, datasheets, BOM.
2. ✅ **Power** — coin + USB-C/LDO + P-FET auto-select + caps. **ERC: 0 errors.**
3. ✅ **MCU core** — ESP32-S3 module, decoupling, EN/BOOT buttons, native USB + USBLC6 ESD, USB-C. **ERC: 0 errors.**
4. ✅ **IMU** — LSM6DS3TR-C on I²C (addr 0x6A), 4.7k pull-ups, INT1→GPIO18. **ERC: 0 errors.**
5. ✅ **Neuron LEDs** — 24 LEDs charlieplexed on 6 GPIO (CHX1-6→R1-6→CP1-6 nodes). **ERC: 0 errors.**
6. ✅ **PCB layout** — front = neural-net art (LED neurons + silk synapses + ax/ay/az/gx/gy/gz +
   digits 0-9 + name + QR), back = all parts. GND pour both layers + stitching vias.
   **Routed via Freerouting (headless): 465 tracks, 57 vias, 99% complete, 0 shorts/crossings.**
   - ⬜ Remaining manual finish (~5 min in GUI): USB-C connector fan-out (~2-3 jumpers:
     CC2, USBC_DP pad-pair) + a few GND pour islands. Autorouters + humans both fight USB-C fan-out.
7. ✅ **Fab outputs** — `fab/NeuralCard_JLCPCB.zip` (Gerbers + drill), `fab/NeuralCard-cpl.csv`
   (pick & place), `BOM_JLCPCB.csv`. The 9 DRC items are internal to the USB-C footprint
   (0.5 mm pitch) — standard and JLC-manufacturable.

### PCB pipeline (fully reproducible, headless)
```
python3 place_pcb.py                       # place + silk art + GND pour + stitching  (KiCad python)
ExportSpecctraDSN -> NeuralCard.dsn
java -jar tools/freerouting.jar -de NeuralCard.dsn -do NeuralCard.ses -mp 30
ImportSpecctraSES + ZONE_FILLER.Fill       # routes back into the board
kicad-cli pcb export gerbers/drill/pos     # fab outputs
```

**Full schematic complete: 56 components, ERC 0 errors** (remaining 56 warnings are benign
"unspecified pin-type" notices inherent to easyeda2kicad-imported symbols).

Schematic is generated by `gen_schematic.py` (re-run to rebuild `NeuralCard.kicad_sch`).

---

## 6. Firmware sketch (out of PCB scope)
Boot → radio OFF → init IMU FIFO → idle, wake on IMU INT → on "write" gesture capture ~1 s of
6-axis motion → normalize → MLP/1D-CNN → 10-way softmax → drive output neuron LEDs by probability;
ripple input→hidden→output. Model trained off-device, int8-quantized, stored in flash.

---
