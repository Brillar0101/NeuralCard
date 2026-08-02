#!/usr/bin/env python3
"""Hand-route the one connection Freerouting leaves (CC2: J1-B5 -> R8) through
the empty front-layer corridor along the right board edge. Run with KiCad python."""
import os
import pcbnew

H = os.path.expanduser("~/kicad-projects/NeuralCard")
BRD = f"{H}/NeuralCard.kicad_pcb"


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def main():
    b = pcbnew.LoadBoard(BRD)
    net = b.FindNet("CC2")
    tw = pcbnew.FromMM(0.2)

    def trk(x1, y1, x2, y2, layer):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(mm(x1, y1)); t.SetEnd(mm(x2, y2))
        t.SetWidth(tw); t.SetLayer(layer); t.SetNet(net); b.Add(t)

    def via(x, y):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(mm(x, y)); v.SetWidth(pcbnew.FromMM(0.6)); v.SetDrill(pcbnew.FromMM(0.3))
        v.SetNet(net); b.Add(v)

    # B.Cu stub from B5 pad, via up to F.Cu, down the right edge corridor, via back to R8
    trk(82.47, 25.25, 83.4, 25.25, pcbnew.B_Cu)
    via(83.4, 25.25)
    trk(83.4, 25.25, 84.4, 25.25, pcbnew.F_Cu)
    trk(84.4, 25.25, 84.4, 42.83, pcbnew.F_Cu)
    trk(84.4, 42.83, 81.0, 42.83, pcbnew.F_Cu)
    via(81.0, 42.83)
    trk(81.0, 42.83, 80.0, 42.83, pcbnew.B_Cu)

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(BRD, b)
    print("CC2 routed via front corridor")


main()
