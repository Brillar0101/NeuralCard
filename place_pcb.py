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
