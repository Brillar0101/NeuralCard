#!/usr/bin/env python3
"""Add a real, scannable QR (front silkscreen) to the routed board.
Conventional contrast: white silk fills the LIGHT modules + quiet zone, the
DARK modules are left bare (green soldermask) -> dark-on-light. Idempotent.
Run with KiCad bundled python. Silk-only -> does not disturb routing."""
import json
import os
import pcbnew

H = os.path.expanduser("~/kicad-projects/NeuralCard")
BRD = f"{H}/NeuralCard.kicad_pcb"
X0, Y0, MOD, QZ = 3.0, 2.8, 0.34, 2   # origin, module size, quiet-zone modules


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def silk_square(b, cx, cy):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm(X0 + cx * MOD, Y0 + cy * MOD))
    s.SetEnd(mm(X0 + (cx + 1) * MOD, Y0 + (cy + 1) * MOD))
    s.SetLayer(pcbnew.F_SilkS)
    s.SetFilled(True)
    s.SetWidth(pcbnew.FromMM(0.0))
    b.Add(s)


def main():
    b = pcbnew.LoadBoard(BRD)
    # idempotent cleanup: remove "QR" text + any F.SilkS rect in the top-left QR zone
    for d in list(b.GetDrawings()):
        t = d.Type()
        if t == pcbnew.PCB_TEXT_T and d.GetText() == "QR":
            b.Remove(d)
        elif (t == pcbnew.PCB_SHAPE_T and d.GetShape() == pcbnew.SHAPE_T_RECT
              and d.GetLayer() == pcbnew.F_SilkS):
            st = d.GetStart()
            if pcbnew.ToMM(st.x) < 16.0 and pcbnew.ToMM(st.y) < 16.0:
                b.Remove(d)
    m = json.load(open(f"{H}/qr_matrix.json"))
    n = len(m)
    cnt = 0
    for cy in range(-QZ, n + QZ):
        for cx in range(-QZ, n + QZ):
            dark = (0 <= cy < n and 0 <= cx < n and m[cy][cx] == 1)
            if not dark:                    # light module / quiet zone -> white silk
                silk_square(b, cx, cy)
                cnt += 1
    pcbnew.SaveBoard(BRD, b)
    print(f"QR ({n}x{n}) drawn dark-on-light: {cnt} silk cells")


main()
