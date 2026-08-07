#!/usr/bin/env python3
"""Generate NeuralCard.kicad_sch section by section.

NeuralCard — AI business card (air-writing digit recognition, ESP32-S3).
Coordinates: sheet mm, 1.27 grid, y DOWN. Paper A3.
Symbol placements use angle 0, no mirror, so a pin at symbol-local (lx, ly)
maps to sheet (px + lx, py - ly).
"""
import re
import uuid

ROOT_UUID = "a1b2c3d4-0001-4000-8000-000000000001"
PROJECT = "NeuralCard"

# ---------------------------------------------------------------- symbol libs
KSYM = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
DEVICE_LIB = f"{KSYM}/Device.kicad_sym"
POWER_LIB = f"{KSYM}/power.kicad_sym"
JLC_LIB = "JLC.kicad_sym"
ST25DV_LIB = "ST25DV.kicad_sym"

# lib_id -> (source file, symbol name in that file)
LIBSYMS = {
    "Device:R": (DEVICE_LIB, "R"),
    "Device:C": (DEVICE_LIB, "C"),
    "Device:LED": (DEVICE_LIB, "LED"),
    "Connector_Generic:Conn_01x06": (f"{KSYM}/Connector_Generic.kicad_sym", "Conn_01x06"),
    "Connector_Generic:Conn_01x02": (f"{KSYM}/Connector_Generic.kicad_sym", "Conn_01x02"),
    "Switch:SW_SPDT": (f"{KSYM}/Switch.kicad_sym", "SW_SPDT"),
    "power:GND": (POWER_LIB, "GND"),
    "power:+3V3": (POWER_LIB, "+3V3"),
    "power:VBUS": (POWER_LIB, "VBUS"),
    "JLC:ME6211C33M5G-N": (JLC_LIB, "ME6211C33M5G-N"),
    "JLC:CR2032-BS-6-1": (JLC_LIB, "CR2032-BS-6-1"),
    "JLC:AO3401A": (JLC_LIB, "AO3401A"),
    "JLC:ESP32-S3-WROOM-1": (JLC_LIB, "ESP32-S3-WROOM-1"),
    "JLC:TYPE-C-31-M-12": (JLC_LIB, "TYPE-C-31-M-12"),
    "JLC:USBLC6-2SC6": (JLC_LIB, "USBLC6-2SC6"),
    "JLC:TS-1187A-B-A-B": (JLC_LIB, "TS-1187A-B-A-B"),
    "JLC:LSM6DS3TR-C": (JLC_LIB, "LSM6DS3TR-C"),
    "ST25DV:ST25DV04KC-IE6S3": (ST25DV_LIB, "ST25DV04KC-IE6S3"),
}

# pin local coords (lx, ly) per lib_id
PIN_XY = {
    "Device:R": {"1": (0, 3.81), "2": (0, -3.81)},
    "Device:C": {"1": (0, 3.81), "2": (0, -3.81)},
    "Device:LED": {"1": (-3.81, 0), "2": (3.81, 0)},
    "Connector_Generic:Conn_01x06": {"1": (-5.08, 5.08), "2": (-5.08, 2.54), "3": (-5.08, 0.0),
                                      "4": (-5.08, -2.54), "5": (-5.08, -5.08), "6": (-5.08, -7.62)},
    "Connector_Generic:Conn_01x02": {"1": (-5.08, 0.0), "2": (-5.08, -2.54)},
    "JLC:ME6211C33M5G-N": {"1": (-12.70, 2.54), "2": (-12.70, 0.0),
                            "3": (-12.70, -2.54), "4": (12.70, -2.54), "5": (12.70, 2.54)},
    "JLC:CR2032-BS-6-1": {"1": (-5.08, 0.0), "2": (5.08, 0.0)},
    # MSK12C02 pinout matches KiCad's generic SPDT: pin 2 is the common pole,
    # pins 1 and 3 are the throws. Do not renumber -- pad 2 carries VBAT on the board.
    "Switch:SW_SPDT": {"1": (5.08, 2.54), "2": (-5.08, 0.0), "3": (5.08, -2.54)},
    "JLC:AO3401A": {"1": (-5.08, 0.0), "2": (2.54, -5.08), "3": (2.54, 5.08)},
    "JLC:TS-1187A-B-A-B": {"1": (-5.08, 2.54), "2": (5.08, 2.54), "3": (-5.08, -5.08), "4": (5.08, -5.08)},
    "JLC:USBLC6-2SC6": {"1": (-16.51, 7.62), "2": (-16.51, 0.0), "3": (-16.51, -7.62),
                         "4": (16.51, -7.62), "5": (16.51, 0.0), "6": (16.51, 7.62)},
    "JLC:TYPE-C-31-M-12": {
        "A1B12": (-6.35, 13.97), "A4B9": (-6.35, 11.43), "B8": (-6.35, 8.89), "A5": (-6.35, 6.35),
        "B7": (-6.35, 3.81), "A6": (-6.35, 1.27), "A7": (-6.35, -1.27), "B6": (-6.35, -3.81),
        "A8": (-6.35, -6.35), "B5": (-6.35, -8.89), "B4A9": (-6.35, -11.43), "B1A12": (-6.35, -13.97),
        "1": (11.43, -13.97), "2": (11.43, -11.43), "3": (11.43, -8.89), "4": (11.43, -6.35)},
    "JLC:ESP32-S3-WROOM-1": {
        "1": (-21.59, 10.16), "2": (-21.59, 7.62), "3": (-21.59, 5.08), "4": (-21.59, 2.54),
        "5": (-21.59, 0.0), "6": (-21.59, -2.54), "7": (-21.59, -5.08), "8": (-21.59, -7.62),
        "9": (-21.59, -10.16), "10": (-21.59, -12.70), "11": (-21.59, -15.24), "12": (-21.59, -17.78),
        "13": (-21.59, -20.32), "14": (-21.59, -22.86),
        "15": (-13.97, -35.56), "16": (-11.43, -35.56), "17": (-8.89, -35.56), "18": (-6.35, -35.56),
        "19": (-3.81, -35.56), "20": (-1.27, -35.56), "21": (1.27, -35.56), "22": (3.81, -35.56),
        "23": (6.35, -35.56), "24": (8.89, -35.56), "25": (11.43, -35.56), "26": (13.97, -35.56),
        "27": (21.59, -22.86), "28": (21.59, -20.32), "29": (21.59, -17.78), "30": (21.59, -15.24),
        "31": (21.59, -12.70), "32": (21.59, -10.16), "33": (21.59, -7.62), "34": (21.59, -5.08),
        "35": (21.59, -2.54), "36": (21.59, 0.0), "37": (21.59, 2.54), "38": (21.59, 5.08),
        "39": (21.59, 7.62), "40": (21.59, 10.16), "41": (21.59, 15.24)},
    "JLC:LSM6DS3TR-C": {
        "1": (-13.97, 7.62), "2": (-13.97, 5.08), "3": (-13.97, 2.54), "4": (-13.97, 0.0),
        "5": (-13.97, -2.54), "6": (-13.97, -5.08), "7": (-13.97, -7.62),
        "8": (13.97, -7.62), "9": (13.97, -5.08), "10": (13.97, -2.54), "11": (13.97, 0.0),
        "12": (13.97, 2.54), "13": (13.97, 5.08), "14": (13.97, 7.62)},
    "ST25DV:ST25DV04KC-IE6S3": {
        "1": (-10.16, 3.81), "2": (-10.16, 1.27), "3": (-10.16, -1.27), "4": (-10.16, -3.81),
        "5": (10.16, -3.81), "6": (10.16, -1.27), "7": (10.16, 1.27), "8": (10.16, 3.81)},
}

# ref -> footprint (lib:fp)
FP = {
    "U3": "JLC:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BL",
    "Q1": "JLC:SOT-23_L2.9-W1.3-P1.90-LS2.4-BR",
    "BT1": "JLC:BAT-TH_CR2032-BS-6-1",
    "R13": "Resistor_SMD:R_0603_1608Metric",
    "C6": "Capacitor_SMD:C_0603_1608Metric",
    "C7": "Capacitor_SMD:C_0603_1608Metric",
    "C8": "Capacitor_SMD:C_0805_2012Metric",
    "C9": "Capacitor_SMD:C_0805_2012Metric",
    "C10": "Capacitor_SMD:C_0805_2012Metric",
    "U1": "JLC:WIRELM-SMD_ESP32-S3-WROOM-1",
    "J1": "NeuralCard:ProgPads_1x6",
    "D0": "JLC:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL",
    "SW1": "JLC:SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL_H1.5",
    "SW2": "JLC:SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL_H1.5",
    "SW3": "Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02",
    "R7": "Resistor_SMD:R_0603_1608Metric",
    "R8": "Resistor_SMD:R_0603_1608Metric",
    "R9": "Resistor_SMD:R_0603_1608Metric",
    "R10": "Resistor_SMD:R_0603_1608Metric",
    "C1": "Capacitor_SMD:C_0603_1608Metric",
    "C2": "Capacitor_SMD:C_0603_1608Metric",
    "C3": "Capacitor_SMD:C_0603_1608Metric",
    "C4": "Capacitor_SMD:C_0603_1608Metric",
    "U2": "JLC:LGA-14_L3.0-W2.5-P0.50-TL",
    "J2": "JLC:USB-C_SMD-TYPE-C-31-M-12_1",
    "U5": "JLC:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL",
    "R11": "Resistor_SMD:R_0603_1608Metric",
    "R12": "Resistor_SMD:R_0603_1608Metric",
    "C5": "Capacitor_SMD:C_0603_1608Metric",
    "U4": "ST25DV:SO-8_L4.9-W3.9-P1.27-LS5.9-BL",
    "C11": "Capacitor_SMD:C_0603_1608Metric",
    "C12": "Capacitor_SMD:C_0603_1608Metric",
    "R14": "Resistor_SMD:R_0603_1608Metric",
    "ANT1": "NeuralCard:NFC_Antenna_13x24",
}
# Charlieplex resistors R1-R6 (0603) and neuron LEDs D1-D24 (blue 0603)
for _n in range(1, 7):
    FP[f"R{_n}"] = "Resistor_SMD:R_0603_1608Metric"
for _n in range(1, 25):
    FP[f"D{_n}"] = "JLC:LED-SMD_L1.6-W0.8-R-RD"   # red 0603 (KT-0603R / C2286)


# ------------------------------------------------------------------ BOM identity
# Part numbers live in the schematic, not only in BOM_JLCPCB.csv. Without these,
# nothing downstream can cross-reference a component: sourcing audits report the
# board as not pre-fab ready, lifecycle checks have nothing to look up, and
# thermal analysis skips entirely for want of datasheet keys. This is also how
# SW3 drifted to "select-at-order" until a fab rejected it.
#
# MPNs verified against the LCSC/jlcsearch API on 2026-08-02 (USB-power parts
# re-verified 2026-08-06). Manufacturer names come from the LCSC catalogue --
# the API does not expose that field.
LCSC_PARTS = {
    "C14663":   ("CC0603KRX7R9BB104", "YAGEO"),
    "C15850":   ("CL21A106KAYNNNE", "Samsung Electro-Mechanics"),
    "C45783":   ("CL21A226MAQNNNE", "Samsung Electro-Mechanics"),
    "C22962":   ("0603WAF2200T5E", "UNI-ROYAL"),
    "C25804":   ("0603WAF1002T5E", "UNI-ROYAL"),
    "C23162":   ("0603WAF4701T5E", "UNI-ROYAL"),
    "C25803":   ("0603WAF1003T5E", "UNI-ROYAL"),
    "C2286":    ("KT-0603R", "Hubei KENTO Elec"),
    "C318884":  ("TS-1187A-B-A-B", "XKB Connection"),
    "C431540":  ("MSK12C02", "SHOU HAN"),
    "C2913204": ("ESP32-S3-WROOM-1-N8R2", "Espressif Systems"),
    "C967633":  ("LSM6DS3TR-C", "STMicroelectronics"),
    "C3304276": ("ST25DV04KC-IE6S3", "STMicroelectronics"),
    "C70377":   ("CR2032-BS-6-1", "Q&J"),
    "C165948":  ("TYPE-C-31-M-12", "Korean Hroparts Elec"),
    "C7519":    ("USBLC6-2SC6", "STMicroelectronics"),
    "C82942":   ("ME6211C33M5G-N", "Nanjing Micro One Elec"),
    "C15127":   ("AO3401A", "Alpha & Omega Semicon"),
    "C23186":   ("0603WAF5101T5E", "UNI-ROYAL"),
    "C15849":   ("CL10A105KB8NNNC", "Samsung Electro-Mechanics"),
}

REF_LCSC = {}
for _code, _refs in [
    ("C14663",   ["C1", "C2", "C3", "C4", "C5", "C11"]),
    ("C15850",   ["C8"]),
    ("C45783",   ["C9", "C10"]),
    ("C22962",   [f"R{n}" for n in range(1, 7)]),
    ("C25804",   ["R9", "R10"]),
    ("C23162",   ["R11", "R12"]),
    ("C25803",   ["R13", "R14"]),
    ("C2286",    [f"D{n}" for n in range(1, 25)]),
    ("C318884",  ["SW1", "SW2"]),
    ("C431540",  ["SW3"]),
    ("C2913204", ["U1"]),
    ("C967633",  ["U2"]),
    ("C3304276", ["U4"]),
    ("C70377",   ["BT1"]),
    ("C165948",  ["J2"]),
    ("C7519",    ["U5"]),
    ("C82942",   ["U3"]),
    ("C15127",   ["Q1"]),
    ("C23186",   ["R7", "R8"]),
    ("C15849",   ["C6", "C7"]),
]:
    for _r in _refs:
        REF_LCSC[_r] = _code

# Per-component ordering notes; surfaced as the Notes column in BOM exports.
BOM_NOTES = {
    "C12": "Select at order: any 0603 NP0/C0G, 56-68pF. Trim to 13.56MHz with a VNA "
           "on the first board before ordering a batch.",
    "SW3": "Right-angle SPDT. Datasheet-exact land including 4 shield tabs and "
           "2x 0.85mm NPTH locating holes -- a substitute switch will not seat.",
    "U1":  "N8R2, not N16R8. PSRAM pins are NC and the int8 model fits 8MB flash.",
    "C10": "22uF substitute -- no basic 100uF exists in 0805.",
}


def u():
    return str(uuid.uuid4())


def extract_block(path, name):
    s = open(path).read()
    i = s.find(f'(symbol "{name}"')
    if i < 0:
        raise SystemExit(f"symbol {name} not found in {path}")
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                break
        j += 1
    return s[i:j + 1]


def build_lib_symbols():
    blocks = []
    for lib_id, (path, name) in LIBSYMS.items():
        blk = extract_block(path, name)
        blk = blk.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
        blocks.append('\t\t' + blk)
    return '\n'.join(blocks)


items = []


GRID = 1.27


def snap(v):
    return round(round(v / GRID) * GRID, 4)


def ep(px, py, lib_id, pin):
    lx, ly = PIN_XY[lib_id][pin]
    return (round(snap(px) + lx, 4), round(snap(py) - ly, 4))


def wire(x1, y1, x2, y2):
    items.append(
        f'\t(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n'
        f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n'
        f'\t\t(uuid "{u()}")\n\t)')


def junction(x, y):
    items.append(
        f'\t(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n'
        f'\t\t(uuid "{u()}")\n\t)')


def no_connect(x, y):
    items.append(f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{u()}")\n\t)')


def glabel(text, x, y, angle=0, justify="left"):
    items.append(
        f'\t(global_label "{text}"\n\t\t(shape bidirectional)\n\t\t(at {x} {y} {angle})\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {justify})\n\t\t)\n'
        f'\t\t(uuid "{u()}")\n'
        f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)\n\t)')


def section_box(x1, y1, x2, y2, title, tx, ty):
    items.append(
        f'\t(rectangle\n\t\t(start {x1} {y1})\n\t\t(end {x2} {y2})\n'
        f'\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type dash)\n\t\t\t(color 0 0 0 1)\n\t\t)\n'
        f'\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')
    items.append(
        f'\t(text "{title}"\n\t\t(exclude_from_sim no)\n\t\t(at {tx} {ty} 0)\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 2.0 2.0)\n\t\t\t\t(thickness 0.4)\n\t\t\t\t(bold yes)\n'
        f'\t\t\t\t(color 30 90 180 1)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)')


def prop(name, value, x, y, angle=0, justify=None, hide=False):
    j = f'\n\t\t\t\t(justify {justify})' if justify else ''
    h = '\n\t\t\t(hide yes)' if hide else ''
    return (f'\t\t(property "{name}" "{value}"\n\t\t\t(at {x} {y} {angle})\n'
            f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t){j}\n\t\t\t){h}\n\t\t)')


def bom_props(ref, x, y):
    """MPN / Manufacturer / LCSC / notes, hidden. Canonical kicad-happy field names."""
    code = REF_LCSC.get(ref, "")
    mpn, mfr = LCSC_PARTS.get(code, ("", ""))
    out = [
        prop("MPN", mpn, x, y, 0, hide=True),
        prop("Manufacturer", mfr, x, y, 0, hide=True),
        prop("LCSC", code, x, y, 0, hide=True),
    ]
    if ref in BOM_NOTES:
        out.append(prop("BOM Comments", BOM_NOTES[ref], x, y, 0, hide=True))
    return out


def place(lib_id, ref, value, x, y, angle, pins, props):
    x, y = snap(x), snap(y)
    pin_lines = '\n'.join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{u()}")\n\t\t)' for p in pins)
    props_txt = '\n'.join(props)
    items.append(
        f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {x} {y} {angle})\n\t\t(unit 1)\n'
        f'\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n'
        f'\t\t(uuid "{u()}")\n{props_txt}\n{pin_lines}\n'
        f'\t\t(instances\n\t\t\t(project "{PROJECT}"\n\t\t\t\t(path "/{ROOT_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')


def part(lib_id, ref, value, x, y, pins):
    fp = FP.get(ref, "")
    place(lib_id, ref, value, x, y, 0, pins, [
        prop("Reference", ref, x + 2.54, y - 1.27, 0, "left"),
        prop("Value", value, x + 2.54, y + 1.27, 0, "left"),
        prop("Footprint", fp, x, y, 0, hide=True),
        prop("Datasheet", "", x, y, 0, hide=True),
        prop("Description", "", x, y, 0, hide=True),
    ] + bom_props(ref, x, y))


def rc(lib_id, ref, value, x, y):
    fp = FP.get(ref, "")
    place(lib_id, ref, value, x, y, 0, ["1", "2"], [
        prop("Reference", ref, x + 1.778, y - 1.016, 0, "left"),
        prop("Value", value, x + 1.778, y + 1.27, 0, "left"),
        prop("Footprint", fp, x, y, 0, hide=True),
        prop("Datasheet", "", x, y, 0, hide=True),
        prop("Description", "", x, y, 0, hide=True),
    ] + bom_props(ref, x, y))


PWR_N = [0]
PWR_LIB = {"GND": "power:GND", "+3V3": "power:+3V3", "VBUS": "power:VBUS"}


def pwr(net, x, y):
    PWR_N[0] += 1
    ref = f"#PWR0{PWR_N[0]:02d}"
    vy = y + 3.302 if net == "GND" else y - 3.302
    place(PWR_LIB[net], ref, net, x, y, 0, ["1"], [
        prop("Reference", ref, x, y, 0, hide=True),
        prop("Value", net, x, vy),
        prop("Footprint", "", x, y, 0, hide=True),
        prop("Datasheet", "", x, y, 0, hide=True),
        prop("Description", "", x, y, 0, hide=True),
    ])


def tap_gnd(x, y, dx=0.0, dy=2.54):
    ex, ey = x + dx, y + dy
    wire(x, y, ex, ey)
    pwr("GND", ex, ey)


def tap_pwr(net, x, y, dx=0.0, dy=-2.54):
    """net in +3V3/VBUS: stub then place power symbol at the stub end."""
    ex, ey = x + dx, y + dy
    wire(x, y, ex, ey)
    pwr(net, ex, ey)


def tap_label(net, x, y, dx=0.0, dy=0.0, just="left"):
    ex, ey = x + dx, y + dy
    if dx or dy:
        wire(x, y, ex, ey)
    glabel(net, ex, ey, 0, just)


# ================================================================ SECTION 1
# POWER — Coin (CR2032) + USB-C/LDO with P-FET auto source-selection
# (the USB-C/LDO/P-FET half lives in section_usb; this section is the coin side)
def section_power():
    section_box(26, 30, 150, 100, "POWER  (CR2032 coin -> SW3 -> VBAT_SW -> Q1 P-FET -> 3V3 rail)", 28, 28)

    # --- Coin cell BT1: pin1(+) -> VBAT, pin2(-) -> GND ---
    bx, by = 55.88, 73.66
    part("JLC:CR2032-BS-6-1", "BT1", "CR2032", bx, by, ["1", "2"])
    p1 = ep(bx, by, "JLC:CR2032-BS-6-1", "1")   # + (left)
    p2 = ep(bx, by, "JLC:CR2032-BS-6-1", "2")   # - (right)
    tap_label("VBAT", p1[0], p1[1], dy=-2.54)    # + -> VBAT (switched)
    tap_gnd(p2[0], p2[1])                         # - -> GND

    # --- SW3 power switch: MSK12C02 SPDT, VBAT -> VBAT_SW ---
    # Pin 2 is the common pole (board pad 2, VBAT); pin 3 is the closed throw;
    # pin 1 is the open throw and is deliberately left unconnected, so sliding
    # to "off" parks the coin on a floating contact. Do not swap the pins.
    # The throw used to land on +3V3 directly; with dual power it now feeds
    # VBAT_SW, the source of battery-isolation P-FET Q1 (see section_usb).
    # NeuralCard.kicad_pcb still has +3V3 on pad 3 until the next board update.
    sx, sy = 76.2, 60.96
    part("Switch:SW_SPDT", "SW3", "MSK12C02", sx, sy, ["1", "2", "3"])
    s1 = ep(sx, sy, "Switch:SW_SPDT", "1")       # open throw
    s2 = ep(sx, sy, "Switch:SW_SPDT", "2")       # common pole
    s3 = ep(sx, sy, "Switch:SW_SPDT", "3")       # closed throw
    tap_label("VBAT", s2[0], s2[1], dx=-2.54, just="right")
    # throw -> VBAT_SW, dropped downward so the label clears C8's +3V3 symbol
    lx_, ly_ = round(s3[0] + 2.54, 4), round(s3[1] + 5.08, 4)
    wire(s3[0], s3[1], lx_, s3[1])
    wire(lx_, s3[1], lx_, ly_)
    glabel("VBAT_SW", lx_, ly_, 90, "right")
    no_connect(s1[0], s1[1])

    # --- Bulk / ride-out caps on +3V3: C8 10uF, C9 22uF, C10 100uF ---
    for ref, val, cx in [("C8", "10uF", 96.52), ("C9", "22uF", 111.76), ("C10", "100uF", 127.0)]:
        rc("Device:C", ref, val, cx, 73.66)
        ct = ep(cx, 73.66, "Device:C", "1")
        cb = ep(cx, 73.66, "Device:C", "2")
        tap_pwr("+3V3", ct[0], ct[1])
        tap_gnd(cb[0], cb[1])

    # No PWR_FLAGs: every power net now has a real power_out driver, so a flag
    # would collide (pin_to_pin power_out vs power_out -- the old ERC errors).
    # GND and VBAT are driven by BT1 (pins typed power_out), +3V3 by U3 VOUT,
    # VBUS by J2's VBUS pins. VBAT_SW carries only passive pins (SW3, Q1
    # source), which ERC does not require a driver for.


def tap_dir(spec, x, y, side, length=2.54):
    """spec: ('gnd',) | ('pwr', net) | ('lbl', net) | ('nc',). side: L/R/U/D."""
    if spec[0] == 'nc':
        no_connect(x, y)
        return
    dx, dy = {'L': (-length, 0), 'R': (length, 0), 'U': (0, -length), 'D': (0, length)}[side]
    ex, ey = round(x + dx, 4), round(y + dy, 4)
    if dx or dy:
        wire(x, y, ex, ey)
    if spec[0] == 'gnd':
        pwr("GND", ex, ey)
    elif spec[0] == 'pwr':
        pwr(spec[1], ex, ey)
    else:  # lbl
        just = {'L': 'right', 'R': 'left', 'U': 'left', 'D': 'left'}[side]
        glabel(spec[1], ex, ey, 0, just)


def rc_net(lib_id, ref, val, x, y, top_spec, bot_spec):
    rc(lib_id, ref, val, x, y)
    t = ep(x, y, lib_id, "1")
    b = ep(x, y, lib_id, "2")
    tap_dir(top_spec, t[0], t[1], 'U')
    tap_dir(bot_spec, b[0], b[1], 'D')


# ================================================================ SECTION 2
# MCU CORE — ESP32-S3-WROOM-1 + USB-C/ESD + BOOT/RESET
def section_mcu():
    section_box(26, 112, 232, 250, "MCU CORE  (ESP32-S3-WROOM-1 + UART programming header)", 28, 110)

    # --- ESP32-S3 module U1 ---
    ux, uy = 130.0, 175.0
    esp = "JLC:ESP32-S3-WROOM-1"
    part(esp, "U1", "ESP32-S3-WROOM-1", ux, uy,
         [str(i) for i in range(1, 42)])
    specs = {
        "1": ("gnd",), "2": ("pwr", "+3V3"), "3": ("lbl", "EN"),
        "4": ("lbl", "CHX1"), "5": ("lbl", "CHX2"), "6": ("lbl", "CHX3"),
        "7": ("lbl", "CHX4"), "8": ("lbl", "CHX5"), "9": ("lbl", "CHX6"),
        "10": ("lbl", "SCL"), "11": ("lbl", "IMU_INT"), "12": ("lbl", "SDA"),
        "13": ("lbl", "USB_DM"),            # IO19 = native USB D- (Table 3-1)
        "14": ("lbl", "USB_DP"),            # IO20 = native USB D+
        "27": ("lbl", "IO0"), "40": ("gnd",), "41": ("gnd",),
    }
    for n in range(15, 27):       # bottom row -> all unused
        specs[str(n)] = ("nc",)
    for n in range(28, 40):       # right-side unused (incl. 35/36/37 PSRAM)
        specs[str(n)] = ("nc",)
    specs["36"] = ("lbl", "RXD")  # RXD0 (GPIO44) -> prog header RX
    specs["37"] = ("lbl", "TXD")  # TXD0 (GPIO43) -> prog header TX
    specs["23"] = ("lbl", "NFC_GPO")  # GPIO21 <- ST25DV field-detect interrupt
    for n in range(1, 42):
        pn = str(n)
        px, py = ep(ux, uy, esp, pn)
        lx, ly = PIN_XY[esp][pn]
        side = 'D' if ly < -30 else ('L' if lx < 0 else 'R')
        tap_dir(specs[pn], px, py, side)

    # --- decoupling: C1/C2/C3 100nF on +3V3 ---
    for ref, cx in [("C1", 178.0), ("C2", 188.0), ("C3", 198.0)]:
        rc_net("Device:C", ref, "100nF", cx, 132.0, ("pwr", "+3V3"), ("gnd",))

    # --- EN reset: R9 10k (+3V3->EN), C4 100nF (EN->GND), SW2 RESET (EN<->GND) ---
    rc_net("Device:R", "R9", "10k", 70.0, 132.0, ("pwr", "+3V3"), ("lbl", "EN"))
    rc_net("Device:C", "C4", "100nF", 84.0, 132.0, ("lbl", "EN"), ("gnd",))
    sw_btn("SW2", 64.0, 150.0, "EN")

    # --- BOOT: R10 10k (+3V3->IO0), SW1 BOOT (IO0<->GND) ---
    rc_net("Device:R", "R10", "10k", 210.0, 132.0, ("pwr", "+3V3"), ("lbl", "IO0"))
    sw_btn("SW1", 200.0, 150.0, "IO0")

    # --- UART programming header J1 (3V3, GND, TX, RX, EN, IO0) ---
    jx, jy = 70.0, 215.0
    hdr = "Connector_Generic:Conn_01x06"
    part(hdr, "J1", "ProgPads", jx, jy, ["1", "2", "3", "4", "5", "6"])
    hspec = {
        "1": ("pwr", "+3V3"), "2": ("gnd",), "3": ("lbl", "TXD"),
        "4": ("lbl", "RXD"), "5": ("lbl", "EN"), "6": ("lbl", "IO0"),
    }
    for pn, spec in hspec.items():
        px, py = ep(jx, jy, hdr, pn)
        tap_dir(spec, px, py, 'L')


def sw_btn(ref, x, y, signal):
    """TS-1187A tact: pins A(1),C(3) -> signal (left); B(2),D(4) -> GND (right)."""
    sw = "JLC:TS-1187A-B-A-B"
    part(sw, ref, "SW_PUSH", x, y, ["1", "2", "3", "4"])
    a = ep(x, y, sw, "1")
    b = ep(x, y, sw, "2")
    c = ep(x, y, sw, "3")
    d = ep(x, y, sw, "4")
    tap_dir(("lbl", signal), a[0], a[1], 'L')
    tap_dir(("lbl", signal), c[0], c[1], 'L')
    tap_dir(("gnd",), b[0], b[1], 'R')
    tap_dir(("gnd",), d[0], d[1], 'R')


# ================================================================ SECTION 3
# IMU — LSM6DS3TR-C 6-axis (air-writing) on I2C
def section_imu():
    section_box(240, 112, 392, 210, "IMU  (LSM6DS3TR-C 6-axis, I2C addr 0x6B)", 242, 110)

    ix, iy = 312.0, 150.0
    imu = "JLC:LSM6DS3TR-C"
    part(imu, "U2", "LSM6DS3TR-C", ix, iy, [str(i) for i in range(1, 15)])
    ispec = {
        "1": ("pwr", "+3V3"),        # SDO/SA0 -> +3V3 (I2C addr 0x6B; routed
                                     # net, unlike pour-dependent GND)
        "2": ("nc",), "3": ("nc",),  # SDx/SCx aux unused
        "4": ("lbl", "IMU_INT"),     # INT1
        "5": ("pwr", "+3V3"),        # VDDIO
        "6": ("gnd",), "7": ("gnd",),
        "8": ("pwr", "+3V3"),        # VDD
        "9": ("nc",), "10": ("nc",), "11": ("nc",),
        "12": ("pwr", "+3V3"),       # CS -> high = I2C mode
        "13": ("lbl", "SCL"), "14": ("lbl", "SDA"),
    }
    for n in range(1, 15):
        pn = str(n)
        px, py = ep(ix, iy, imu, pn)
        lx, _ = PIN_XY[imu][pn]
        tap_dir(ispec[pn], px, py, 'L' if lx < 0 else 'R')

    # I2C pull-ups to +3V3
    rc_net("Device:R", "R11", "4.7k", 280.0, 128.0, ("pwr", "+3V3"), ("lbl", "SDA"))
    rc_net("Device:R", "R12", "4.7k", 290.0, 128.0, ("pwr", "+3V3"), ("lbl", "SCL"))
    # VDD decoupling
    rc_net("Device:C", "C5", "100nF", 350.0, 150.0, ("pwr", "+3V3"), ("gnd",))


# ================================================================ SECTION 4
# NEURON LEDs — 24x charlieplexed on 6 GPIO (the neural-net art)
def led_cp(ref, x, y, i, j):
    """Horizontal LED: K(left)->CPj, A(right)->CPi."""
    # "red" per the v2 decision (KT-0603R / C2286) -- blue cannot be driven from a
    # 3.0V coin with margin. The footprint and fab BOM have always been red; only
    # this Value string lagged behind.
    place("Device:LED", ref, "red", x, y, 0, ["1", "2"], [
        prop("Reference", ref, x, y - 2.794, 0, "left"),
        prop("Value", "red", x, y + 2.794, 0, "left"),
        prop("Footprint", FP.get(ref, ""), x, y, 0, hide=True),
        prop("Datasheet", "", x, y, 0, hide=True),
        prop("Description", "", x, y, 0, hide=True),
    ] + bom_props(ref, x, y))
    k = ep(x, y, "Device:LED", "1")   # cathode (left)
    a = ep(x, y, "Device:LED", "2")   # anode (right)
    tap_dir(("lbl", f"CP{j}"), k[0], k[1], 'L')
    tap_dir(("lbl", f"CP{i}"), a[0], a[1], 'R')


def section_leds():
    section_box(26, 258, 360, 374,
                "NEURON LEDs  (24x charlieplex on 6 GPIO)   input(6) > hidden(8) > output(10)",
                28, 256)
    # charlieplex current-limit resistors R1-R6: CHXn -> CPn (one node per GPIO line)
    for n in range(1, 7):
        rc_net("Device:R", f"R{n}", "220R", 40.64 + (n - 1) * 19.05, 272.0,
               ("lbl", f"CHX{n}"), ("lbl", f"CP{n}"))
    # 24 neuron LEDs across 24 ordered CP-node pairs (i=anode node, j=cathode node)
    pairs = [(i, j) for i in range(1, 7) for j in range(1, 7) if i != j][:24]
    cols = [60.96, 111.76, 162.56, 213.36, 264.16, 314.96]
    rows = [299.72, 318.77, 337.82, 356.87]
    for idx, (i, j) in enumerate(pairs):
        led_cp(f"D{idx + 1}", cols[idx % 6], rows[idx // 6], i, j)


# ================================================================ SECTION 5
# NFC — ST25DV04KC dynamic tag (tap-to-share) on I2C + PCB loop antenna
def section_nfc():
    section_box(400, 112, 560, 210, "NFC  (ST25DV04KC, I2C addr 0x53/0x57, PCB coil on AC0/AC1)", 402, 110)

    nx, ny = 470.0, 160.0
    nfc = "ST25DV:ST25DV04KC-IE6S3"
    part(nfc, "U4", "ST25DV04KC-IE6S3", nx, ny, [str(i) for i in range(1, 9)])
    nspec = {
        "1": ("nc",),                    # V_EH energy harvesting unused
        "2": ("lbl", "NFC_ANT_A"),       # AC0 -> coil outer terminal
        "3": ("lbl", "NFC_ANT_B"),       # AC1 -> coil inner terminal
        "4": ("gnd",),
        "5": ("lbl", "SDA"),             # shared bus with IMU (addrs differ)
        "6": ("lbl", "SCL"),
        "7": ("lbl", "NFC_GPO"),         # open-drain field-detect -> GPIO21
        "8": ("pwr", "+3V3"),
    }
    for n in range(1, 9):
        pn = str(n)
        px, py = ep(nx, ny, nfc, pn)
        lx, _ = PIN_XY[nfc][pn]
        tap_dir(nspec[pn], px, py, 'L' if lx < 0 else 'R')

    # GPO is open-drain: pull-up to +3V3
    rc_net("Device:R", "R14", "100k", 430.0, 128.0, ("pwr", "+3V3"), ("lbl", "NFC_GPO"))
    # VCC decoupling
    rc_net("Device:C", "C11", "100nF", 530.0, 128.0, ("pwr", "+3V3"), ("gnd",))
    # antenna tuning cap across the coil (value trimmed after VNA measurement:
    # coil ~1.5uH (9 turns) + chip 28.5pF internal -> ~62pF external,
    # ~13.6 MHz pre-fab)
    rc_net("Device:C", "C12", "62pF", 430.0, 180.0, ("lbl", "NFC_ANT_A"), ("lbl", "NFC_ANT_B"))

    # the PCB coil itself (net-tie footprint: 13x24.5mm 10-turn spiral, B.Cu)
    ax, ay = 480.0, 190.0
    ant = "Connector_Generic:Conn_01x02"
    part(ant, "ANT1", "NFC_COIL", ax, ay, ["1", "2"])
    for pn, net in (("1", "NFC_ANT_A"), ("2", "NFC_ANT_B")):
        px, py = ep(ax, ay, ant, pn)
        tap_dir(("lbl", net), px, py, 'L')


# ================================================================ SECTION 6
# USB-C POWER/DATA — VBUS -> ME6211 LDO -> +3V3; AO3401A isolates the coin
# while USB is present; USBLC6 ESD array on the native-USB data lines.
def section_usb():
    section_box(158, 30, 448, 100,
                "USB-C  (VBUS -> ME6211 3.3V LDO; Q1 P-FET isolates coin when USB present; USBLC6 ESD)",
                160, 28)

    # --- J2 USB-C receptacle (TYPE-C-31-M-12, 16 pins) ---
    # 5.1k Rd on CC1/CC2 advertises a UFP sink, so any source grants 5V VBUS.
    # DP1/DP2 and DN1/DN2 are ganged externally by labelling both to the same
    # net (required for either plug orientation). SBU pins are typed
    # no_connect in JLC.kicad_sym; EH shell tabs 1-4 go to GND.
    jx, jy = 185.0, 66.0
    usb = "JLC:TYPE-C-31-M-12"
    part(usb, "J2", "TYPE-C-31-M-12", jx, jy, list(PIN_XY[usb]))
    # Left column uses global labels throughout (GND/VBUS labels merge with the
    # power-symbol nets by name) -- power-symbol graphics at 2.54 pitch overlap
    # the neighbouring pins' wires.
    uspec = {
        "A1B12": ("lbl", "GND"), "A4B9": ("lbl", "VBUS"), "B8": ("nc",), "A5": ("lbl", "CC1"),
        "B7": ("lbl", "USB_DM"), "A6": ("lbl", "USB_DP"),
        "A7": ("lbl", "USB_DM"), "B6": ("lbl", "USB_DP"),
        "A8": ("nc",), "B5": ("lbl", "CC2"), "B4A9": ("lbl", "VBUS"), "B1A12": ("lbl", "GND"),
    }
    for pn, spec in uspec.items():
        px, py = ep(jx, jy, usb, pn)
        tap_dir(spec, px, py, 'L')
    # shell tabs 1-4 (EH): bus with one vertical wire, single GND drop
    eh = [ep(jx, jy, usb, pn) for pn in ("4", "3", "2", "1")]   # top to bottom
    vx = round(eh[0][0] + 2.54, 4)
    for px, py in eh:
        wire(px, py, vx, py)
    wire(vx, eh[0][1], vx, eh[-1][1])
    junction(vx, eh[1][1])
    junction(vx, eh[2][1])
    tap_gnd(vx, eh[-1][1])

    # CC pulldowns: 5.1k each to GND (never share one resistor across CC1/CC2)
    rc_net("Device:R", "R7", "5.1k", 215.0, 48.0, ("lbl", "CC1"), ("gnd",))
    rc_net("Device:R", "R8", "5.1k", 225.0, 48.0, ("lbl", "CC2"), ("gnd",))

    # --- U5 USBLC6-2SC6 ESD array on USB_DP/USB_DM ---
    # I/O1 = pins 1+6 (internally paired), I/O2 = pins 3+4; the array clamps
    # the lines to GND/VBUS. Labels put both ends of each pair on the same net.
    ex_, ey_ = 262.0, 66.0
    esd = "JLC:USBLC6-2SC6"
    part(esd, "U5", "USBLC6-2SC6", ex_, ey_, [str(i) for i in range(1, 7)])
    espec = {
        "1": ("lbl", "USB_DP"), "2": ("gnd",), "3": ("lbl", "USB_DM"),
        "4": ("lbl", "USB_DM"), "5": ("pwr", "VBUS"), "6": ("lbl", "USB_DP"),
    }
    for pn, spec in espec.items():
        px, py = ep(ex_, ey_, esd, pn)
        lx, _ = PIN_XY[esd][pn]
        tap_dir(spec, px, py, 'L' if lx < 0 else 'R')

    # --- U3 ME6211C33M5G-N LDO: VBUS -> +3V3, CE tied to VIN ---
    lx3, ly3 = 330.0, 60.0
    ldo = "JLC:ME6211C33M5G-N"
    part(ldo, "U3", "ME6211C33M5G-N", lx3, ly3, ["1", "2", "3", "4", "5"])
    vin = ep(lx3, ly3, ldo, "1")
    vss = ep(lx3, ly3, ldo, "2")
    ce = ep(lx3, ly3, ldo, "3")
    nc4 = ep(lx3, ly3, ldo, "4")
    vout = ep(lx3, ly3, ldo, "5")
    tx = round(vin[0] - 5.08, 4)                  # CE-to-VIN tie rail
    wire(vin[0], vin[1], tx, vin[1])
    pwr("VBUS", tx, vin[1])
    wire(ce[0], ce[1], tx, ce[1])
    wire(tx, ce[1], tx, vin[1])
    junction(tx, vin[1])
    tap_dir(("gnd",), vss[0], vss[1], 'L')
    tap_dir(("pwr", "+3V3"), vout[0], vout[1], 'R')
    no_connect(nc4[0], nc4[1])
    # 1uF ceramics on VIN and VOUT (ME6211 datasheet stability minimum)
    rc_net("Device:C", "C6", "1uF", 312.0, 84.0, ("pwr", "VBUS"), ("gnd",))
    rc_net("Device:C", "C7", "1uF", 352.0, 84.0, ("pwr", "+3V3"), ("gnd",))

    # --- Q1 AO3401A P-FET battery path: VBAT_SW -> +3V3 when USB absent ---
    # Source = SW3's throw (VBAT_SW), drain = +3V3 rail, gate = VBUS with R13
    # 100k pulldown. USB present: gate high, FET off, coin isolated (body diode
    # sees 3.3V drain vs 3.0V source = 0.3V < Vf, stays off). USB absent: R13
    # pulls the gate low and the coin feeds the rail through the FET.
    qx, qy = 400.0, 58.0
    fet = "JLC:AO3401A"
    part(fet, "Q1", "AO3401A", qx, qy, ["1", "2", "3"])
    g = ep(qx, qy, fet, "1")
    s = ep(qx, qy, fet, "2")
    d = ep(qx, qy, fet, "3")
    tap_dir(("pwr", "VBUS"), g[0], g[1], 'L', 5.08)
    tap_dir(("lbl", "VBAT_SW"), s[0], s[1], 'D')
    tap_dir(("pwr", "+3V3"), d[0], d[1], 'U')
    rc_net("Device:R", "R13", "100k", 424.0, 58.0, ("pwr", "VBUS"), ("gnd",))


# ================================================================ build
section_power()
section_mcu()
section_imu()
section_leds()
section_nfc()
section_usb()

lib_symbols = build_lib_symbols()
body = '\n'.join(items)
out = f'''(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "9.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A2")
\t(title_block
\t\t(title "NeuralCard")
\t\t(rev "V0.1")
\t\t(company "Barakaeli Lawuo")
\t\t(comment 1 "AI business card - air-writing digit recognition, ESP32-S3")
\t)
\t(lib_symbols
{lib_symbols}
\t)
{body}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
open("NeuralCard.kicad_sch", "w").write(out)
print(f"wrote NeuralCard.kicad_sch: {len(out)} bytes, {len(items)} items")
