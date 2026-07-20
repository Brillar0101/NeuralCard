#!/usr/bin/env python3
"""Generate NeuralCard.pretty/NFC_Antenna_13x24.kicad_mod.

10-turn rectangular spiral NFC coil for the ST25DV04KC (28.5 pF internal
tuning cap + external C12 47 pF -> ~13.6 MHz with the coil's ~1.7 uH).

Geometry is in ABSOLUTE board coordinates; the footprint is placed at (0,0)
angle 0, unflipped. Copper lives on B.Cu; the inner-terminal escape crosses
the turns on F.Cu between two small through-hole pads (a footprint may not
contain vias, but TH pads serve the same purpose and stay inside the
net-tie group, which is what lets one conductor legally bridge the
NFC_ANT_A and NFC_ANT_B nets).

Pads: 1 = outer terminal (SMD, B.Cu)   2 = inner terminal brought outside (TH)
      3 = inner crossover (TH)
"""
TRACK = 0.3      # mm copper width
PITCH = 0.6      # mm turn-to-turn (0.3 track + 0.3 gap)
TURNS = 9
# outer centerline rectangle (zone x[2.5,14.5] y[16,40.5] minus track/2);
# right edge stops at 14.5 so the input-LED column keeps a routing corridor.
# Feed exits the TOP edge: U4 lives beside the IMU at the board's top-left.
XL0, XR0 = 2.65, 14.35
YT0, YB0 = 16.15, 40.35
ENTRY_X = 3.2            # where pad-1 stub meets the outer turn
PAD1 = (3.2, 14.2)       # outer terminal, above the coil, below U4
PAD2 = (8.0, 14.2)       # inner terminal escape landing, outside the coil
PAD3 = (8.5, 22.8)       # crossover TH pad inside the coil cavity
PAD_R = 0.6              # TH pad radius (1.2 dia, 0.3 drill — JLCPCB minimum)

lines = []                # (x1,y1,x2,y2,layer,width)


def seg(a, b, layer="B.Cu", w=TRACK):
    lines.append((a[0], a[1], b[0], b[1], layer, w))


def spiral():
    """Inward rectangular spiral entered from the TOP edge."""
    pts = [(ENTRY_X, YT0)]
    for k in range(TURNS):
        xl, xr = XL0 + k * PITCH, XR0 - k * PITCH
        yb = YB0 - k * PITCH
        yt_next = YT0 + (k + 1) * PITCH
        cur = pts[-1]
        pts += [(xl, cur[1]), (xl, yb), (xr, yb), (xr, yt_next)]
        if k < TURNS - 1:
            pts.append((XL0 + (k + 1) * PITCH, yt_next))
    return pts


pts = spiral()
for a, b in zip(pts, pts[1:]):
    seg(a, b)
def edge_stop(frm, pad):
    """Endpoint on the TH pad's annulus edge (stops copper short of the
    hole so hole-clearance passes; touching the annulus still connects)."""
    dx, dy = pad[0] - frm[0], pad[1] - frm[1]
    d = (dx * dx + dy * dy) ** 0.5
    return (round(pad[0] - dx / d * PAD_R, 3), round(pad[1] - dy / d * PAD_R, 3))


seg(PAD1, (ENTRY_X, YT0))                          # pad1 stub into outer turn
seg(pts[-1], edge_stop(pts[-1], PAD3))             # spiral inner end -> crossover
seg((PAD3[0], PAD3[1] - PAD_R), (PAD2[0], PAD2[1] + PAD_R),
    layer="F.Cu")                                  # front escape across top turns

