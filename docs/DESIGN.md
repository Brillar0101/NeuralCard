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
| PCB thickness | **1.6 mm** standard for prototypes; 0.8 mm is the card-like option |
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
> See [`BOM.md`](./BOM.md) (with JLC/LCSC confirm links) and [`BOM_JLCPCB.csv`](../fab/BOM_JLCPCB.csv).
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

**Full schematic complete: 54 components, ERC 0 errors** (remaining 41 warnings are benign
`pin_to_pin` "unspecified pin-type" notices inherent to easyeda2kicad-imported symbols).
Counts verified 2026-08-02 against `kicad-cli sch erc` / `sch export netlist`; SW3 is
included. Note 54 schematic components vs 52 CPL placements — ANT1 and J1 are the
difference, both bare copper and excluded from BOM/CPL.

---

## 6. Firmware sketch (out of PCB scope)
Boot → radio OFF → init IMU FIFO → idle, wake on IMU INT → on "write" gesture capture ~1 s of
6-axis motion → normalize → MLP/1D-CNN → 10-way softmax → drive output neuron LEDs by probability;
ripple input→hidden→output. Model trained off-device, int8-quantized, stored in flash.

---

## 8. NFC tap-to-share (v2.1)

**ST25DV04KC-IE6S3** (U4, SO-8, LCSC C3304276) on the shared I2C bus
(addr 0x53 user / 0x57 system — no clash with IMU 0x6A). GPO (open-drain
field-detect, R14 100k pull-up) -> **GPIO21** (module pin 23): phone tap can
wake the ESP32 for an LED ripple. C11 100nF decoupling. V_EH unused.

**Antenna:** 9-turn rectangular spiral on B.Cu, outer 12x24.5mm at
x[2.5,14.5] y[16,40.5] (left-middle, under the input-LED column area),
0.3mm track / 0.3mm gap. The net-tie footprint
`NeuralCard:NFC_Antenna_13x24` bridges
NFC_ANT_A/NFC_ANT_B legally; inner terminal escapes on F.Cu between two
0.3mm-drill TH pads. Front silk marks the tap zone ("NFC / tap phone here").

**Tuning:** coil ~1.5uH (Mohan approx) + 28.5pF chip-internal + ~3pF
parasitics -> **C12 62pF NP0** across AC0/AC1 => ~13.6 MHz pre-fab.
Verify on the fab'd board with a VNA; trim C12 within 56–68pF.

**Rule areas** (both layers) over the coil: no pour, no tracks, no vias —
pads and footprint copper exempt, so the coil itself is legal and the
autorouter/GND pour stay out of the field.

**Pour handling:** orphan GND pour
fragments are tied with vias and <3mm2 slivers purged. GND pour local
clearance raised 0.2 -> 0.3mm (>= 0.25 hole-to-copper rule).

**Layout shifts vs v2:** stitching vias at (2.6,27), (2.6,42), (5,51)
removed (coil/NFC pocket); U4/C11 top-left beside IMU; C12 at the coil
feed; NFC content plan: NDEF URI -> portfolio /card page (vCard download);
QR on front silk should encode the same URL.

**Status:** re-routed 100% (freerouting, 0 unrouted), **DRC 0 violations**;
5 cosmetic same-net GND-pour fragment notices remain (every GND pad is
track-routed; fragments are redundant copper). Fab outputs regenerated.

### BOM verification note (v2.1, JLCPCB live check)
All LCSC IDs verified against JLCPCB part pages. Three v2-era mismatches fixed:
C2913204 is the **N8R2** module (BOM said N16R8) — fine for this design (PSRAM
pins NC, int8 MLP fits 8MB flash easily); C8's old ID (C5674) was a 22uF part,
now C15850 (true 10uF); C10's old ID (C15850) was 10uF, not 100uF — no basic
100uF exists in 0805, so C10 is now 22uF (C45783), total bulk ~54uF. If more
ride-out is wanted, move C10 to a 1206 100uF in the next rev. ESP32 + IMU are
Standard-PCBA-only parts, so the board assembles as Standard regardless of the
NFC chip being Economic-capable.

### Power-button behavior (firmware spec, no hardware change)
SW1/GPIO0 doubles as the power button: **long-press = off** (deep sleep,
motion-wake disabled, only EXT0/GPIO0 button wake armed, ~7-10uA — years on
the coin, comparable to CR2032 self-discharge); **press = on** (boot, arm
IMU wake-on-motion, wake ripple). Short press while on = user button
(replay last inference / mode cycle). SW2 stays hard reset. NFC keeps
working while "off" (RF-field powered). A hard-off latch IC was considered
and rejected: saves nothing vs battery self-discharge, costs parts + reroute.

## 9. Hardware power switch — SW3 (v2.2)

**SHOU HAN MSK12C02** (SW3, LCSC C431540), an SPDT slide switch in series between the coin
cell and the `+3V3` rail. Physical on/off, independent of the SW1/GPIO0 firmware deep-sleep
behavior in §8 — that spec still stands; SW3 supplements it with a true hard cutoff.

```
 BT1 CR2032 (+) ──► VBAT ──► SW3 pad 2 (common pole)
                              ├── pad 3 ──► +3V3 rail    (slid ON)
                              └── pad 1 ──► open throw   (slid OFF)
```

| Property | Value |
|---|---|
| Footprint | `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` |
| Body | 8 × 2.8 mm, right-angle actuator |
| Pads | 3 signal + 4 `SH` shield tabs + 2× 0.85 mm NPTH locating holes |
| Placement | 81.4550, -28.0000, Bottom, rotated -90 (v2.2 re-place; was 142.1112, -64.4434) |
| Orientation | Pins inboard toward BT1; actuator faces the right card edge (thumb-reachable) |
| Edge clearance | 1.0 mm courtyard-to-edge (moved 0.546 mm inboard for assembly) |

The four `SH` tabs are **intentionally netless**. They are the retention frame, and the
datasheet does not state that the frame is isolated from the contacts — tying them to GND
risks shorting the coin cell. They still solder down for mechanical retention.

**Schematic symbol:** `Switch:SW_SPDT`, in the POWER section.
KiCad's generic SPDT numbers its common pole **pin 2**, which matches the MSK12C02 pinout
and the pad nets on the board, so the stock symbol is used unmodified.

> ⚠️ **Do not renumber SW3's pins.** Pin 2 is the common pole on `VBAT`, pin 3 the closed
> throw on `+3V3`, pin 1 the open throw (explicit no-connect). Swapping them would short the
> coin cell across the throws. Verified pad-by-pad against `NeuralCard.kicad_pcb`:
> 174 schematic pads vs 173 PCB pads, **0 net mismatches** — Update PCB from Schematic is a
> connectivity no-op. See [`CHANGELOG.md`](../CHANGELOG.md).

---

## 10. Decoupling re-place (v2.2)

The v2.1 board had its decoupling capacitors in the wrong place — not miswired, just
physically distant from the ICs they serve — dealt into two cosmetic edge rows by
list order, with no reference to which IC a cap belonged to.

Measured on the v2.1 board, centroid to centroid:

| IC | v2.1 nearest cap | v2.2 |
|---|---|---|
| U1 ESP32-S3 | **24.8 mm** | 11.4 mm (C3 sits ~2 mm off the module edge) |
| U2 IMU | 10.8 mm (its own C5 was **42 mm** away) | **4.0 mm** |
| U4 NFC | 4.9 mm | 4.9 mm (unchanged) |

At ~0.3–0.8 nH of loop inductance per mm, a 100 nF cap 25 mm from the pin it feeds does
essentially nothing at the frequencies that matter. Neither ERC nor DRC can see this — the
connectivity was always correct.

**v2.2 placement.** C1/C2 on the module's left flank, C3/C4/C8 in the corridor between the
module's pad edge (x≈41.1) and BT1's courtyard (x≈47). That corridor is only ~6 mm wide, so
those caps are rotated 90°: a 0603 on its side is 0.8 mm across instead of 1.6 mm. C5 sits
4 mm from the IMU. C9/C10 (22 µF ride-out, not HF decoupling) stay in the top edge row —
keeping them out of the corridor is what let the output-column charlieplex lines route.

**U1 still reads 11.4 mm** to its nearest cap and the detector still flags it. That is an
artefact of centroid-to-centroid measurement against an 18 × 25.5 mm module: any cap beside
the module edge is ≥9 mm from its centre. C3 is ~2 mm from the module edge and close to the
3V3 pin, which is what actually matters.

### Also in v2.2

- **SW3 entered the placement data.** It was added by hand in `b2ccb56`, so any re-place
  would have dropped it to the default centre slot.
- **Part numbers moved into the schematic** — `MPN`, `Manufacturer`, `LCSC` on every
  purchasable component (15/18 lines; ANT1, J1 and C12 are correctly part-less).

### Verification (v2.2)

| | v2.1 | v2.2 |
|---|---|---|
| Routing | 100% | **100%** (freerouting score 995.36, 0 unrouted) |
| Unconnected pads | 0 | **0** (the 7 reported are netless by design: ANT1 escape, SW3's 2 NPTH + 4 shield tabs) |
| Tracks / vias | 465 / 57 | 631 / 79 |
| ERC | 0 errors | 0 errors, 41 warnings |
| DRC clearance/crossing | 0 | 0 |
| GND pour fragments | 5 | **28** — see below |

**Known regression: isolated GND pour islands went from 5 to 28.** These are redundant copper
fragments the stitcher could not reach with a via; every GND pad is track-routed, so this is
cosmetic rather than functional. It is a side effect of the new placement changing the pour
topology; stitching converges there (a second pass adds 0 vias). Worth
revisiting before a large production run, since isolated copper is not ideal for EMC.

---

### NFC/QR destinations (final)
- QR (copper-permanent): **https://www.princetekki.com** (v3, EC-Q, regenerated
  2026-07 — old matrix encoded a stale URL and was replaced).
- NFC NDEF (rewritable): **dual-record message** — record 1 is the vCard as
  `text/vcard` (Android routes it straight to Contacts on tap: true direct save),
  record 2 is the URI **https://www.princetekki.com/card?src=nfc** (iPhone ignores
  the vCard in background reading and dispatches the URL to Safari). 255 B of the
  tag's 512 B. Flash with the ST25 App once boards arrive — no firmware needed. Verify both flows on
  real hardware before handing cards out.
- The /card landing page lives in the portfolio repo (CardPage.jsx): vCard 3.0
  download (public/card.vcf — keep in sync with src/config.js), social links,
  and it greets with the drawn digit when ?drew=N is appended by future firmware.

### Typography (v2.1)
Silkscreen uses the site's PatternFly faces (outline fonts, plotted as
polygons): Red Hat Display Bold (name), Red Hat Text SemiBold (title,
instruction), Red Hat Mono SemiBold (digits, axis labels, URL, microtext).
SemiBold keeps small strokes above JLC's 0.15mm silk minimum. Applied
after place/route, BEFORE fab export.
Fonts must be installed (RedHatOfficial/RedHatFont, already in ~/Library/Fonts).
