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
