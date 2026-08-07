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

## After GND stitching

`after-gnd-stitching.rpt` — **40 violations, 3 unconnected.** Four stitching vias added,
0.6/0.3 mm to match the Default net class. No new violations: the count is unchanged and
only `unconnected_items` moved, 7 -> 3.

GND groups went 8 -> 4; the main plane grew 4,170 -> 5,245 mm2.

Connected to the main plane:
- **U1.41, the ESP32's own ground/thermal pad (9 sub-pads)** - via at (39.025, 37.369)
- BT1.2, C8.2, C4.2 - via at (47.298, 10.005)

Merged into the top-edge cluster but still not reaching main:
- U4.4 (NFC ground) - via at (7.758, 6.026)
- C11.2 - via at (10.806, 5.734)

### What a via cannot fix, and why

Three groups remain, stranding U2.6/U2.7 (the IMU's only grounds), C1.2, C5.2, C2.2 and the
NFC ground now chained to them. **None has a via site**: there is no point where the island's
copper on one layer sits over main-plane copper on the other. A via joins layers at a point;
it cannot bridge a gap that exists on both layers at once.

All of them lie in the top-edge strip, y 4.2-22, which is the region fragmented by the ~60 mm
copper-free band at y 3.4-5.0 running x 15-80 on both layers - the slot cut by the signal
bundle feeding the LED resistor row. That band is also why 94% of IMU_INT, 88% of SDA and 82%
of SCL run with no reference copper beneath them.

So the remaining three are one defect, not three: the plane is severed across the top of the
board. Fixing it is a routing change - move the LED resistor bundle so the pour can close -
not a stitching job. Recorded rather than forced.

## After USB power routing (inline, direct)

after-usb-power-routing.rpt - 41 violations, 13 unconnected.

Power nets routed directly via the pcbnew API, geometry-queried per segment, DRC-iterated
on a copy through six revisions: VBUS (J2 both pads -> F.Cu trunk over the phase-1 +3V3
wall -> LDO, C6, U5, Q1 gate, R13), +3V3 (U3.5 -> C9/C10 rail tie -> C7), VBAT_SW
(SW3.3 -> F.Cu hop over the VBAT feed -> Q1 source). R8 rotated 90 so CC2 can enter
axially. J2 given a 0.09mm local clearance - its 0.5mm-pitch pads violate the 0.2 class
rule among themselves; physical gap stays at JLCPCB's published 0.1 minimum.

Delta vs 40-violation baseline: +1 footprint_type_mismatch on J2, accepted with reason:
hybrid SMD connector with PTH shell anchors; attr stays smd so the CPL keeps it.
Unconnected 13 = 3 pre-existing islands + 10 ratsnest gaps of the unrouted USB_DP/USB_DM
pair. U1 pads 13/14 now carry USB_DM/USB_DP (were unconnected- placeholders).

REMAINING: the DP/DM differential pair. USB-C interleaves the A/B pins (B7 DM, A6 DP,
A7 DM, B6 DP at 0.5mm pitch) so pairing them to U5 requires F.Cu via crossings, and the
45mm run to U1 pins 13/14 needs the lane plan: DP y16.05 / DM staggered, turn columns
west of U1's left pad column, entries from west/north. Corridor analysis is in the git
history of this file's session notes.
