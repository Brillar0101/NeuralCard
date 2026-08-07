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

## After USB data PHY routing

after-usb-phy-routing.rpt - 41 violations (baseline + accepted J2 attr), 7 unconnected.

DP/DM routed from the connector through the ESD array. The USB-C interleave (B7-DM,
A6-DP, A7-DM, B6-DP at 0.5mm pitch) is topologically unroutable on one layer; resolved
with a compact DM dogbone east of the pad column (the NPTHs at y11.6/17.4 are 2mm away,
so the space behind the pads is usable) and an F.Cu via hop for A6 into B6's lane on
the west. DM crosses the DP U5 bridge on F.Cu. VBUS's U5 feed moved to F.Cu via-in-pad
to clear the west corridor.

REMAINING: U5 -> U1 (pins 13/14), ~48mm. The y16-18 corridor is the charlieplex highway
(CP1-6, CHX*, NFC_GPO, EN, +3V3 all live there - a first attempt drew 80+ violations
and was dropped on evidence). Needs its own corridor study; candidates: F.Cu lane, or
B.Cu along y12-13 north of the highway.

### U5 -> U1 corridor study, attempt 2 (F.Cu lanes): failed on evidence

Straight F.Cu lanes at y16.05/17.95 drew 77 USB-involved violations. The assumption
that F.Cu is empty is false: CP2 and CP4 route on F.Cu (the charlieplex uses both
layers), a CP4 via sits at (21.60, 20.44) - touching the only clean B.Cu entry to
U1 pin 13 - and the VBUS F.Cu riser at x71.6 blocks via placement at the U5 end.

Conclusion: no free corridor exists on either layer. The route requires either
(a) threading between individual charlieplex tracks with a full obstacle map of
the y12-22 band on both layers, or (b) first rerouting 2-3 CP tracks to open a
lane - option (b) is likely cheaper. Both need a dedicated session. The board is
committed clean at f393dd8 with the PHY section done and these two nets open.

## After DP/DM completion — USB fully routed

`after-usb-dpdm-complete.rpt` - **41 violations, 7 unconnected. Exact parity with the
pre-USB baseline: the entire USB-C addition costs zero new DRC items.**

Option (b) from the corridor conclusion, executed. Three charlieplex edits opened the lane:

- **CHX6** dipped south of the U1 pad row: its F.Cu horizontal at y17.97 crossed the only
  legal via window; redrawn through y16.5/16.85 with a short B.Cu bridge, clear of the
  17.36-18.86 pad band.
- **CHX4** moved off pad 14: its F.Cu approach camped directly over the pad, blocking the
  DM entry; shifted 0.6mm north to y18.75.
- **CP3** via nudged 0.2mm west at (66.27, 7.34) to widen the northern highway.

Then the pair, A* grid-routed at 0.1mm resolution against a clearance-inflated obstacle
map of every foreign net, waypoint-constrained where the free solver would trade legality
for length:

- **USB_DM**: U5 -> U1 pin 13, 75.9mm, 8 vias. Funnel out of the connector pocket, north
  highway at y8.3 on F.Cu (parts are on the back, so F crosses the pad rows freely), west
  descent at x40, under-row approach into the pad from the south.
- **USB_DP**: U5 -> U1 pin 14, 100.1mm, 10 vias. Free-solved; threads the razor passages
  between the four parallel charlieplex diagonals.
- **VBUS**: U3 pad 1 -> pad 3 repair, 3.3mm, closing the last power gap.

Skew DM 75.9 vs DP 100.1mm is irrelevant at USB full-speed (12 Mbps): 24mm is ~130ps
against a 52ns bit half-period. Impedance is likewise uncontrolled and fine at FS.

Unconnected 7 = the 3 pre-existing GND islands (6 zone pairings) + the orphaned +3V3
fragment at (81.35, 19.4). The fragment predates this work and sits between J2's shell
anchors and the VBUS runs, where no legal lane exists on either layer at current
constraints; left recorded, not forced.

## After GND island bridges

`after-gnd-island-bridges.rpt` - **40 violations, 4 unconnected. One below the pre-USB
baseline: the dangling stitching via under the coin cell is gone.**

The island bookkeeping turned out optimistic. Walking the connectivity database pad by pad
showed **six** disconnected GND groups, not three: the earlier count treated
{BT1.2, C3.2, C4.2, C8.2} as main-plane when it was its own cluster, and C7.2 and C2.2
had each been stranded by the USB power routing slicing the pour around U3 and J2.

Three bridges routed, same A* grid method as the USB pair:

- **C7.2 -> C9.2**, 5.5mm, 2 vias - reconnects the LDO output cap ground.
- **C8.2 -> U1.41**, 44.3mm, 4 vias - ties the battery cluster (BT1, C3, C4, C8) into the
  ESP32 thermal pad, detouring around the charlieplex matrix.
- **C2.2 -> U1.1**, 18.1mm, 4 vias - down the alley west of U1's pad column.

Main plane: 22 -> 28 pads. Also fixed en route: J2's footprint carried a 0.09mm local
clearance override, below JLCPCB's 0.10 board minimum. It never fired because the pour
behind J2 used to be discarded as an isolated island; the C7 bridge revived that copper
and DRC caught it. Override raised to 0.10 - the connector's own pad-to-pad gaps measure
0.1000/0.1002, exactly at the fab's limit, so 0.10 is the only value that passes both ways.

### Three islands remain, each provably unroutable without moving signals

Exhaustive both-layer flood-fill from each island (via hops included) confirms no legal
0.2mm lane exists at current clearances:

- **{U2.6, U2.7}** - the IMU's only grounds sit in a sealed pocket: the LGA fanout walls
  it north and east, SDA/SCL wall it south, the NFC region west.
- **{C11.2, U4.4}** - the NFC ground chain is enclosed by the antenna coil and the LED
  resistor bundle on both layers.
- **{C1.2, C5.2}** - hemmed in by CP2/CP4's horizontals, the charlieplex diagonals and
  the new USB entries; the 5mm hop to C2.2 has no lane on either layer.

All three need the same cure the corridor study prescribed: shift the LED resistor bundle
(and for U2, the IMU fanout) so the pour can close. That is a layout change with RF and
matrix implications, out of scope for the USB-C branch. Unconnected 4 = these 3 island
edges + the orphaned +3V3 fragment behind J2.

## Zero

`zero-violations.rpt` - **0 violations, 0 unconnected. ERC: 0 errors, 0 warnings.**
Every net on the board is a single connected cluster, including GND (42 pads, one plane).

What it took, beyond the USB work above:

**Silk text (34).** Three separate root causes. The J1 pad labels were under the 0.8mm
height minimum - raised. The stroke-font texts were under 0.15mm - thickened. The
TrueType texts (Red Hat Display/Mono/Text at SemiBold) genuinely render strokes thinner
than JLCPCB's 0.15mm printable minimum at small sizes; DRC measures the cached glyph
polygons, so no pen-width setting can fix them. Weights raised to Bold/Black board-wide,
the six IMU-axis labels and headline texts rescaled, and twelve small functional labels
(instructions, URLs) converted to the KiCad stroke font, which is guaranteed printable.
Fontconfig trap recorded: the face string must be the fontconfig family name -
"Red Hat Mono" plus the bold flag, not "Red Hat Mono Bold", which silently substitutes
Andale Mono.

**Clearance shaves (2).** NFC_ANT_B and SCL sat 2-10 microns inside the 0.2mm class
clearance at U4's pads. Both nudged with 45-degree joins preserved.

**Courtyards (3).** C1-C6 carried 0.65mm courtyard margins - two and a half times the
IPC norm for an 0603 - which is what actually collided with U1's module courtyard;
trimmed to 0.30/0.25mm. J1 had no courtyard at all; drawn from its pad extents plus
0.25mm.

**J2 type mismatch (1).** Excluded per-item in the project file with the reason inline:
hybrid SMD connector with PTH shell anchors, attr stays smd so the CPL keeps it.

**The +3V3 fragment.** Unroutable for two sessions - because the router's grid ended at
x=80 and the board ends at x=85.65. With the full board in the grid it routed in one
pass: 12.4mm, zero vias, around J2's east side.

**The three GND islands.** The top-edge seal was three tracks: SDA and NFC_GPO on F.Cu
plus the +3V3 north rail on B.Cu, jointly closing y3.1-4.7 across the whole board while
the top 2.5mm of the card sat empty. Both +3V3 horizontals moved into that empty strip,
which opened a B.Cu crossing; the NFC ground chain (67mm), the C1/C5 group (58mm) and
the IMU grounds (18mm) then routed through it to the main plane. The IMU pocket
additionally needed one redundant +3V3 branch deleted - U2 was fed from both sides, and
the west diagonal was the wall; its cap chain re-fed locally (6.4mm).

**ERC.** The one warning was U2's SDO/SA0 strapped to 3V3 - the deliberate I2C address
select. pin_to_pin set to ignore with this note as the reason; it was the only instance.

Fab package regenerated to match: gerbers, drill, and a 61-component CPL including the
USB-C section.
