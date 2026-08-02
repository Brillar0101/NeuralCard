# NeuralCard — Bill of Materials (JLCPCB assembly)

**Project:** NeuralCard — AI business card (air-writing digit recognition)
**Owner:** Barakaeli Lawuo
**Assembly:** JLCPCB SMT. **All parts SMD/SMT except the CR2032 coin** (the holder BT1 is SMT; only the coin itself is non-soldered).
**Upload file for JLC:** `BOM_JLCPCB.csv` (+ a place/CPL file generated after PCB layout).

> ⚠️ **Confirm every LCSC part number at the links below before ordering.** Actives/connectors
> were pulled directly from LCSC (footprints are JLC-exact, in `JLC.pretty`). Passive (R/C)
> codes are common JLC **Basic** parts — verify value/voltage/package on the linked page.

---

## 1. Active parts, connectors, electromechanical (confirmed JLC-exact footprints)

| Ref | Part | Value / role | Pkg | Qty | LCSC | Confirm link | Datasheet |
|---|---|---|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-**N8R2** | MCU (radio unused) | module SMD | 1 | **C2913204** | [LCSC](https://www.lcsc.com/product-detail/C2913204.html) · [JLC](https://jlcpcb.com/partdetail/C2913204) | [Espressif PDF](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) (local ✓) |
| U2 | LSM6DS3TR-C | 6-axis IMU (air-writing) | LGA-14 | 1 | **C967633** | [LCSC](https://www.lcsc.com/product-detail/C967633.html) · [JLC](https://jlcpcb.com/partdetail/C967633) | [ST PDF](https://www.st.com/resource/en/datasheet/lsm6ds3tr-c.pdf) (⚠ open in browser) |
| U3 | ME6211C33M5G | 3.3 V LDO (USB→3V3) | SOT-23-5 | 1 | **C82942** | [LCSC](https://www.lcsc.com/product-detail/C82942.html) · [JLC](https://jlcpcb.com/partdetail/C82942) | [LCSC](https://www.lcsc.com/product-detail/C82942.html) |
| Q1 | AO3401A | P-MOSFET (coin auto-select) | SOT-23 | 1 | **C15127** | [LCSC](https://www.lcsc.com/product-detail/C15127.html) · [JLC](https://jlcpcb.com/partdetail/C15127) | [LCSC](https://www.lcsc.com/product-detail/C15127.html) |
| J1 | TYPE-C-31-M-12 | USB-C 16P (program + power) | SMD | 1 | **C165948** | [LCSC](https://www.lcsc.com/product-detail/C165948.html) · [JLC](https://jlcpcb.com/partdetail/C165948) | [LCSC](https://www.lcsc.com/product-detail/C165948.html) |
| D0 | USBLC6-2SC6 | USB ESD protection | SOT-23-6 | 1 | **C7519** | [LCSC](https://www.lcsc.com/product-detail/C7519.html) · [JLC](https://jlcpcb.com/partdetail/C7519) | [ST PDF](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) (local ✓) |
| D1–D24 | KT-0603R (red) | Neuron LEDs (24×) | 0603 | 24 | **C2286** | [LCSC](https://www.lcsc.com/product-detail/C2286.html) · [JLC](https://jlcpcb.com/partdetail/C2286) | [LCSC](https://www.lcsc.com/product-detail/C2286.html) |
| BT1 | CR2032-BS-6-1 (Q&J) | Coin cell holder | SMD holder | 1 | **C70377** | [LCSC](https://www.lcsc.com/product-detail/C70377.html) · [JLC](https://jlcpcb.com/partdetail/C70377) | [LCSC](https://www.lcsc.com/product-detail/C70377.html) |
| SW1, SW2 | TS-1187A-B-A-B | Tact switch (BOOT, RESET) | SMD | 2 | **C318884** | [LCSC](https://www.lcsc.com/product-detail/C318884.html) · [JLC](https://jlcpcb.com/partdetail/C318884) | [LCSC](https://www.lcsc.com/product-detail/C318884.html) |
| SW3 | SHOU HAN MSK12C02 | SPDT slide switch — **power on/off**, in series with coin + terminal | SMD 8×2.8 mm, right-angle | 1 | **C431540** | [LCSC](https://www.lcsc.com/product-detail/C431540.html) · [JLC](https://jlcpcb.com/partdetail/C431540) | [LCSC PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_SHOU-HAN-MSK12C02_C431540.pdf) |

## 2. Passives — JLC **Basic** parts (verify value/voltage at link)

| Ref | Value | Pkg | Qty | LCSC (verify) | Confirm link | Role |
|---|---|---|---|---|---|---|
| R1–R6 | 220 Ω 1% | 0603 | 6 | C22962 | [LCSC](https://www.lcsc.com/product-detail/C22962.html) | LED charlieplex current limit |
| R7, R8 | 5.1 kΩ 1% | 0603 | 2 | C23186 | [LCSC](https://www.lcsc.com/product-detail/C23186.html) | USB-C CC1/CC2 sink |
| R9, R10 | 10 kΩ 1% | 0603 | 2 | C25804 | [LCSC](https://www.lcsc.com/product-detail/C25804.html) | EN + IO0 pull-ups |
| R11, R12 | 4.7 kΩ 1% | 0603 | 2 | C23162 | [LCSC](https://www.lcsc.com/product-detail/C23162.html) | I²C SDA/SCL pull-ups |
| R13 | 100 kΩ 1% | 0603 | 1 | C25803 | [LCSC](https://www.lcsc.com/product-detail/C25803.html) | P-FET gate bleeder (VBUS→GND) |
| C1–C5 | 100 nF X7R 50V | 0603 | 5 | C14663 | [LCSC](https://www.lcsc.com/product-detail/C14663.html) | Decoupling (ESP32 ×3, IMU, LDO) |
| C6, C7 | 1 µF X7R 25V | 0603 | 2 | C15849 | [LCSC](https://www.lcsc.com/product-detail/C15849.html) | LDO in/out |
| C8 | 10 µF 25V | 0805 | 1 | C5674 | [LCSC](https://www.lcsc.com/product-detail/C5674.html) | ESP32 bulk |
| C9 | 22 µF 16V | 0805 | 1 | C45783 | [LCSC](https://www.lcsc.com/product-detail/C45783.html) | Rail bulk |
| C10 | 100 µF 6.3V | 0805 | 1 | C15850 | [LCSC](https://www.lcsc.com/product-detail/C15850.html) | Ride-out cap (coin peaks) |

**Total placements: 52** per the current `fab/NeuralCard-cpl.csv` — 24 LEDs + 11 R + 10 C +
3 switches (SW1/SW2/SW3) + 3 ICs/module (U1/U2/U4) + BT1.

> ⚠️ **Sections 1–2 above are stale.** They still list the v2-removed USB-C power path
> (J1, D0, U3, Q1, R7, R8, R13, C6, C7) — those nine parts are **not** in the current CPL.
> See `DESIGN.md` §0 for the removal and [`CHANGELOG.md`](./CHANGELOG.md) "Known issues".

---

## 3. ⚠️ Important ordering notes

1. **LSM6DS3TR-C (U2) is JLC "Standard PCBA only" + needs an assembly fixture.** Because of this
   one part, the whole board must use **JLCPCB Standard Assembly** (not Economic). Budget the
   one-time fixture fee. Confirm on the [JLC part page](https://jlcpcb.com/partdetail/C967633).
2. **LEDs are red (C2286), and must stay red.** Blue LEDs need ~2.8–3.2 V forward, which a
   3.0 V coin cannot drive with any margin — this was resolved in v2 by moving to red
   `KT-0603R` (Vf ~1.8 V). Do **not** revert to the old blue `C72041`: it contradicts
   `BOM_JLCPCB.csv` and the board's red footprint, and a 2026-08-02 LCSC check found
   **only 14 units in stock**, which cannot supply 24 per board.
3. **Power source selection (Q1 P-FET):** USB→LDO powers the rail and auto-disconnects the coin
   (no back-charge of the non-rechargeable CR2032, no diode drop). 100 % SMD.
4. **CR2032 holder height** adds ~3.5 mm on one side — normal for coin-cell cards.
5. **SW3 must be ordered as C431540 specifically.** It was previously "select-at-order" against
   an improvised land, which JLCPCB rejected at DFM on order SMT026072863054. The board now
   carries the datasheet-exact MSK12C02 footprint including 4 shield tabs and 2× 0.85 mm NPTH
   locating holes — a different slide switch will not seat. See [`CHANGELOG.md`](./CHANGELOG.md).
6. Passive LCSC codes are common JLC Basic parts — **verify each value/voltage** at its link.

---

## 3b. LCSC verification (2026-08-02)

All 14 LCSC codes in `BOM_JLCPCB.csv` resolved against the LCSC/jlcsearch API. Every code
maps to a real, well-stocked part — no substitutions or discontinuations found.

| LCSC | Qty | Resolved MPN | Stock | Unit $ |
|---|---|---|---|---|
| C2286 | 24 | KT-0603R | 7,824,832 | 0.0053 |
| C22962 | 6 | 0603WAF2200T5E | 3,413,507 | 0.0010 |
| C14663 | 6 | CC0603KRX7R9BB104 | 81,299,425 | 0.0022 |
| C318884 | 2 | TS-1187A-B-A-B | 918,009 | 0.0177 |
| C25804 | 2 | 0603WAF1002T5E | 37,165,617 | 0.0008 |
| C23162 | 2 | 0603WAF4701T5E | 9,126,951 | 0.0010 |
| C45783 | 2 | CL21A226MAQNNNE | 5,389,915 | 0.0197 |
| C2913204 | 1 | ESP32-S3-WROOM-1-**N8R2** | 17,776 | 5.0143 |
| C967633 | 1 | LSM6DS3TR-C | 47,071 | 0.9286 |
| C70377 | 1 | CR2032-BS-6-1 | 32,111 | 0.1621 |
| C15850 | 1 | CL21A106KAYNNNE | 12,668,317 | 0.0091 |
| C3304276 | 1 | ST25DV04KC-IE6S3 | 18,587 | 0.5271 |
| C25803 | 1 | 0603WAF1003T5E | 14,797,688 | 0.0009 |
| **C431540** | 1 | **MSK12C02** | 98,963 | 0.0471 |

**Parts cost ≈ $6.91/board**, 73% of it the ESP32 module.

Notes:
- **SW3 confirmed.** C431540 resolves to MSK12C02 with ~99k in stock — the DFM fix is sound.
- **U1 is N8R2, not N16R8.** Confirmed by the API; harmless here (PSRAM pins NC, int8 MLP
  fits 8 MB flash). Table above corrected.
- **51 of 52 placements carry a code.** The exception is **C12**, the NFC tuning cap —
  deliberately select-at-order pending VNA trim within the 56–68 pF window.

## 4. Datasheets (local copies in `datasheets/`)

| Part | Local file | Source link |
|---|---|---|
| ESP32-S3-WROOM-1 | `datasheets/ESP32-S3-WROOM-1.pdf` ✓ | [Espressif](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) |
| LSM6DS3TR-C | ⚠ not downloaded (ST/LCSC block bots) | [ST datasheet](https://www.st.com/resource/en/datasheet/lsm6ds3tr-c.pdf) — open in browser, save to `datasheets/` |
| ME6211C33M5G | — | [LCSC C82942](https://www.lcsc.com/product-detail/C82942.html) |
| AO3401A | — | [LCSC C15127](https://www.lcsc.com/product-detail/C15127.html) |
| USBLC6-2 | (download to datasheets/) | [ST](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) |

---

## 5. NFC (v2.1 addition)

| Ref | Part | Package | LCSC | Notes |
|---|---|---|---|---|
| U4 | ST25DV04KC-IE6S3 dynamic NFC tag | SO-8 | [C3304276](https://jlcpcb.com/partdetail/STMicroelectronics-ST25DV04KCIE6S3/C3304276) | Extended, Economic PCBA OK |
| C11 | 100nF 0603 | 0603 | C14663 | VCC decoupling |
| C12 | 62pF NP0/C0G 0603 | 0603 | select at order | antenna tuning — verify with VNA; 56–68pF window |
| R14 | 100k 0603 | 0603 | C25803 | GPO open-drain pull-up |
| ANT1 | PCB coil 12x24.5mm, 9 turns 0.3/0.3 | — | (bare copper) | net-tie footprint, excluded from BOM/CPL |

Datasheet: [ST25DV04KC](https://www.st.com/resource/en/datasheet/st25dv04kc.pdf) — open in
browser, save to `datasheets/` (ST blocks scripted downloads).
