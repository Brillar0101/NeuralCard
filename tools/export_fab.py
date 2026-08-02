#!/usr/bin/env python3
"""Regenerate the JLCPCB fab package in fab/ from NeuralCard.kicad_pcb.

The README documents these steps as raw kicad-cli invocations; this collects
them so a fab refresh is one reproducible command instead of five remembered
ones. Gerbers, drill (with map), and the pick-and-place export all come from
kicad-cli. The CPL is a straight rename of kicad-cli's position export into the
column names JLCPCB expects -- kicad-cli already emits Y negated, so the
coordinates pass through untouched.

The BOM (fab/NeuralCard-bom.csv) is hand-maintained and is not written here; it
is only copied into the zip.

    python3 tools/export_fab.py
"""
import csv
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = os.path.join(ROOT, "NeuralCard.kicad_pcb")
FAB = os.path.join(ROOT, "fab")
NAME = "NeuralCard"

LAYERS = ("F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,"
          "F.Silkscreen,B.Silkscreen,Edge.Cuts")

# The zip is the gerber/drill package only. JLCPCB takes the BOM and CPL as
# separate uploads, so they stay loose in fab/ rather than going in here.
ZIP_MEMBERS = [
    f"{NAME}-F_Cu.gtl", f"{NAME}-B_Cu.gbl",
    f"{NAME}-F_Mask.gts", f"{NAME}-B_Mask.gbs",
    f"{NAME}-F_Paste.gtp", f"{NAME}-B_Paste.gbp",
    f"{NAME}-F_Silkscreen.gto", f"{NAME}-B_Silkscreen.gbo",
    f"{NAME}-Edge_Cuts.gm1", f"{NAME}-job.gbrjob",
    f"{NAME}.drl", f"{NAME}-drl_map.gbr",
]


def run(*args):
    print("  $", " ".join(args[:3]), "...")
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        sys.exit("failed: %s" % " ".join(args))


def main():
    os.makedirs(FAB, exist_ok=True)

    print("gerbers")
    # Protel extensions (.gtl/.gbl/...) on purpose: that is the naming the fab
    # package already uses, and dropping them writes a parallel .gbr set
    # instead of refreshing these files in place.
    run("kicad-cli", "pcb", "export", "gerbers",
        "--layers", LAYERS, "-o", FAB + os.sep, BOARD)

    print("drill + map")
    run("kicad-cli", "pcb", "export", "drill",
        "--format", "excellon", "--drill-origin", "absolute",
        "--excellon-units", "mm", "--generate-map", "--map-format", "gerberx2",
        "-o", FAB + os.sep, BOARD)

    print("position -> cpl")
    raw = os.path.join(FAB, f"{NAME}-pos-raw.csv")
    run("kicad-cli", "pcb", "export", "pos",
        "--format", "csv", "--units", "mm", "--side", "both",
        "-o", raw, BOARD)

    cpl = os.path.join(FAB, f"{NAME}-cpl.csv")
    with open(raw, newline="") as fh_in, open(cpl, "w", newline="") as fh_out:
        reader = csv.DictReader(fh_in)
        writer = csv.writer(fh_out)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        rows = 0
        for row in reader:
            writer.writerow([
                row["Ref"],
                "%.4f" % float(row["PosX"]),
                "%.4f" % float(row["PosY"]),
                row["Side"].capitalize(),
                "%.4f" % float(row["Rot"]),
            ])
            rows += 1
    print("  %d placements" % rows)

    print("zip")
    bundle = os.path.join(FAB, f"{NAME}_JLCPCB.zip")
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
        for member in ZIP_MEMBERS:
            path = os.path.join(FAB, member)
            if not os.path.exists(path):
                sys.exit("missing expected fab output: %s" % member)
            zf.write(path, member)
    print("  wrote %s" % os.path.relpath(bundle, ROOT))


if __name__ == "__main__":
    main()
