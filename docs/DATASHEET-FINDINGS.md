# Datasheet findings — what changes, and the page that says so

Every row is a change to the board or libraries, traced to the page, table or figure of the
manufacturer datasheet that mandates it. Page numbers are **PDF page numbers** in the file
held in `hardware/datasheets/`, with the document's own section/table/figure number alongside,
because the two rarely agree.

Nothing in this document is engineering opinion. Where a change is a judgement call rather
than a datasheet requirement, it is marked **[judgement]** and the reasoning is given.

**Status: 14 of 14 parts documented.** SW3 is verified against a drawing that exists only as a screenshot — see its provenance warning.

---

## U1 — ESP32-S3-WROOM-1-N8R2 (Espressif)

`hardware/datasheets/ESP32-S3-WROOM-1.pdf`, Datasheet v1.8

| # | Change required | Datasheet reference | Current state |
|---|---|---|---|
| U1-1 | **Clear all copper from the antenna keep-out zone, on both layers.** Board coords x 23.0–41.0, y 37.36–43.39 | **PDF p.10**, §3.1 Pin Layout — diagram labelled "Keepout Zone"; **PDF p.45**, Fig 10.1 Module Dimensions — "Antenna Area", 7.49 mm | F.Cu **84.4 %** copper, B.Cu **81.3 %** copper. No keep-out zone exists. |
| U1-2 | **Set pin electrical types** — pins 1, 2, 40, 41 → `power_in`; pin 3 (EN) → `input`; pins 4–39 → `bidirectional` | **PDF p.11**, Table 3-1 Pin Definitions, "Type" column: `P` = power, `I` = input, `I/O/T` = input/output/tristate | All 41 pins are `unspecified` in `JLC.kicad_sym`. ERC electrical checking is off board-wide. |
| U1-3 | Pin numbering and names — **no change needed** | **PDF p.11**, Table 3-1 | Verified: 41 pins, 40 of 41 names match exactly. Pin 41 is named `GND` in the symbol vs `EPAD` in the table — Table 3-1 gives EPAD's Function as "GND", so this is correct and arguably clearer. |
| U1-4 | **Verified 2026-08-07** — EN and boot strapping match the reference design | Espressif reference schematic (WROOM-1 variant) | EN: R9 10 kΩ pull-up to 3V3 + C4 100 nF to GND + SW2 (reset to GND) — exactly the datasheet's 10 kΩ/0.1 µF RC. IO0: R10 10 kΩ pull-up + SW1 (boot to GND). GPIO45/46/3 float at their default straps (VDD_SPI = 3.3 V). USB polarity correct: pin 13 IO19 = D− = USB_DM, pin 14 IO20 = D+ = USB_DP, matching J2 A7/B7 = D− and A6/B6 = D+. Deviation from reference: no 499 Ω series on U0TXD and no ESD diode on EN — both belong to the auto-download circuit of a permanent USB-UART bridge; J1 here is passive program pads, so they are optional. |

**Note on variant:** the board uses **WROOM-1** (integrated PCB antenna), not WROOM-1U (external
connector). Datasheet **p.10** states explicitly that WROOM-1U "has no antenna keepout zone."
The keep-out requirement in U1-1 applies *because* this is the -1 variant.

---

## U4 — ST25DV04KC-IE6S3 (STMicroelectronics)

`hardware/datasheets/ST25DV04KC.pdf`, DS13519 Rev 8. Footprint
`ST25DV.pretty/SO-8_L4.9-W3.9-P1.27-LS5.9-BL.kicad_mod`

| # | Change required | Datasheet reference | Current state |
|---|---|---|---|
| U4-1 | **Change `(attr through_hole)` to `(attr smd)`** | **PDF p.151**, §10.1 SO8N package information — an SO8N is a gull-wing surface-mount package; all 8 pads in the footprint are already `smd` | `(attr through_hole)` on an all-SMD part. Drives position-file output and PCBA classification — the same failure class as the SW3 rejection. |
| U4-2 | **Extend the courtyard to enclose the pads.** Pads reach y ±3.644; courtyard stops at y ±1.960 | Derived from the land pattern, **PDF p.151**, Fig 85 | Pads sit **1.684 mm outside the courtyard** on both sides. DRC cannot detect encroachment on most of this part's copper. |
| U4-3 | **Add `F.Fab` body outline: 4.9 × 3.9 mm** (D typ × E1 typ) | **PDF p.151**, Table 259 SO8N Mechanical data — D = 4.800/4.900/5.000, E1 = 3.800/3.900/4.000 | No `F.Fab` geometry at all. |
| U4-4 | **Fix the 3D model path** to `${KIPRJMOD}/…` | n/a — repo hygiene, not a datasheet item | `nfc_integration/ST25DV.3dshapes/…`, relative to a directory that does not exist. |
| U4-5 | **[judgement]** Consider redrawing pads to ST's recommendation | **PDF p.151**, Fig 85 SO8N Footprint example — 0.6 mm pad width ×8, 1.27 mm pitch, 6.7 mm outer span, 3.9 mm inner gap (⇒ 1.4 mm pad length) | See table below. Deviates but will function. |

### U4-5 detail — land pattern vs Figure 85

| Dimension | Datasheet (Fig 85) | Footprint | Delta |
|---|---|---|---|
| Pitch | 1.27 mm | 1.27 mm | ✓ |
| Pad width | 0.60 mm | 0.574 mm | −4 % |
| Pad length | 1.40 mm | 1.888 mm | **+35 %** |
| Outer span | 6.70 mm | 7.288 mm | +0.59 mm |
| Inner gap | 3.90 mm | 3.512 mm | −0.39 mm |

**Verdict: functional, not correct.** Pads are longer than ST recommends in both directions.
Outward extension is harmless and aids inspection. Inward extension is the questionable half —
ST puts the inner pad edge flush with the body (E1 = 3.9 mm), and this footprint runs **0.194 mm
under the package on each side**. At 1.27 mm pitch that is unlikely to cause wicking, and the
narrower pad still covers the lead (b = 0.28–0.48 mm, **Table 259**). Joints will form.

This is a *deviation from the manufacturer's recommendation that nobody had compared*, not a
defect that stops the board working. Fixing it is the same work as U4-2 and U4-3, so do all
three together if the footprint is redrawn.

---

## SW3 — MSK12C02 (SHOU HAN) — VERIFIED against the manufacturer drawing

`hardware/datasheets/MSK12C02.pdf` (7-page specification) and
`hardware/datasheets/MSK12C02-outline-drawing.png` (mechanical drawing, from the LCSC
product page — **not** in the PDF).

**No change required.** Every checkable dimension of KiCad's shipped
`Button_Switch_SMD.pretty/SW_SPDT_Shouhan_MSK12C02.kicad_mod` matches the drawing:

| Feature | Drawing | Footprint |
|---|---|---|
| Mounting holes | 2 × Ø0.85, 3.0 mm apart | 2 × Ø0.85 NPTH at (±1.5, 0) |
| Post diameter on the part | Ø0.75 ±0.1 | 0.10 mm clearance in the hole |
| Signal pads | 0.6 × 1.3, spacing **1.5 and 3.0** | −2.25 / 0.75 / 2.25 |
| Shield pads | 1.05 × 0.7, outer 8.4 / inner 6.3 | ±3.675, ±1.1 |

### Two traps recorded, because both cost time

**The non-uniform pin spacing is correct.** 1.5 mm on one side and 3.0 mm on the other looks
like a library error and is not — the drawing dimensions it that way. Do not "fix" it.

**The specification text contradicts the drawing.** §2.4 states "1 pole, 1 throw" and §2.3
says "tactile feedback", and the cover calls the part 轻触开关 (*tactile switch*). The
drawing's 电路图 shows ①②③ plus ④ as shield — unambiguously SPDT. The text sections of that
PDF are a vendor template with the wrong product's content; **the drawing is the authority.**

**Three prongs vs two holes:** the part has **two** Ø0.75 mounting posts, which is what the
two holes are for. The three items that read as vertical prongs in the 3D render are the
signal terminals ①②③ — flat 0.15 mm tabs that solder to the surface, per the end view and
the mounting diagram. If the STEP model renders them as vertical pins it misrepresents the
part; cosmetic only, no fabrication consequence.

### Provenance warning

The mechanical drawing exists in this repo **only as a screenshot** of the LCSC product page.
The linked PDF (`lcsc_datasheet_2304140030_SHOU-HAN-MSK12C02_C431540.pdf`) is byte-identical
to `MSK12C02.pdf` and contains no drawing — verified by MD5. Its §8.1 refers the reader to an
"outside drawing page" that is not distributed with it. A screenshot is a fragile primary
source for the one part that has already been rejected once by a fab. Replace it when a
proper copy can be obtained.

---

## Passives — land patterns not changed

| Part | Datasheet | Package data | Action |
|---|---|---|---|
| CC0603KRX7R9BB104 (C1–C6) | `CC0603KRX7R9BB104-YAGEO-CC-series.pdf` | 0603: 1.6 ±0.15 × 0.8 ±0.15 × 0.8 ±0.15 | none — uses KiCad's IPC-7351 land |
| CL21A106KAYNNNE (C8) | `CL21A106KAYNNNE-Samsung-CL21A-series.pdf` | CL21A = 0805 (2012) | none — as above |
| CL21A226MAQNNNE (C9, C10) | same Samsung series document | CL21A = 0805 (2012) | none for the footprint — **see below** |
| 0603WAF series (R1–R14) | `UNI-ROYAL-0603WAF-series.pdf` | 0603 thick film | none — as above |

**C10 — resolved 2026-08-07.** Schematic `Value` corrected from `100uF` to `22uF` to match
the MPN `CL21A226MAQNNNE` actually on the BOM. The rail carries C9 + C10 = 44 µF of bulk,
and the ME6211C33 LDO requires only 1 µF at its output, so 22 µF is electrically sound.
The BOM keeps its note to consider a 1206-size 100 µF next revision for extra WiFi-burst
headroom on coin-cell power.

---

## Remaining work — datasheets now held, changes not yet made

| Part | Manufacturer | LCSC | Refs | Outstanding |
|---|---|---|---|---|
| **LSM6DS3TR-C** | STMicroelectronics | C967633 | U2 | LGA-14, 0.5 mm pitch — the tightest land on the board. Courtyard 0.098 mm inside the pads on all four sides. No `F.Fab`. Dead 3D model path. |
| **CR2032-BS-6-1** | Q&J | C70377 | BT1 | Courtyard **2.240 mm** inside the pads. `(attr through_hole)` on an SMD holder. Footprint named "TH" while its own 3D model is named "SMD". Keep-out needed under the cell (74 % copper there today). |
| **TS-1187A-B-A-B** | XKB Connection | C318884 | SW1, SW2 | Courtyard 0.950 mm inside the pads. No pin-1 marker. Dead 3D model path. |
| **KT-0603R** | Hubei KENTO | C2286 | D1–D24 | ×24 placements. **Zero** courtyard clearance in y. Ø0.20 mm silk dot centred on pad 1's corner — ink on the land, on every one. Dead 3D model path. |
| CC0603KRX7R9BB104 | YAGEO | C14663 | C1–C6 | Uses KiCad's IPC-7351 land — low priority. Confirm dielectric/voltage. |
| CL21A106KAYNNNE | Samsung | C15850 | C8 | As above. |
| CL21A226MAQNNNE | Samsung | C45783 | C9, C10 | Resolved: schematic Value corrected to 22 µF, matching the MPN. |
| 0603WAF-series | UNI-ROYAL | C22962/25804/23162/25803 | R1–R14 | As above. |
| **C12** | — | *none* | C12 | No part chosen. 62 pF NP0, 56–68 pF window, tuned against the coil after VNA. The ST25DV datasheet sets the target; the part decision comes after that. |

---

## How to read a datasheet for this purpose

For each part, four things produce four changes:

1. **Mechanical data table** (dimensions D, E, E1, b, e) → the `F.Fab` body outline
2. **Recommended footprint / land pattern figure** → pad size, pitch, span
3. **Pin definitions table, "Type" column** → pin electrical types, which is what makes ERC work
4. **Any keep-out, thermal or layout note** → zones and placement constraints

If a datasheet gives no recommended land pattern, IPC-7351 is the fallback authority — and we do
not hold it. Record that as a gap rather than inventing a pattern.
