# Datasheet findings — what changes, and the page that says so

Every row is a change to the board or libraries, traced to the page, table or figure of the
manufacturer datasheet that mandates it. Page numbers are **PDF page numbers** in the file
held in `hardware/datasheets/`, with the document's own section/table/figure number alongside,
because the two rarely agree.

Nothing in this document is engineering opinion. Where a change is a judgement call rather
than a datasheet requirement, it is marked **[judgement]** and the reasoning is given.

**Status: 2 of 14 parts have datasheets.** Rows can only be written for parts whose datasheet
is in the repo. The rest are listed at the bottom as blocked.

---

## U1 — ESP32-S3-WROOM-1-N8R2 (Espressif)

`hardware/datasheets/ESP32-S3-WROOM-1.pdf`, Datasheet v1.8

| # | Change required | Datasheet reference | Current state |
|---|---|---|---|
| U1-1 | **Clear all copper from the antenna keep-out zone, on both layers.** Board coords x 23.0–41.0, y 37.36–43.39 | **PDF p.10**, §3.1 Pin Layout — diagram labelled "Keepout Zone"; **PDF p.45**, Fig 10.1 Module Dimensions — "Antenna Area", 7.49 mm | F.Cu **84.4 %** copper, B.Cu **81.3 %** copper. No keep-out zone exists. |
| U1-2 | **Set pin electrical types** — pins 1, 2, 40, 41 → `power_in`; pin 3 (EN) → `input`; pins 4–39 → `bidirectional` | **PDF p.11**, Table 3-1 Pin Definitions, "Type" column: `P` = power, `I` = input, `I/O/T` = input/output/tristate | All 41 pins are `unspecified` in `JLC.kicad_sym`. ERC electrical checking is off board-wide. |
| U1-3 | Pin numbering and names — **no change needed** | **PDF p.11**, Table 3-1 | Verified: 41 pins, 40 of 41 names match exactly. Pin 41 is named `GND` in the symbol vs `EPAD` in the table — Table 3-1 gives EPAD's Function as "GND", so this is correct and arguably clearer. |
| U1-4 | **[judgement]** Confirm EN has a pull-up and the boot strapping matches the reference design | Espressif reference schematic (the WROOM-1 variant, not WROOM-1U) — R1 10 kΩ on EN, ESD diode on EN, R3 499 Ω on U0TXD | **Not yet verified.** Net parse failed; needs checking against the schematic directly. |

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

## SW3 — MSK12C02 (SHOU HAN) — no datasheet held, but verified another way

The footprint is pad-for-pad identical to KiCad's shipped
`Button_Switch_SMD.pretty/SW_SPDT_Shouhan_MSK12C02.kicad_mod` — every `at`, `size` and `drill`
diffed, only the −90° placement rotation and B.Cu mirror differ. NPTH locators correct, LCSC
`C431540` matches the LCSC URL in that footprint's own `descr`, 3D model resolves through
`${KICAD10_3DMODEL_DIR}`.

**No change required.** Obtain the datasheet anyway — this is the one part where a fab rejection
has already been paid for, and verification against the source beats verification against
another library.

---

## Blocked — no datasheet, no rows can be written

| Part | Manufacturer | LCSC | Refs | Known defects awaiting the datasheet |
|---|---|---|---|---|
| **LSM6DS3TR-C** | STMicroelectronics | C967633 | U2 | LGA-14, 0.5 mm pitch — the tightest land on the board. Courtyard 0.098 mm inside the pads on all four sides. No `F.Fab`. Dead 3D model path. |
| **CR2032-BS-6-1** | Q&J | C70377 | BT1 | Courtyard **2.240 mm** inside the pads. `(attr through_hole)` on an SMD holder. Footprint named "TH" while its own 3D model is named "SMD". Keep-out needed under the cell (74 % copper there today). |
| **TS-1187A-B-A-B** | XKB Connection | C318884 | SW1, SW2 | Courtyard 0.950 mm inside the pads. No pin-1 marker. Dead 3D model path. |
| **KT-0603R** | Hubei KENTO | C2286 | D1–D24 | ×24 placements. **Zero** courtyard clearance in y. Ø0.20 mm silk dot centred on pad 1's corner — ink on the land, on every one. Dead 3D model path. |
| CC0603KRX7R9BB104 | YAGEO | C14663 | C1–C6 | Uses KiCad's IPC-7351 land — low priority. Confirm dielectric/voltage. |
| CL21A106KAYNNNE | Samsung | C15850 | C8 | As above. |
| CL21A226MAQNNNE | Samsung | C45783 | C9, C10 | As above — **and C10's schematic Value says `100uF` while this MPN is 22 µF.** Resolve. |
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
