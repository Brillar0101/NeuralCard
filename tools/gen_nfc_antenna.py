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