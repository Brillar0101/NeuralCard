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
