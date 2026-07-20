#!/usr/bin/env python3
"""Set the silkscreen typography to the site's PatternFly faces
(Red Hat Display / Text / Mono) by patching (face "...") into each text
item's font block in NeuralCard.kicad_pcb. Outline fonts plot to gerbers
as filled polygons; SemiBold keeps small strokes above JLCPCB's 0.15mm
silk minimum. Run after place/route, before fab export.
"""
import re
import os

H = os.path.expanduser("~/kicad-projects/NeuralCard")
BRD = f"{H}/NeuralCard.kicad_pcb"

# text content -> (font face, bold)
FONTS = {
    "BARAKAELI LAWUO": ("Red Hat Display", True),
    "AI & COMPUTER ENGINEER": ("Red Hat Text SemiBold", False),
    "VIRGINIA TECH ENGINEERING · CLASS OF 2027": ("Red Hat Text SemiBold", False),
    "AIR-WRITE A DIGIT · THE BRIGHTEST NEURON ANSWERS": ("Red Hat Text SemiBold", False),
    "NFC": ("Red Hat Display SemiBold", False),
    "tap phone here": ("Red Hat Mono SemiBold", False),
    "princetekki.com": ("Red Hat Mono SemiBold", False),
    "NEURALCARD v2.1 · 2026": ("Red Hat Mono SemiBold", False),
    "CR2032 · + side out": ("Red Hat Mono SemiBold", False),
    "NeuralCard v2.1 · princetekki.com": ("Red Hat Mono SemiBold", False),
    "FLASH: hold BOOT · tap RST · release BOOT": ("Red Hat Mono SemiBold", False),
    "BOOT": ("Red Hat Mono SemiBold", False),
    "RST": ("Red Hat Mono SemiBold", False),
    "OSHW · github.com/Brillar0101": ("Red Hat Mono SemiBold", False),
    "S/N": ("Red Hat Mono SemiBold", False),
}
for ch in "0123456789":
    FONTS[ch] = ("Red Hat Mono SemiBold", False)
for lab in ("ax", "ay", "az", "gx", "gy", "gz"):
    FONTS[lab] = ("Red Hat Mono SemiBold", False)

s = open(BRD).read()
s = s.replace("NeuralCard v2.1 · barakaeli.dev", "NeuralCard v2.1 · princetekki.com")

count = 0