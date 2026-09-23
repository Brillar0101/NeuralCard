# What to send PCBWay

Everything in this folder is generated from the board as it stands, not from an
earlier revision. Regenerate it if the board changes again.

## Files to upload

| File | What it is |
|---|---|
| `NeuralCard_gerbers.zip` | 9 Gerber X2 layers, the drill file, the drill map and the job file |
| `BOM_PCBWay.csv` | 21 lines, 61 placements, manufacturer part numbers with approved alternates |
| `NeuralCard-cpl.csv` | 61 placements, Designator / Mid X / Mid Y / Layer / Rotation |

The loose Gerbers sit alongside the zip for inspection. Upload the zip.

## Board specification

| Setting | Value |
|---|---|
| Size | 85.6 by 54 mm (ID-1, standard business card) |
| Layers | 2 |
| Thickness | 1.6 mm |
| Copper | 1 oz |
| Soldermask | green |
| Silkscreen | white |
| Surface finish | HASL, or ENIG if the budget allows |
| Min track and clearance | 0.15 mm used, 0.1 mm capability assumed |
| Min drill | 0.3 mm |
| Castellation, edge plating | none |

ENIG is worth asking about. It costs more and changes nothing in the Gerbers, but
this board is meant to be handed to people and gold pads look considerably better
than tinned ones on a card. 0.8 mm thickness is the other upgrade worth pricing:
it makes the board feel like a card rather than a circuit board.

## Assembly

Both sides are populated. 24 red LEDs on the front, 37 parts on the back.

| Item | Detail |
|---|---|
| Placements | 66 total, 24 top and 42 bottom |
| Unique parts | 25 |
| Through hole | BT1 coin cell holder, plus the mixed SMD and through hole legs on J2 and SW3 |
| Stencil | yes, needed for the 0.5 mm pitch LGA-14 at U2 |
| Fiducials | four on the bottom, one in each corner |

The cell itself is not on the BOM. Holders ship empty.

BT1 takes a LIR2450, which is rechargeable. Do not fit a primary CR2450 in
this holder. The board charges whatever is in BT1 from USB through U6, and a
primary cell on a live charger output can vent.

There are no fiducials on the top side. If the placement machine wants them for
the LED pass, say so and three 1 mm pads can be added in clear corner space
without touching any routing.

## Two lines to confirm before the order is built

U3 is an ME6211C33M5G-N. No Western distributor carries it, so it has to come
from local stock. If that is a problem, the approved substitute is
AP2112K-3.3TRG1 from Diodes, which has the identical SOT-23-5 pinout and needs no
board change.

U4 is an ST25DV04KC-IE6S3, which is the active part. The older ST25DV04K-IER6S3
is marked not recommended for new designs but is still deeply stocked, and it is
listed as the fallback. Either builds.

Both are called out in the BOM's Remarks column, along with the parts that must
not be substituted at all.

## Verification behind this package

DRC 0 violations and 0 unconnected. ERC 0 violations. Every pin in the schematic
compared against every pad on the board: 211 pads carrying nets, zero net name
disagreements, zero pins without a pad. BOM and placement file cross checked
against each other: 61 designators each, no part in one and missing from the
other.
