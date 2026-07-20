#!/usr/bin/env python3
"""Post-route GND stitching (graph-based).

Model every GND pour fragment (both layers) as a node and every GND via as
an edge between the fragments it lands in. For each connected component
that does not include the main sheet, place a new via at a point inside one
of its fragments where the OTHER layer's main-component copper also exists,
merging the component in. Sub-3mm2 slivers are purged via area-based island
removal. Iterates until fully merged or no candidate spot remains.

Run after SES import, with KiCad's bundled python:
  .../Versions/Current/bin/python3 tools/stitch_islands.py
"""
import os
import pcbnew

H = os.path.expanduser("~/kicad-projects/NeuralCard")
MM = pcbnew.FromMM
MIN_ISLAND_MM2 = 3.0
MARGIN = 0.7          # via clearance to island edge, mm

