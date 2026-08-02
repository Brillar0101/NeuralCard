# NeuralCard — Changelog

Hardware revisions and fab-affecting fixes. Newest first.

---

## [Unreleased] — branch `fix/sw3-msk12c02-footprint`

### Fixed — SW3 now exists in the schematic (2026-08-02)

SW3 had been added directly to the layout and had no schematic symbol, so
**Tools → Update PCB from Schematic** would have flagged it as an extra footprint and
deleted it, silently reverting the DFM fix. The board also carried a `VBAT` net with no
schematic counterpart.

Fixed in `gen_schematic.py` rather than by hand-editing `NeuralCard.kicad_sch`, so the
switch survives the next regeneration:

- `LIBSYMS` gains `Switch:SW_SPDT`, `PIN_XY` its pin geometry, `FP` maps SW3 to
  `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02`.
- `section_power()` now routes the coin through the switch: BT1 pin 1 (+) drives `VBAT`,
  SW3 pin 2 (common pole) takes `VBAT`, pin 3 (closed throw) drives `+3V3`, and pin 1
  (open throw) carries an explicit no-connect.

KiCad's generic `Switch:SW_SPDT` numbers its common pole **pin 2**, which matches the
MSK12C02 pinout and the pad nets already on the board — so no custom symbol was needed and
no pin renumbering was involved.

Net changes, and nothing else moved:

| Net | Before | After |
|---|---|---|
| `+3V3` | `BT1.1` … | `SW3.3` … (coin no longer feeds the rail directly) |
| `VBAT` | did not exist in schematic | `BT1.1`, `SW3.2` |
| `SW3.1` | — | unconnected (open throw, no-connect flagged) |

**Verification.** Schematic netlist checked pad-by-pad against `NeuralCard.kicad_pcb`:
**174 schematic pads, 173 PCB pads, 0 net mismatches** — the one difference is SW3 pad 1,
unconnected on both sides. Update PCB from Schematic is now a connectivity no-op. ERC: **0
errors, 41 warnings**, identical to the count before this change (all 41 are the benign
`pin_to_pin` notices inherent to easyeda2kicad-imported symbols).

The generator was also confirmed to reproduce the previously committed schematic exactly —
53 nets and 53 components, zero differences — before the switch was added, so regenerating
loses nothing.

### Fixed — SW3 power switch footprint (`a316055`, 2026-07-31)

JLCPCB rejected SW3 at DFM review on PCBA order **SMT026072863054**: the part they had
selected, **C431540** (SHOU HAN MSK12C02), did not fit the pads on the board.

Root cause: SW3 was added by hand in `b2ccb56` and never went through `gen_schematic.py` /
`place_pcb.py`, so it carried an improvised land pattern. The BOM listed the part as
"select-at-order" with a note to verify the footprint against whatever got chosen. That
verification never happened.

| | Before (`b2ccb56`) | After (`a316055`) |
|---|---|---|
| Footprint | `""` — unnamed, hand-drawn land | `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` |
| Value | `""` — empty | `MSK12C02` |
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

**Net mapping — unchanged by this fix.** Pad 2 is the common pole on `VBAT`, pad 3 the closed
throw on `+3V3`, pad 1 the open throw (intentionally netless). Sliding one way ties the coin
to the rail; the other way parks the pole on a floating throw. Standard SPDT-as-on/off.

The four `SH` tabs are deliberately left netless. They are the retention frame, and the
datasheet does not state that the frame is isolated from the contacts — tying them to GND
would risk shorting the coin cell. They still solder down for mechanical retention.

**Verification.** DRC clean under the project rules (0 violations, 0 unconnected). Measured
against the same ruleset, the board carries the same silk-art violation count as before the
change.

**Fab package regenerated.** Both NPTH holes appear in the drill file at X142.111 / Y-62.943
and Y-65.943. CPL places SW3 at 142.1112, -64.4434 rotated -90, Bottom. BOM names C431540
outright instead of select-at-order.

### Added — reproducible fab tooling (`a316055`)

- `tools/fix_sw3_footprint.py` — documents and applies the footprint swap.
- `tools/export_fab.py` — regenerates the whole JLCPCB fab bundle in one command. Writes
  Protel-extension gerbers directly, so no stray `.gbr` duplicates are produced. The zip
  contains gerbers and drill only; BOM and CPL upload separately.

### Added — hardware power switch (`b2ccb56`, 2026-07-22)

SW3 introduced as a physical on/off slide switch in series between the coin cell and the
`+3V3` rail, alongside ground repairs and a DRC cleanup. This supplements — it does not
replace — the firmware deep-sleep power-button behavior on SW1/GPIO0 described in
`DESIGN.md` §8.

Added directly to `NeuralCard.kicad_pcb` without a matching schematic symbol. See Known
Issues.

---

## Known issues

Open as of 2026-08-02.

### Resolved on this branch

- **SW3 missing from the schematic** — fixed above; schematic and PCB now agree on every pad.
- **KiCad 10 re-save drift** — `NeuralCard.kicad_sch` and `JLC.kicad_sym` had ~15,000 lines
  of uncommitted working-tree changes from a KiCad 10 re-save (format `20250114`→`20260306`,
  eeschema 9.0→10.0, paper A2→A3). Discarded on 2026-08-02; the schematic is back to the
  generator's canonical KiCad 9 / A2 output. **Open the project in KiCad 9, or decline the
  format-upgrade prompt in KiCad 10**, or the drift returns the moment the file is saved.

### 1. Documentation drift predating this branch

`BOM.md` sections 1–2 and `DESIGN.md` §3 still describe the v2-removed USB-C power path
(J1, D0, U3 LDO, Q1 P-FET, R7/R8 CC resistors, R13 bleeder, C6/C7). Those nine parts are
absent from the current CPL. `DESIGN.md` §0 records the removal but the downstream sections
were never updated. Out of scope for this branch.

---

## Current placement count

52 placements per `fab/NeuralCard-cpl.csv`:

| Group | Refs | Qty |
|---|---|---|
| Neuron LEDs | D1–D24 | 24 |
| Resistors | R1–R6, R9–R12, R14 | 11 |
| Capacitors | C1–C5, C8–C12 | 10 |
| Switches | SW1, SW2, **SW3** | 3 |
| ICs / module | U1, U2, U4 | 3 |
| Coin holder | BT1 | 1 |

Only non-soldered item remains the CR2032 coin itself.
