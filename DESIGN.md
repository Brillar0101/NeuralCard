# NeuralCard — AI Business Card (Design Spec)

> An ESP32-S3 PCB business card shaped like a neural network. You **air-write a digit (0–9)
> holding the card**; an on-device neural net classifies the motion, and the **LEDs at each
> neuron node ripple the real inference** — the brightest output neuron is the recognized digit.

**Owner:** Barakaeli Lawuo — AI & Computer Engineer
**Location:** `~/kicad-projects/NeuralCard/` (moved off the TCC-protected Desktop so tooling
like `easyeda2kicad` doesn't trip macOS file-access protection).
**KiCad:** v9 file format, `kicad-cli 10.0.3`.

---

## 1. Form factor (ISO/IEC 7810 ID-1 — real credit card)

| Spec | Value |
|---|---|
| Outline | **85.60 mm × 53.98 mm** rounded rectangle |
| Corner radius | **3.18 mm** |
| PCB thickness | **0.8 mm** (card-like) |
| Layers | 2-layer |
| Assembly | **100% SMD/SMT. Only non-soldered item = the CR2032 coin.** Fab: **JLCPCB**. |

Board outline is on `Edge.Cuts` in `NeuralCard.kicad_pcb` (render-verified).

---
