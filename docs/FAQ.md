# NeuralCard FAQ

Answers to the questions people actually ask about this board. Everything here
refers to hardware revision v2.3.

---

### What does the card actually do?

You hold it, air-write a digit (0-9), and a neural network running on the card
classifies the gesture. The 24 LEDs on the front are drawn as a network of
neurons - the output column on the right edge lights up with the network's
answer, brightest neuron wins. Tap a phone on the NFC area and it opens a
contact page. It is a business card that demonstrates the thing it claims its
owner can do.

### How does it detect the number?

Five stages, all on the card:

1. **Capture** - the LSM6DS3 IMU streams 6-axis motion (accel + gyro) at a few
   hundred Hz. An air-written digit is a ~1.5 s time-series with a distinctive
   shape per digit.
2. **Segmentation** - the IMU's motion interrupt wakes the ESP32; recording
   runs until the motion stops.
3. **Preprocessing** - gravity is subtracted, the gesture is resampled to a
   fixed length and normalised, so a big slow "7" and a small quick "7" look
   alike.
4. **Inference** - a small quantised network (1D-CNN or MLP, tens of thousands
   of parameters, trained offline on recorded gestures) turns ~600 input
   numbers into 10 output scores. The ESP32-S3's vector instructions run this
   in milliseconds.
5. **Display** - softmax confidences map to LED brightness on the 0-9 output
   column. 80% sure it's a 3 means LED "3" blazes and "8" glimmers.

Nothing on the card "knows" what a 3 is - the network is just trained weights,
and detection is a matrix multiplication small enough for a coin cell.

### What battery does it take?

A single CR2032 lithium coin cell, plus-side facing out, held in the
CR2032-BS-6-1 clip on the back. The slide switch (SW3) next to it is the power
switch. The battery is not rechargeable and the board never attempts to charge
it - see the next answer.

### Does it only work on the coin cell? What can't it do on battery?

Three power states, three capability levels:

| | No power | CR2032 | USB-C |
|---|---|---|---|
| NFC tap-to-share | **yes** | yes | yes |
| Gestures + inference + LEDs | no | **yes** | yes |
| Flashing / serial | no | no | **yes** |
| WiFi / Bluetooth | no | no | yes |
| Full LED brightness | no | limited | yes |

The NFC chip is a passive tag powered by the reading phone's own radio field,
so the business-card function works with the battery dead or missing.

The coin cell's limit is internal resistance, not capacity: it delivers
10-30 mA comfortably, sags on spikes. Inference at reduced CPU clock fits;
a WiFi transmit burst (300 mA+) collapses the rail and resets the chip. Radio
features are therefore USB-only by physics, not by policy.

When USB-C is plugged in, a P-FET (Q1) disconnects the battery entirely -
USB can never back-feed or charge the cell.

### Can I program it over USB-C?

Yes - that is the point of v2.3. The USB-C data pair is routed to the
ESP32-S3's native USB-Serial-JTAG, so a plain USB-C cable gives you flashing
and a serial console with no adapter. First-time flash of a blank board:
hold BOOT, tap RST, release BOOT (also printed on the silk). After the first
firmware, esptool resets it automatically.

Note the corollary: initial flashing is the one thing that strictly requires
the USB port. A blank ESP32 cannot be programmed by battery wishes or NFC.

### Why only 6 pins for 24 LEDs?

Charlieplexing. Each LED only conducts for one specific pair-and-polarity of
the six charlieplex lines (CHX1-6 through the 220R resistors), so n pins drive
n*(n-1) LEDs - 6 pins cover up to 30. The firmware scans fast enough that
persistence of vision turns one-at-a-time flashes into a steady image, and
per-LED duty cycle becomes brightness. It is also why the display is
coin-cell-viable: only one LED is ever actually on.

### What does it cost to build?

Two routes (5-board quantities, 2026 prices):

- **Hand assembly**: ~$9 for PCBs + solder-paste stencil from JLCPCB, ~$77 of
  parts from LCSC (spare-heavy quantities - the floor is ~$60). About a third
  of the parts cost is the five ESP32-S3 modules alone. Passives are
  essentially free: ~700 resistors and capacitors cost about $8.
- **Factory assembly**: ~$168 extra at JLCPCB for 5 boards, of which ~$100 is
  fixed setup/feeder/stencil overhead that would amortise at volume. Rational
  at 30+ boards, not at 5.

The fab files are in `fab/` (gerber zip, BOM with LCSC part numbers, CPL).

### Anything tricky about hand-soldering it?

Two parts. The LSM6DS3 IMU is an LGA-14 at 0.5 mm pitch with pads under the
package - stencil plus hot plate or hot air, an iron alone cannot reach the
joints. The ESP32 module's thermal pad likes hot air too. Everything else is
0603/0805/SOT/SO-8 and iron-friendly. The LEDs go on the front face,
everything else on the back - two paste passes. Buttons and the battery clip
solder last with an iron.

Known substitution: the BOM specifies ST25DV04K-IER6S3 (C155601) for the NFC
chip because the original ST25DV04KC variant is nearly out of stock
everywhere. Same package, same pinout, same function.

### What is C12 and why is its value "tune after VNA"?

C12 parallel-tunes the NFC antenna coil to 13.56 MHz. The right value depends
on the manufactured coil's actual inductance, so the design carries a 68 pF
C0G placeholder inside the calculated 56-68 pF window. Read range is the
practical test: if taps need contact instead of ~2 cm, swap C12 a few pF and
retest. A VNA makes this rigorous; a phone and patience make it possible.

### Does the card need firmware to be useful?

The NFC contact-sharing works from the moment U4 is soldered and programmed
with an NDEF record - no firmware, no battery. Everything else (gestures,
inference, LEDs) is firmware that lives ahead: charlieplex scanner, IMU
streaming, gesture recording, then the trained model. The hardware for every
stage is on the board and verified.
