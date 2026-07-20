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
