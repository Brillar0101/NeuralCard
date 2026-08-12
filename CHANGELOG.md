# NeuralCard: Changelog

Hardware revisions and fab-affecting fixes. Newest first.

## v2.3.1

Audit against the "6 common PCB design mistakes" checklist, two findings fixed.

- **Sharp corners eliminated.** Four acute trace vertices (three 45-degree, one
  83-degree) chamfered; a fifth "0-degree corner" turned out to be a duplicate
  track left by the power-repair routing and was deleted. Zero corners below
  90 degrees remain.
- **U1 decoupling fixed.** C2 relocated from 11.1 mm to 2.8 mm from the
  ESP32's power pin, sitting directly beside pins 1 and 2. C2 was a leaf
  component - a dead-end +3V3 stub plus a 16 mm ground bridge - so the move
  cost nothing and let 6 track segments and 4 vias be deleted outright.
  No schematic change: same 100 nF between the same two nets.
- Verified after: DRC 0 violations, 0 unconnected, every net a single
  connected cluster. Fab files, CPL and renders regenerated.

Full findings and remaining backlog in `docs/PCB-AUDIT.md`.

---

## [Unreleased]: branch `fix/sw3-msk12c02-footprint`

### Changed: repository reorganized into folders (2026-08-03)

Root shrank from 18 loose files to `README.md`, `CHANGELOG.md`, `LICENSE` and four
directories:

| Directory | Contents |
|---|---|
| `hardware/` | KiCad project (`.kicad_pro/sch/pcb`), symbol libs, `.pretty` footprints, lib tables, `board_outline`, `qr_matrix.json` |
| `fab/` | Release deliverables, now including `BOM_JLCPCB.csv` |
| `docs/` | `DESIGN.md`, `BOM.md`, schematic PDF |
| `render/` | Board renders |

The KiCad project moved as a unit, so every `${KIPRJMOD}` library reference is untouched.
All moves are git renames, history follows each file. Doc links, `.gitignore` anchors and
the fab export path updated to match. Verified from the new layout: ERC 0 errors /
41 warnings, DRC 0 violations, identical to before the move.

The untracked generation scripts moved to `hardware/` + `hardware/tools/` beside the files
they operate on (they derive paths from their own location, so they keep working).

## [v2.2.2]: 2026-08-03

Closes out the two items left open at v2.2.1 and syncs the silkscreen with the release tag.

### Fixed: isolated GND pour islands: 27 → 0 (`isolated_copper`)

The v2.2 regression, resolved at its root. the pour stitching step relaxed the pours to
AREA-mode island removal so candidate islands survive long enough to receive a stitching
via, but never restored the strict mode, so every island it couldn't reach stayed isolated
copper forever. It now restores `ISLAND_REMOVAL_MODE_ALWAYS` after the loop converges and
refills: via-stitched islands are connected and survive; unreachable orphans are purged.

**DRC: 0 violations.** The 5 remaining unconnected notices are same-net GND zone fragments,
identical in kind and count to the v2.1 baseline.

### Fixed: R14 edge clearance (`PM-002`)

Moved 52.3 → 51.9 mm, putting its courtyard past the 1.0 mm handling/depaneling
recommendation. Also cleared the silk-edge-clearance warning that its reference designator
caused. Zero PM-002 findings remain.

### Fixed: silkscreen version now matches the release

v2.2.1 shipped with `v2.2` on the silk. The board now reads **v2.2.2**, matching the tag.

### Verification

- **100% routed**, freerouting score 995.19, zero unrouted
- **DRC: 0 violations** (v2.1: 9 · v2.2: 29 · v2.2.1: 28 · **v2.2.2: 0**)
- PCB analyzer: **0 errors, 1 warning**, `TE-001` test points, N/A for a business card
- 642 tracks, 83 vias; CPL 52 placements, fiducials excluded
- Netless-by-design pads: 10 (ANT1 escape, SW3 2×NPTH + 4×SH, 3 fiducials)

---

## [v2.2.1]: 2026-08-03

Two findings from the first full analyzer run against the *v2.2* board. Both were real; one
was a genuine footprint defect the earlier "probably an artifact" call had half-right.

### Fixed: the NFC coil footprint had no courtyard (`PM-002`)

The coil footprint carried `allow_missing_courtyard`, so placement checkers
had nothing to measure and fell back to the footprint origin at (0, 0), the board corner,
reporting **"ANT1 is 0.0 mm from board edge"**. The coil copper actually sits 2.65 mm inboard.

The reading was wrong but the cause was a real defect: a footprint without a courtyard can't
be collision-checked. Now emits a `B.CrtYd` box around the drawn extent plus the standard
0.25 mm margin. C12 moved 13.4 → 12.9 mm, since the new courtyard clipped its by 0.1 mm.

### Fixed: no fiducials (`FD-001`)

Three `Fiducial_1mm_Mask2mm` targets on B.Cu at (3.5, 3.0), (3.5, 50.5) and (81.0, 50.5),
an L pattern, asymmetric so the placement machine cannot mistake board orientation. Excluded
from BOM and CPL, so the placement count stays 52. Justified by the 0.28 mm minimum pad on
the LGA-14 IMU.

### Verification

- **100% routed**, freerouting score 995.36, zero unrouted
- **PCB analyzer errors: 0** (was 2). Findings 13 → 11; both remaining are warnings
- 586 tracks; DRC 0 clearance, 0 crossing, 0 courtyard-overlap violations
- Isolated GND pour islands **28 → 27**, still the open regression from v2.2
- CPL 52 placements, fiducials correctly excluded

### Still open

`PM-002` R14 at 0.95 mm from the board edge (0.05 mm under the 1.0 mm recommendation) and
`TE-001` test-point coverage, which does not apply to a business card. `LR-001` still fires
24 times on the charlieplex matrix it misreads.

---

## [v2.2]: 2026-08-02

Board revision driven by the kicad-happy analysis. **The headline is decoupling.**

### Fixed: decoupling capacitors were 25 mm from the ICs they serve

Placement dealt every passive into two cosmetic edge rows by list order, ignoring which
IC each cap belonged to. The caps were correctly wired and completely ineffective:

| IC | v2.1 | v2.2 |
|---|---|---|
| U1 ESP32-S3 | **24.8 mm** | 11.4 mm |
| U2 IMU | 10.8 mm (its own C5 was **42 mm** away) | **4.0 mm** |

Neither ERC nor DRC can see this, connectivity was always correct. C1/C2 now flank the
module, C3/C4/C8 sit in the 6 mm corridor beside it (rotated 90° to fit), C5 is 4 mm from the
IMU. C9/C10 (22 µF ride-out, not HF) stay in the edge row; keeping them out of the corridor
is what let the output-column charlieplex lines route.

### Fixed: SW3 was missing from the placement table

Added by hand in `b2ccb56`, it never entered the placement data, so this re-place would have
dropped it to the default centre slot and silently undone the DFM fix. Now pinned at
81.455, 28.0, rotated -90.

### Fixed: stale internal paths (2026-08-03)

Local tooling referenced a directory the project no longer lives in; corrected.

### Changed: v2.1 → v2.2 on the silkscreen, fab package and renders regenerated

### Verification

- **100% routed**, freerouting score 995.36, zero unrouted connections
- **0 unconnected pads.** The 7 reported are netless by design: ANT1's escape, SW3's two NPTH
  holes and four shield tabs
- 631 tracks, 79 vias (v2.1: 465 / 57)
- ERC 0 errors / 41 warnings; DRC 0 clearance and 0 crossing violations
- CPL still 52 placements; SW3 at 81.4550, -28.0000, Bottom, -90

**Known regression:** isolated GND pour islands went from 5 to 28. Redundant copper the
stitcher can't reach with a via; every GND pad is track-routed, so it is cosmetic rather than
functional. stitching converges there. Worth revisiting before a production run.

**Not fixed in v2.2:** `FD-001` (no fiducials), `DFM-001`/`DFM-002` (0.1 mm annular ring below
IPC Class 2), `PU-001` (INT2 pull-up, the pin is unused). Thermal analysis still SKIPPED: it
needs datasheet PDFs in an extraction cache, and LCSC serves no datasheet URLs for these parts.

**This supersedes the v2.1 fab package.** Order SMT026072863054 was placed against v2.1.

---

### Removed: internal tooling untracked (2026-08-02)

Local build tooling is no longer distributed with the repository; the published design is
the committed `NeuralCard.kicad_sch` and `NeuralCard.kicad_pcb`. The README section that
documented a rebuild-from-source workflow was removed with it, since the repo no longer
ships what it described. Editing the design means editing the KiCad files directly.

### Removed: automated design review CI (2026-08-02)

Dropped the review workflow, its render script and `docs/design-review.md`. The workflow worked, it ran clean on both a PR and a push, and
committed its own refresh, but it added a bot commit loop and a generated section to a repo
whose value is the board, not its CI.

**The mermaid diagrams stay.** They are hand-authored, not tool output, and they are the part
that helps someone landing on the repo. The three descriptive badges stay; the workflow-status
badge went with the workflow.

The two real fixes the review surfaced (`RS-001`, LED `Value`) are already merged and remain.
Findings recorded for later: `SS-001` (0% MPN coverage), `DFM-001`/`DFM-002` (0.1 mm annular
ring, below IPC Class 2), `FD-001` (no fiducials).

### Changed: board renders regenerated (2026-08-02)

`render/NeuralCard_front_v21.png` and `_back_v21.png` were last updated in `b2ccb56`
(22 Jul), one PCB commit **before** the SW3 footprint swap in `a316055` (31 Jul), so the
published images still showed the old improvised switch land. Regenerated from the current
board with `kicad-cli pcb render` at 1568×1040, transparent background, matching the previous
framing. SW3 now appears with its correct MSK12C02 body.

### Changed:.gitignore expanded (2026-08-02)

Rebased on [github/gitignore's KiCad.gitignore](https://github.com/github/gitignore/blob/main/KiCad.gitignore).
Adds KiCad backup/autosave patterns (`*.bak`, `*.kicad_sch-bak`, `_autosave-*`, `*-save.*`),
ERC and cache-library output, Python artifacts (`__pycache__/`, `*.py[cod]`, `.venv/`),
3D exports (`*.step`), superseded fab snapshots (`fab.old-*/`), and editor/OS noise. This
takes `JLC.bak` and `fab.old-jul22/` out of the working tree's untracked list.

Deliberately still tracked: `BOM_JLCPCB.csv` and `fab/*.csv` are release deliverables uploaded
to JLCPCB, not incidental KiCad exports, and the generator scripts are the design source,
see README, "The board is generated, not drawn."

### Added: automated design review in CI (2026-08-02, removed same day)

`.github/workflows/design-review.yml` runs [kicad-happy](https://github.com/aklofas/kicad-happy)
against the schematic and PCB. On a PR it posts a diff-only comment (just what that PR
changed); on `main` it refreshes the README summary and commits the full report to
`docs/design-review.md`. SPICE is disabled, no ngspice on the runner and nothing analog here.

A render step turned the analyzer JSON into the README block. It grouped findings
by `rule_id`, so a detector that fires 24 times is one row rather than 24, and applies a
suppression list with a stated reason per rule instead of silently dropping anything.

`README.md` gains four badges and a **How it's wired** section with two mermaid diagrams,
the power path through SW3, and the 6→8→10 inference path. Coloured from the PatternFly
palette, matching the Red Hat faces already plotted on the silkscreen (§Typography).

**Baseline: 81 findings, 3 errors, 5 warnings, 49 info after suppression.**

One suppression matters. `LR-001` fires once per LED claiming no current-limiting resistor,
which is wrong: the matrix is charlieplexed, so R1, R6 limit current on the six shared GPIO
drive lines. Left in, it would be 89% of the error count. Note that `LA-AUD` tags the same
LEDs `[resistor_limited]`, so the toolchain contradicts itself here.

Findings worth acting on, recorded but not yet fixed: `SS-001` (0% MPN coverage, the root
cause of the SW3 drift), `DFM-001`/`DFM-002` (0.1 mm annular ring, below IPC Class 2's
0.125 mm), and `FD-001` (no fiducials, with 0.28 mm minimum pad on the LGA-14 IMU).
`PM-002`'s "ANT1 is 0.0 mm from board edge" is almost certainly the net-tie footprint origin
rather than copper, the coil sits at x[2.5, 14.5] per §8.

### Fixed: LED value and VBAT source flag (2026-08-02)

Two findings from the first CI-equivalent run, both fixed at the schematic source:

- **`RS-001`, `VBAT` has no declared source.** Fallout from the SW3 symbol: a plain label
  carries no pin type, so strict checkers read the net as undriven. Added a `PWR_FLAG`.
  KiCad's own ERC passed without it; this satisfies the stricter check.
- **LED `Value` said `blue`** while the footprint and fab BOM have always been red. Corrected
  to `red`. Safe to change: the fab BOM is hand-maintained
  and not generated from the schematic, so no fab output moves.

Verified: netlist unchanged on every real pin, **174 schematic pads vs 173 PCB pads, 0
mismatches**, ERC still **0 errors / 41 warnings**. The analyzer now reads
`LED D1 (red) [resistor_limited]` and `RS-001` is gone.

### Fixed: LED part number contradicted the board (2026-08-02)

Found by running [kicad-happy](https://github.com/aklofas/kicad-happy)'s BOM and LCSC skills
against the project.

`BOM.md` listed D1, D24 as **blue** `C72041` while `BOM_JLCPCB.csv`, the PCB footprint
(`LED-SMD_L1.6-W0.8-R-RD`) and `DESIGN.md` §0 all specify **red** `C2286`. Ordering from the
human-facing BOM would have bought the wrong colour for 24 of 52 placements, and the LCSC
check found `C72041` down to **14 units in stock**, so the order would have failed outright.

- `BOM.md` D1, D24 row corrected to `C2286` / KT-0603R.
- Ordering note 2 rewritten: red is the settled v2 decision, not a future suggestion.
- U1 corrected from `N16R8` to **`N8R2`**, the part `C2913204` actually resolves to. This was
  already noted in `DESIGN.md` §8 but never fixed in the BOM table.
- New `BOM.md` §3b records all 14 codes with resolved MPN, stock and unit price
  (parts ≈ **$6.91/board**).

`C431540` independently confirmed as MSK12C02 with ~99k in stock, the SW3 fix holds.

Still outstanding: the schematic's `Value` field for D1, D24 reads `blue`
while the footprint and fab outputs are red. Cosmetic, it does not
reach the netlist or the fab package, but it should be corrected in the generator.

### Fixed: SW3 now exists in the schematic (2026-08-02)

SW3 had been added directly to the layout and had no schematic symbol, so
**Tools → Update PCB from Schematic** would have flagged it as an extra footprint and
deleted it, silently reverting the DFM fix. The board also carried a `VBAT` net with no
schematic counterpart.

Fixed at the schematic source rather than by hand-editing `NeuralCard.kicad_sch`, so the
switch survives the next regeneration:

- `LIBSYMS` gains `Switch:SW_SPDT`, `PIN_XY` its pin geometry, `FP` maps SW3 to
  `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02`.
- `section_power()` now routes the coin through the switch: BT1 pin 1 (+) drives `VBAT`,
  SW3 pin 2 (common pole) takes `VBAT`, pin 3 (closed throw) drives `+3V3`, and pin 1
  (open throw) carries an explicit no-connect.

KiCad's generic `Switch:SW_SPDT` numbers its common pole **pin 2**, which matches the
MSK12C02 pinout and the pad nets already on the board, so no custom symbol was needed and
no pin renumbering was involved.

Net changes, and nothing else moved:

| Net | Before | After |
|---|---|---|
| `+3V3` | `BT1.1` … | `SW3.3` … (coin no longer feeds the rail directly) |
| `VBAT` | did not exist in schematic | `BT1.1`, `SW3.2` |
| `SW3.1` |: | unconnected (open throw, no-connect flagged) |

**Verification.** Schematic netlist checked pad-by-pad against `NeuralCard.kicad_pcb`:
**174 schematic pads, 173 PCB pads, 0 net mismatches**, the one difference is SW3 pad 1,
unconnected on both sides. Update PCB from Schematic is now a connectivity no-op. ERC: **0
errors, 41 warnings**, identical to the count before this change (all 41 are the benign
`pin_to_pin` notices inherent to easyeda2kicad-imported symbols).

The generator was also confirmed to reproduce the previously committed schematic exactly,
53 nets and 53 components, zero differences, before the switch was added, so regenerating
loses nothing.

### Fixed: SW3 power switch footprint (`a316055`, 2026-07-31)

JLCPCB rejected SW3 at DFM review on PCBA order **SMT026072863054**: the part they had
selected, **C431540** (SHOU HAN MSK12C02), did not fit the pads on the board.

Root cause: SW3 was added by hand in `b2ccb56` outside the normal design flow, so it
carried an improvised land pattern. The BOM listed the part as
"select-at-order" with a note to verify the footprint against whatever got chosen. That
verification never happened.

| | Before (`b2ccb56`) | After (`a316055`) |
|---|---|---|
| Footprint | `""`: unnamed, hand-drawn land | `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` |
| Value | `""`: empty | `MSK12C02` |
| LCSC part | select-at-order | **C431540** |
| Signal pads | 3× 0.7 × 1.1 mm rect, 1.3 mm pitch | 3× roundrect, per manufacturer datasheet |
| Shield tabs | none | 4× `SH` retention pads |
| Locating holes | none | 2× 0.85 mm NPTH |
| 3D model | Copal DIP switch scaled to 0.62 (placeholder) | `SW_SPDT_Shouhan_MSK12C02.step` |
| Body size assumed | ~3 mm | 8 × 2.8 mm (actual) |

Nothing was going to seat on the original land.

**Orientation and placement.** The MSK12C02 is right-angle, so it is rotated 270° with its
pins facing inboard toward BT1 and the actuator facing the right card edge where a thumb can
reach it. Moved 0.546 mm inboard to leave 1.0 mm from courtyard to board edge for assembly.

**Net mapping, unchanged by this fix.** Pad 2 is the common pole on `VBAT`, pad 3 the closed
throw on `+3V3`, pad 1 the open throw (intentionally netless). Sliding one way ties the coin
to the rail; the other way parks the pole on a floating throw. Standard SPDT-as-on/off.

The four `SH` tabs are deliberately left netless. They are the retention frame, and the
datasheet does not state that the frame is isolated from the contacts, tying them to GND
would risk shorting the coin cell. They still solder down for mechanical retention.

**Verification.** DRC clean under the project rules (0 violations, 0 unconnected). Measured
against the same ruleset, the board carries the same silk-art violation count as before the
change.

**Fab package regenerated.** Both NPTH holes appear in the drill file at X142.111 / Y-62.943
and Y-65.943. CPL places SW3 at 142.1112, -64.4434 rotated -90, Bottom. BOM names C431540
outright instead of select-at-order.

### Added: reproducible fab refresh (`a316055`)

The JLCPCB fab bundle is regenerated in one reproducible pass rather than five remembered
commands, writing Protel-extension gerbers directly with no stray `.gbr` duplicates. The
zip contains gerbers and drill only; BOM and CPL upload separately.

### Added: hardware power switch (`b2ccb56`, 2026-07-22)

SW3 introduced as a physical on/off slide switch in series between the coin cell and the
`+3V3` rail, alongside ground repairs and a DRC cleanup. This supplements, it does not
replace, the firmware deep-sleep power-button behavior on SW1/GPIO0 described in
`DESIGN.md` §8.

Added directly to `NeuralCard.kicad_pcb` without a matching schematic symbol. See Known
Issues.

---

## Known issues

Open as of 2026-08-02.

### Resolved on this branch

- **SW3 missing from the schematic**, fixed above; schematic and PCB now agree on every pad.
- **KiCad 10 re-save drift**, `NeuralCard.kicad_sch` and `JLC.kicad_sym` had ~15,000 lines
  of uncommitted working-tree changes from a KiCad 10 re-save (format `20250114`→`20260306`,
  eeschema 9.0→10.0, paper A2→A3). Discarded on 2026-08-02; the schematic is back to the
  generator's canonical KiCad 9 / A2 output. **Open the project in KiCad 9, or decline the
  format-upgrade prompt in KiCad 10**, or the drift returns the moment the file is saved.

### 1. Documentation drift predating this branch

`BOM.md` sections 1 to 2 and `DESIGN.md` §3 still describe the v2-removed USB-C power path
(J1, D0, U3 LDO, Q1 P-FET, R7/R8 CC resistors, R13 bleeder, C6/C7). Those nine parts are
absent from the current CPL. `DESIGN.md` §0 records the removal but the downstream sections
were never updated. Out of scope for this branch.

---

## Current placement count

52 placements per `fab/NeuralCard-cpl.csv`:

| Group | Refs | Qty |
|---|---|---|
| Neuron LEDs | D1: D24 | 24 |
| Resistors | R1: R6, R9: R12, R14 | 11 |
| Capacitors | C1: C5, C8: C12 | 10 |
| Switches | SW1, SW2, **SW3** | 3 |
| ICs / module | U1, U2, U4 | 3 |
| Coin holder | BT1 | 1 |

Only non-soldered item remains the CR2032 coin itself.
