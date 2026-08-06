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
