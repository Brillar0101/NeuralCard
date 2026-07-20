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
| U1 | ESP32-S3-WROOM-1-N16R8 | MCU (radio unused) | module SMD | 1 | **C2913204** | [LCSC](https://www.lcsc.com/product-detail/C2913204.html) · [JLC](https://jlcpcb.com/partdetail/C2913204) | [Espressif PDF](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) (local ✓) |
| U2 | LSM6DS3TR-C | 6-axis IMU (air-writing) | LGA-14 | 1 | **C967633** | [LCSC](https://www.lcsc.com/product-detail/C967633.html) · [JLC](https://jlcpcb.com/partdetail/C967633) | [ST PDF](https://www.st.com/resource/en/datasheet/lsm6ds3tr-c.pdf) (⚠ open in browser) |
| U3 | ME6211C33M5G | 3.3 V LDO (USB→3V3) | SOT-23-5 | 1 | **C82942** | [LCSC](https://www.lcsc.com/product-detail/C82942.html) · [JLC](https://jlcpcb.com/partdetail/C82942) | [LCSC](https://www.lcsc.com/product-detail/C82942.html) |
| Q1 | AO3401A | P-MOSFET (coin auto-select) | SOT-23 | 1 | **C15127** | [LCSC](https://www.lcsc.com/product-detail/C15127.html) · [JLC](https://jlcpcb.com/partdetail/C15127) | [LCSC](https://www.lcsc.com/product-detail/C15127.html) |
| J1 | TYPE-C-31-M-12 | USB-C 16P (program + power) | SMD | 1 | **C165948** | [LCSC](https://www.lcsc.com/product-detail/C165948.html) · [JLC](https://jlcpcb.com/partdetail/C165948) | [LCSC](https://www.lcsc.com/product-detail/C165948.html) |
| D0 | USBLC6-2SC6 | USB ESD protection | SOT-23-6 | 1 | **C7519** | [LCSC](https://www.lcsc.com/product-detail/C7519.html) · [JLC](https://jlcpcb.com/partdetail/C7519) | [ST PDF](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) (local ✓) |
| D1–D24 | Blue LED 0603 | Neuron LEDs (24×) | 0603 | 24 | **C72041** | [LCSC](https://www.lcsc.com/product-detail/C72041.html) · [JLC](https://jlcpcb.com/partdetail/C72041) | [LCSC](https://www.lcsc.com/product-detail/C72041.html) |
| BT1 | CR2032-BS-6-1 (Q&J) | Coin cell holder | SMD holder | 1 | **C70377** | [LCSC](https://www.lcsc.com/product-detail/C70377.html) · [JLC](https://jlcpcb.com/partdetail/C70377) | [LCSC](https://www.lcsc.com/product-detail/C70377.html) |
| SW1, SW2 | TS-1187A-B-A-B | Tact switch (BOOT, RESET) | SMD | 2 | **C318884** | [LCSC](https://www.lcsc.com/product-detail/C318884.html) · [JLC](https://jlcpcb.com/partdetail/C318884) | [LCSC](https://www.lcsc.com/product-detail/C318884.html) |

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

**Total placements: 56** (10 active/EM lines + 13 R + 10 C + 24 LEDs).

---
