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
    "power:GND": (POWER_LIB, "GND"),
    "power:+3V3": (POWER_LIB, "+3V3"),
    "power:VBUS": (POWER_LIB, "VBUS"),
    "power:PWR_FLAG": (POWER_LIB, "PWR_FLAG"),
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
    "R7": "Resistor_SMD:R_0603_1608Metric",
    "R8": "Resistor_SMD:R_0603_1608Metric",
    "R9": "Resistor_SMD:R_0603_1608Metric",
    "R10": "Resistor_SMD:R_0603_1608Metric",
    "C1": "Capacitor_SMD:C_0603_1608Metric",
    "C2": "Capacitor_SMD:C_0603_1608Metric",
    "C3": "Capacitor_SMD:C_0603_1608Metric",
    "C4": "Capacitor_SMD:C_0603_1608Metric",
    "U2": "JLC:LGA-14_L3.0-W2.5-P0.50-TL",
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

