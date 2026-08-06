# DRC baselines — branch fix/footprints-from-datasheets, board unmodified

Captured before any footprint change reached the board. KiCad embeds footprints in
the .kicad_pcb, so library edits do not alter these until 'Update Footprints from
Library' is run. Diff against these afterwards.

| Run | Violations | Unconnected | Parity |
|---|---|---|---|
| baseline-default.rpt (project as configured) | 0 | 5 | not checked |
| baseline-parity.rpt (--schematic-parity) | 0 | 5 | 165 |
| baseline-all-promoted.rpt (29 classes -> error) | 414 | 5 | not checked |

Constraints at 0.0 in NeuralCard.kicad_pro: min_clearance, min_connection,
min_groove_width, min_silk_clearance, min_track_width, solder_mask_to_copper_clearance.
clearance and track_width sit at severity 'error' and cannot fire against a zero threshold.

kicad-cli 10.0.3. Board at commit 1001fda.

## After footprint update, zone refill and cell keep-out

| Run | Violations | Unconnected | Note |
|---|---|---|---|
| after-footprint-update.rpt | 9 | 5 | broken footprints stopped hiding real defects |
| after-refill-and-cell-keepout.rpt | 5 | 7 | antenna keep-out satisfied; more GND islands exposed |

The antenna `items_not_allowed` violations went to zero — finding B1 is resolved in copper.
Three zone-clearance violations also cleared.

Unconnected rose 5 -> 7 and one via became dangling, at (65.14, 36.75), which is 9.3 mm from
BT1's centre and therefore inside the new cell keep-out. Both are true findings: the ground
plane was partly held together by copper inside the ESP32 antenna area and under the coin
cell. Removing copper that should never have been there exposed how thin the real stitching
is. This is the same defect as B2 (isolated GND islands), now measured more honestly.

Still outstanding and unaffected by any of the above: six constraints at 0.0 in
NeuralCard.kicad_pro, so `clearance` and `track_width` remain unenforceable; and the 29
suppressed severity classes hiding 414 violations.

## After real fab constraints and a selective severity policy

`after-real-constraints.rpt` — **40 violations, 7 unconnected.** This is the first honest
number this board has produced.

Constraints set from JLCPCB's published 2-layer 1oz process (jlcpcb.com/capabilities):
min_clearance 0.0 -> 0.10, min_track_width 0.0 -> 0.10, min_connection 0.0 -> 0.10,
min_hole_to_hole 0.2 -> 0.45 (was looser than the fab allows), min_text_thickness
0.08 -> 0.15 (their minimum printable line width).

Setting constraints alone changed nothing, because the severities were suppressed too.
Both layers had to be lifted. Severities restored: missing_courtyard, footprint_type_mismatch,
extra_footprint, missing_footprint to error; text_thickness, text_height to warning.

Deliberately left at ignore, with reason: silk_over_copper and silk_overlap. These are 398
of the 438 violations and they are the front-face neural-network artwork - a design decision
by someone who looked, not negligence. Suppressing them at class level is defensible here
because per-object suppression across 398 items is impractical. Recorded so the choice is
visible rather than silent.

footprint_type_mismatch now reports 0: both footprints carrying attr through_hole on all-SMD
parts were corrected.

| Class | Count | Nature |
|---|---|---|
| text_thickness | 28 | board's own labels - RST, S/N, ax/ay/az/gx/gy/gz, OSHW mark - thinner than 0.15mm |
| unconnected_items | 7 | isolated GND islands |
| text_height | 6 | J1 pad labels at 0.7mm |
| courtyards_overlap | 2 | C2 against U1 |
| clearance | 2 | U4 pads vs SDA/SCL at 0.190-0.198mm |
| via_dangling | 1 | GND via under the coin cell, inside the new keep-out |
| missing_courtyard | 1 | ProgPads_1x6 (J1) |

JLCPCB also publishes a 1.0mm minimum silkscreen text height; min_text_height is left at 0.8
pending a decision, since raising it would flag most of the board's labelling.
