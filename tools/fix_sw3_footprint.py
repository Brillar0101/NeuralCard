#!/usr/bin/env python3
"""Replace the hand-drawn SW3 land pattern with the official MSK12C02 footprint.

SW3 (power slide switch, coin cell in series with the +3V3 rail) was added by
hand in commit b2ccb56 with an improvised 3-pad land: 1.3 mm pitch, no mounting
tabs, no locating holes, and a placeholder 3D model (a Copal DIP switch scaled
to 0.62). JLCPCB selected C431540 (SHOU HAN MSK12C02) at order time and their
DFM check rejected it -- the real part is 8 x 2.8 mm, needs four shield tabs and
two 0.85 mm NPTH locating holes, none of which the land provided.

This swaps in Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02, the KiCad library
footprint drawn from the manufacturer datasheet, and re-routes the two stubs.

Orientation: the part is right-angle (side actuated), so it is rotated 270 deg
with the pins facing inboard toward BT1 and the actuator facing the right card
edge, where a thumb can reach it. Position is nudged 0.546 mm inboard to leave
1.0 mm from the courtyard to the board edge for assembly.

Net mapping is preserved exactly as the schematic defines it:
    pad 1 -> unconnected (open throw)
    pad 2 -> VBAT   (common pole, from BT1 pad 1)
    pad 3 -> +3V3   (closed throw)

The four SH tabs are left netless on purpose. They are the switch's metal
retention frame; the datasheet does not state that the frame is isolated from
the contacts, and tying them to GND would short the coin cell if it is not.
They still solder down and provide full mechanical retention.

Run with the Python bundled inside KiCad (it needs pcbnew):
    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        tools/fix_sw3_footprint.py
"""
import os
import sys

import wx  # noqa: F401  -- pcbnew needs a wxApp before it will load headless

_app = wx.App()

import pcbnew  # noqa: E402

BOARD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "NeuralCard.kicad_pcb")
LIB = os.environ.get(
    "KICAD_FOOTPRINT_DIR",
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
) + "/Button_Switch_SMD.pretty"
FP_NAME = "SW_SPDT_Shouhan_MSK12C02"

# Board right edge, and the clearance we want from the courtyard to it.
EDGE_RIGHT = 146.2562
EDGE_GAP = 1.0

CENTRE_Y = 64.4434
ROTATION = 270.0


def mm(value):
    return value / 1e6


def to_iu(value):
    return int(round(value * 1e6))


def pt(x, y):
    return pcbnew.VECTOR2I(to_iu(x), to_iu(y))


def main():
    board = pcbnew.LoadBoard(BOARD)

    old = board.FindFootprintByReference("SW3")
    if old is None:
        sys.exit("SW3 not found on the board")

    # Track width and net objects come from the existing design so the new
    # routing matches what is already there.
    vbat = board.FindNet("VBAT")
    v3v3 = board.FindNet("+3V3")
    if vbat is None or v3v3 is None:
        sys.exit("VBAT / +3V3 nets missing")

    # GetTracks() also yields vias, whose GetWidth() needs a layer argument.
    segments = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
    widths = [t.GetWidth() for t in segments
              if t.GetNetname() in ("VBAT", "+3V3")]
    width = max(set(widths), key=widths.count)
    print("matching existing power track width %.3f mm" % mm(width))

    # Drop the old hand-drawn part and its two stubs. Everything else on +3V3
    # stays put; the stub we remove only ever fed the old pad 3.
    old_pos = old.GetPosition()
    board.Remove(old)

    doomed = []
    for t in segments:
        if t.GetLayer() != pcbnew.B_Cu:
            continue
        a, b = (mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))
        net = t.GetNetname()
        if net == "VBAT" and max(a[0], b[0]) > 138.0:
            doomed.append(t)
        elif net == "+3V3" and abs(a[0] - 141.3562) < 0.01 and abs(b[0] - 141.3562) < 0.01:
            doomed.append(t)
    for t in doomed:
        board.Remove(t)
    print("removed old footprint and %d stub segments" % len(doomed))

    # Place the real part.
    fp = pcbnew.FootprintLoad(LIB, FP_NAME)
    if fp is None:
        sys.exit("could not load %s from %s" % (FP_NAME, LIB))
    board.Add(fp)
    fp.SetReference("SW3")
    fp.SetValue("MSK12C02")
    fp.SetPosition(old_pos)
    fp.Flip(fp.GetPosition(), False)   # onto B.Cu, same side as before
    fp.SetOrientationDegrees(ROTATION)

    # Nudge inboard so the courtyard clears the card edge by EDGE_GAP.
    crtyd = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
    centre_x = mm(old_pos.x) - (mm(crtyd.GetRight()) - (EDGE_RIGHT - EDGE_GAP))
    fp.SetPosition(pt(centre_x, CENTRE_Y))
    print("placed at (%.4f, %.4f) rot %.0f on %s"
          % (centre_x, CENTRE_Y, ROTATION, board.GetLayerName(fp.GetLayer())))

    pads = {p.GetNumber(): p for p in fp.Pads()}
    pads["2"].SetNet(vbat)
    pads["3"].SetNet(v3v3)

    def pad_xy(num):
        p = pads[num].GetPosition()
        return mm(p.x), mm(p.y)

    p2x, p2y = pad_xy("2")
    p3x, p3y = pad_xy("3")

    # VBAT: straight out of the common pole into the BT1 coin-holder pad, which
    # is a through-hole pad so it is reachable from the back copper.
    # +3V3: out of the closed throw, clear of the body, up to the existing
    # +3V3 track that runs vertically at x = 140.41.
    routes = [
        (vbat, [(p2x, p2y), (138.0, p2y)]),
        (v3v3, [(p3x, p3y), (139.5, p3y + 0.75), (139.5, 70.01), (140.41, 70.01)]),
    ]
    added = 0
    for net, points in routes:
        for start, end in zip(points, points[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pt(*start))
            t.SetEnd(pt(*end))
            t.SetWidth(width)
            t.SetLayer(pcbnew.B_Cu)
            t.SetNet(net)
            board.Add(t)
            added += 1
    print("routed %d new segments" % added)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    print("refilled %d zones" % len(list(board.Zones())))

    board.BuildListOfNets()
    pcbnew.SaveBoard(BOARD, board)
    print("saved %s" % BOARD)


if __name__ == "__main__":
    main()
