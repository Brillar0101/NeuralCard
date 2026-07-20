#!/usr/bin/env python3
"""Populate NeuralCard.kicad_pcb from the netlist and place footprints.

Run with KiCad's bundled python (has pcbnew):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 place_pcb.py

Front (F.Cu) = the neural-net art: 24 LEDs as neurons (6 input / 8 hidden / 10 output).
Back  (B.Cu) = ESP32, USB-C, coin, IMU, LDO, P-FET, ESD, buttons, passives.
"""
import os
import re
import pcbnew

H = os.path.expanduser("~/kicad-projects/NeuralCard")
FPD = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
LIB = {"JLC": f"{H}/JLC.pretty",
       "NeuralCard": f"{H}/NeuralCard.pretty",
       "ST25DV": f"{H}/ST25DV.pretty",
       "Resistor_SMD": f"{FPD}/Resistor_SMD.pretty",
       "Capacitor_SMD": f"{FPD}/Capacitor_SMD.pretty"}

# NFC antenna zone (B.Cu coil lives here; rule areas keep everything else out)
NFC_ZONE = (1.9, 15.4, 15.05, 41.1)     # x1, y1, x2, y2 incl. margin; right
                                        # edge leaves the D1-D6 column a corridor
NET = f"{H}/NeuralCard.net"
BRD = f"{H}/NeuralCard.kicad_pcb"


def parse_netlist(path):
    s = open(path).read()
    comps = {}            # ref -> footprint id
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\).*?\(footprint "([^"]+)"\)', s, re.S):
        comps[m.group(1)] = m.group(2)
    nets = {}             # netname -> list of (ref, pad)
    starts = [m.start() for m in re.finditer(r'\(net\s+\(code', s)]
    starts.append(len(s))
    for a, b in zip(starts, starts[1:]):
        chunk = s[a:b]
        nm = re.search(r'\(name "([^"]*)"', chunk)
        name = nm.group(1) if nm else ""
        nodes = re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', chunk)
        if name and nodes:
            nets[name] = nodes
    return comps, nets


def mm(v):
    return pcbnew.VECTOR2I(pcbnew.FromMM(v[0]), pcbnew.FromMM(v[1]))


def linspace(a, b, n):
    return [round(a + (b - a) * i / (n - 1), 3) for i in range(n)]


# ---- Front neural-net art: LED neuron positions (x, y) mm on the card ----
IN_X, HID_X, OUT_X = 17.0, 42.8, 68.6
layout = {}             # ref -> (x, y, deg, back?)
for k, y in enumerate(linspace(11, 43, 6)):     # input layer = D1..D6
    layout[f"D{k+1}"] = (IN_X, y, 0, False)
for k, y in enumerate(linspace(7, 47, 8)):      # hidden layer = D7..D14
    layout[f"D{k+7}"] = (HID_X, y, 0, False)
for k, y in enumerate(linspace(5, 49, 10)):     # output layer = D15..D24
    layout[f"D{k+15}"] = (OUT_X, y, 0, False)

# ---- Back side: major parts (x, y, deg) ----
back_major = {
    "U1": (32.0, 27.0, 0),     # ESP32-S3 module (center-left back)
    "U2": (21.5, 9.5, 0),      # IMU (rigid-body sensor: position-agnostic;
                               # parked above the ESP32, out of the NFC corner)
    "BT1": (62.0, 28.0, 0),    # coin holder
    "J1": (66.0, 50.0, 0),     # UART programming pads (bottom edge)
    "SW1": (12.0, 47.3, 0),    # BOOT (clear of the ESP32 module edge, y>44.5)
    "SW2": (24.0, 47.3, 0),    # RESET
    "U4": (6.2, 9.6, 0),       # ST25DV04KC NFC tag, top-left beside the IMU
    "C12": (10.9, 13.4, 0),    # antenna tuning cap, next to the coil feed
    "C11": (10.8, 8.0, 90),    # NFC VCC decoupling
    "R14": (62.0, 52.3, 0),    # NFC GPO pull-up
}
layout["ANT1"] = (0.0, 0.0, 0, False)   # coil footprint bakes absolute coords
for ref, (x, y, d) in back_major.items():
    layout[ref] = (x, y, d, True)

# ---- Back side: passives auto-placed in top/bottom edge rows ----
passives = ([f"R{n}" for n in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12]]
            + [f"C{n}" for n in [1, 2, 3, 4, 5, 8, 9, 10]])
slots = []
for x in linspace(8, 80, 12):
    slots.append((x, 4.5))     # top edge row
for x in linspace(8, 58, 6):
    slots.append((x, 51.5))    # bottom edge row (left of prog pads)
for ref, (x, y) in zip(passives, slots):
    layout[ref] = (x, y, 0, True)


def main():
    import shutil
    comps, nets = parse_netlist(NET)
    shutil.copyfile(f"{H}/board_outline.kicad_pcb", BRD)   # always start from pristine outline
    board = pcbnew.LoadBoard(BRD)

    placed = {}
    for ref, fpid in comps.items():
        lib, name = fpid.split(":")
        fp = pcbnew.FootprintLoad(LIB[lib], name)
        if fp is None:
            print("MISSING FP:", fpid); continue
        fp.SetReference(ref)
        x, y, deg, back = layout.get(ref, (42.8, 27.0, 0, True))
        board.Add(fp)
        fp.SetPosition(mm((x, y)))
        if back:
            fp.SetLayerAndFlip(pcbnew.B_Cu)
        fp.SetOrientationDegrees(deg)
        if not back or ref in ("SW1", "SW2"):
            fp.Reference().SetVisible(False)   # front silk is art; SW get role labels
        placed[ref] = fp

    # nets
    made = 0
    for name, nodes in nets.items():
        if not name:
            continue
        ni = board.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
        for ref, padnum in nodes:
            fp = placed.get(ref)
            if not fp:
                continue
            for pad in fp.Pads():
                if pad.GetNumber() == padnum:
                    pad.SetNet(ni)
        made += 1

    add_silk(board)
    add_stitching(board)
    add_nfc_keepouts(board)
    add_rule_strip(board)
    add_pours(board)

    board.BuildListOfNets()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(BRD, board)
    print(f"placed {len(placed)} footprints, {made} nets assigned, "
          f"{board.Zones().GetCount() if hasattr(board.Zones(),'GetCount') else len(list(board.Zones()))} zones")


# ---------------------------------------------------------------- silkscreen art
def seg(board, x1, y1, x2, y2, layer, w):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm((x1, y1)))
    s.SetEnd(mm((x2, y2)))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(w))
    board.Add(s)


def rect(board, x1, y1, x2, y2, layer, w):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm((x1, y1)))
    s.SetEnd(mm((x2, y2)))
    s.SetLayer(layer)
    s.SetWidth(pcbnew.FromMM(w))
    board.Add(s)


def text(board, t, x, y, size, layer, thick, justify=None, angle=0, mirror=False):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(t)
    tx.SetPosition(mm((x, y)))
    tx.SetLayer(layer)
    tx.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    tx.SetTextThickness(pcbnew.FromMM(thick))
    if justify == "left":
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    elif justify == "right":
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    if angle:
        tx.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    if mirror:
        tx.SetMirrored(True)
    board.Add(tx)


def _track(board, p1, p2, layer, net, tw):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(p1)
    t.SetEnd(p2)
    t.SetWidth(tw)
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)


def _via(board, pos, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pos)
    v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3))
    v.SetNet(net)
    board.Add(v)


def add_routes(board):
    """Greedy MST router for non-GND nets (GND handled by pour)."""
    from collections import defaultdict
    tw = pcbnew.FromMM(0.2)
    netpads = defaultdict(list)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            n = pad.GetNetname()
            if n and n != "GND" and pad.GetNumber():
                netpads[n].append(pad)
    for name, pads in netpads.items():
        if len(pads) < 2:
            continue
        net = board.FindNet(name)
        placed = [pads[0]]
        rest = list(pads[1:])
        while rest:
            best = None
            for a in placed:
                pa = a.GetPosition()
                for b in rest:
                    pb = b.GetPosition()
                    d = (pa.x - pb.x) ** 2 + (pa.y - pb.y) ** 2
                    if best is None or d < best[0]:
                        best = (d, a, b)
            _, a, b = best
            la = pcbnew.F_Cu if a.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            lb = pcbnew.F_Cu if b.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            pa, pb = a.GetPosition(), b.GetPosition()
            _track(board, pa, pb, la, net, tw)
            if la != lb:
                _via(board, pb, net)
            placed.append(b)
            rest.remove(b)

