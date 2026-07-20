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


def fragments(board, gnd_code):
    """[(layer, sps, outline_idx)] for every filled GND fragment."""
    out = []
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() != gnd_code:
            continue
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(layer):
                continue
            sps = z.GetFilledPolysList(layer)
            for i in range(sps.OutlineCount()):
                out.append((layer, sps, i))
    return out


def components(frags, vias):
    parent = list(range(len(frags)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        parent[find(a)] = find(b)

    for v in vias:
        touched = [k for k, (lay, sps, i) in enumerate(frags)
                   if sps.Contains(v.GetPosition(), i)]
        for a, b in zip(touched, touched[1:]):
            union(a, b)
    groups = {}
    for k in range(len(frags)):
        groups.setdefault(find(k), []).append(k)
    return list(groups.values())


def in_no_via_area(board, px, py):
    pt = pcbnew.VECTOR2I(MM(px), MM(py))
    for z in board.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias():
            if z.Outline().Contains(pt):
                return True
    return False

