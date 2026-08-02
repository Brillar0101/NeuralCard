# NeuralCard — Changelog

Hardware revisions and fab-affecting fixes. Newest first.

---

## [Unreleased] — branch `fix/sw3-msk12c02-footprint`

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

These are open as of 2026-08-02 and are **not** fixed by the commits above.

### 1. SW3 exists on the PCB but not in the schematic

`NeuralCard.kicad_sch` contains only SW1 (BOOT) and SW2 (RESET). There is no SW3 symbol in
either the committed or the working-tree schematic, and no `VBAT` net anywhere in the
schematic — the PCB's `VBAT` net has no schematic counterpart. SW3's pad nets were assigned
directly in the layout.

Consequences:

- Running **Tools → Update PCB from Schematic** in KiCad will flag SW3 as an extra footprint
  and can delete it, silently reverting the DFM fix.
- ERC cannot verify the power path through the switch.
- `gen_schematic.py` regenerates the schematic from source and will not produce SW3.

Fix requires adding an SPDT symbol to the schematic with pad 2 on `VBAT`, pad 3 on `+3V3`,
pad 1 open, then re-annotating so the PCB and schematic agree.

### 2. Uncommitted schematic drift in the working tree

`NeuralCard.kicad_sch` and `JLC.kicad_sym` carry large uncommitted changes — a KiCad 10
re-save of an older file. Roughly 15,000 lines changed across the two.

| | Committed (HEAD) | Working tree |
|---|---|---|
| File format | `20250114` | `20260306` |
| Generator | eeschema 9.0 | eeschema 10.0 |
| Paper size | A2 | A3 |

This is the version KiCad opens today. Decide whether to keep or discard it before editing
the schematic, since it changes what any schematic fix would be applied to.

### 3. Documentation drift predating this branch

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
