# PCB audit — "6 Horribly Common PCB Design Mistakes"

Source: YouTube video `Z9nycymUd-I`, transcript pulled and checked point by
point against the board. Every finding below is measured from
`hardware/NeuralCard.kicad_pcb`, not assumed.

Verdict: clean on three of the six, real work on two, one does not apply.
**Two findings were fixed immediately and shipped as v2.3.1** (sharp corners,
U1 decoupling). The rest are backlog for whatever revision follows the first
prototype — each needs either a new component or disturbs verified copper,
so they are best decided once a physical board exists.

---

## 1. Incorrect traces — sharp angles ✅ FIXED

The video's rule: avoid interior angles below 90 degrees; acid traps and
field concentration at sharp corners. Measured on the board — five corners
with an interior angle under 89 degrees:

| Net | Location (mm) | Angle |
|---|---|---|
| +3V3 | 79.5, 8.8 | **0** (doubled-back segment) |
| CP6 | 43.5, 24.1 | 45 |
| CP5 | 67.8, 34.3 | 45 |
| NFC_ANT_B | 8.0, 14.2 | 45 |
| GND | 37.5, 33.8 | 83 |

**Resolved.** The 0-degree "corner" turned out to be a *duplicate track* —
two identical +3V3 segments stacked on the same path, a leftover from the
power-repair routing. Deleted. The other four were genuine acute vertices and
were chamfered (0.25-0.40 mm), converting each 45/83-degree vertex into two
obtuse ones. Re-scan reports **0 corners below 90 degrees**; DRC unchanged at
zero.

Note the NFC coil corner: the video exempts printed antennas from this rule,
but a 0.36 mm chamfer changes the loop area by ~0.05 mm2 out of ~60 mm2 —
far below the C12 tuning tolerance — while still removing the acid trap.

Nothing else in this category: no high-current traces are undersized (the
charlieplex lines carry ~10 mA), and there are no analog signal traces
running parallel to fast digital ones.

## 2. Decoupling capacitors ✅ U1 FIXED, rest deferred

The video's rule: each power pin gets a pair — ~10 uF bulk for load
transients plus ~0.1 uF close in for high-frequency noise — and the small
one must sit right at the pin or its effect is largely lost.

Measured distance from each +3V3 cap to the nearest IC power pin:

| Cap | Value | Nearest power pin | Distance | Status |
|---|---|---|---|---|
| C5 | 100 nF | U2.8 (IMU) | **2.1 mm** | good |
| C9 | 22 uF | U3.5 (LDO out) | 3.5 mm | good (bulk) |
| C7 | 1 uF | U3.5 | 4.5 mm | good |
| C10 | 22 uF | U3.5 | 4.9 mm | good (bulk) |
| C1 | 100 nF | U2.12 | 6.2 mm | marginal |
| C11 | 100 nF | U4.8 (NFC) | 7.4 mm | marginal |
| C2 | 100 nF | U2.12 | 11.1 mm | too far |
| C3 | 100 nF | U2.8 | 23.1 mm | too far — rail cap, not decoupling |
| C8 | 10 uF | U1.2 | 21.8 mm | fine as battery-side bulk |

**U1, the ESP32, has no local decoupling at all** — nearest 100 nF is 11 mm
away. Mitigating fact: the WROOM-1 is a module with internal decoupling on
its 3V3 pin, which is why boards like this work in practice. Espressif still
specifies an external 0.1 uF + 10 uF adjacent to pin 2.

**Done — C2 relocated to U1's power pins.** C2 was a leaf component: its
+3V3 pad was a dead-end stub hanging off C1, and its ground ran 18 mm back to
U1 through a bridge added during the ground repairs. Moving it therefore cost
nothing that was carrying other traffic:

- C2 moved from (21.0, 21.5) to (20.5, 35.25), rotated 90 degrees, sitting
  directly beside U1 pins 1 and 2
- The redundant 16 mm ground bridge (6 segments, 4 vias) and the dead +3V3
  stub were deleted — the same connection is now made in 0.8 mm
- New legs: +3V3 1.35 mm to the via feeding pin 2, GND 0.80 mm to the pin-1
  stub. Loop area is now small enough to actually decouple.

**Distance to U1 pin 2: 11.1 mm -> 2.8 mm.** No schematic change was needed:
C2 is still the same 100 nF between +3V3 and GND, only its placement moved.
Verified after: DRC 0 violations, 0 unconnected, every net still a single
connected cluster (GND 42 pads, +3V3 23 pads).

**Still open** (each needs a new part or disturbs verified copper):

- 10 uF bulk companion beside C2 at U1 — needs a new component in the schematic
- 1 uF companion beside C5 so the IMU has a true bulk+HF pair — new component
- Move C11 to within ~2 mm of U4 pin 8
- C3 (23 mm from anything) becomes a deliberate rail cap or moves — its ground
  pad is an endpoint of the battery-cluster bridge, so moving it means
  re-routing verified copper. Decide, then document.

## 3. Length equalisation of high-speed traces — not applicable

The rule targets parallel buses and clock trees where edge timing must be
preserved. This board has one differential pair, USB D+/D-, at **full speed
(12 Mbps)**. The pair is 100.1 mm and 75.9 mm — a 24 mm skew, about 130 ps,
against a 52 ns half-bit period. That is 0.25% of the bit time; irrelevant at
FS, and it would only start to matter at 480 Mbps High-Speed, which the
ESP32-S3's native USB does not do.

No action. Worth recording so a future reviewer does not "fix" it.

## 4. Antenna feed lines ⚠️ needs analysis, not assumption

Two radios here, and the video's rule applies differently to each:

**ESP32 2.4 GHz** — the module carries its own antenna and matching network.
Nothing to impedance-match on our board. What we owe it is the keepout, and
v2.2 already cleared all copper from the antenna zone. Verified clean.

**NFC 13.56 MHz coil** — this is where the board deviates from the video's
advice, and it needs deciding rather than defending:

- Coil traces are 0.2 mm, the same as signal routing. NFC coils normally use
  wider traces to lower resistance and raise Q.
- Ground pour is partially present under the coil region: sampled 71/140
  points on F.Cu and 44/140 on B.Cu. **Ground under an NFC coil couples to
  the field and lowers Q** — most ST25DV reference layouts specify a clear
  keepout under and around the antenna.

A future revision should either widen the coil and add a proper keepout beneath it, or
accept reduced read range as a documented trade. Measure the v2.3 prototype's
actual read range first — if a tap works reliably at 1-2 cm, this may be an
optimisation rather than a defect. Note C12's value (currently 68 pF
placeholder) must be re-tuned after any coil geometry change.

## 5. Component placement — mostly clean

- **Inductors**: none on the board, so no mutual-coupling concern
- **Heat**: no power resistors; the LDO handles at most ~150 mA — negligible
- **Switching regulator**: none, an LDO is used precisely because it is quiet
- **AC mains**: none — battery and USB only

The one placement item worth attention is the decoupling work in section 2,
which the video itself files under this heading.

## 6. Grounds and ground planes ⚠️ known limitation, by design

The video recommends 4 layers with dedicated power and ground planes, and
star-point returns on 2-layer boards.

This is a **2-layer board**, chosen so the artwork reads through and the cost
stays at $2/board. Consequences, honestly stated:

- Ground is a poured plane on both layers, heavily stitched, and after the
  v2.3 work every ground pad is on one connected plane (verified: single
  cluster, 42 pads). That is far better than daisy-chained returns.
- But the plane is perforated by the charlieplex routing, so return paths are
  not ideal, and the earlier corridor study measured that 94% of IMU_INT,
  88% of SDA and 82% of SCL run with no reference copper directly beneath.
- With a quiet LDO, no switcher, no mains, and slow signals, this is
  acceptable. It would not be acceptable on a board with fast edges.

**Option, not obligation:** going 4-layer would fix the reference-plane
gaps outright and cost roughly 3-4x per board. Worth it only if the
prototype shows I2C or USB reliability problems. Cheaper intermediate step:
add ground stitching vias flanking the USB pair and the I2C lines.

---

## Backlog for the next revision

1. ~~Local decoupling at U1 pin 2~~ — **done in v2.3.1**, C2 relocated to
   2.8 mm. A 10 uF bulk companion still wants adding (new component).
2. ~~Fix the five sub-90-degree corners~~ — **done in v2.3.1**, zero remain.
3. IMU bulk companion cap; pull C11 in to U4; resolve C3
4. NFC coil: widen traces + keepout under the coil, retune C12 — pending
   read-range measurement on the v2.3 prototype
5. Optional: ground stitching along USB and I2C, or a 4-layer stack if the
   prototype misbehaves
6. Already carried over from earlier reviews: consider 1206/100 uF for C10

Nothing here blocks building v2.3.1. Every remaining item is an improvement
to make once the physical board has told us which of them actually matter.
