# NeuralCard firmware

Bring-up scaffold for the v2.3 board. What works today:

- **Charlieplex driver** for all 24 LEDs, 8 brightness levels, mapping
  extracted from the board netlist (D1-D24 -> CP pin pairs)
- **LSM6DS3 driver** over I2C (SDA=IO8, SCL=IO17, addr 0x6B)
- **Gesture recorder** - motion-triggered capture printed as CSV over the
  USB-C serial console, for building the training dataset
- Boot self-test: LED sweep + IMU WHO_AM_I check

What is deliberately not here yet: the neural network. It gets trained from
gestures recorded with this firmware, then lands as a quantised C array in a
later step.

## Build & flash

Requires ESP-IDF v5.x (`idf.py` on PATH, target esp32s3).

    cd firmware
    idf.py set-target esp32s3
    idf.py build
    idf.py flash monitor        # plain USB-C cable, no adapter

First flash of a blank board: hold BOOT, tap RST, release BOOT (printed on
the silk), then run the flash command.

## Serial commands

| Key | Action |
|---|---|
| `t` | LED sweep test |
| `s` | stream raw IMU CSV (any key stops) |
| `0`-`9` | record one gesture labelled with that digit |

## Training data

The plan is to train on an existing public dataset rather than recording
gestures by hand.

The one that fits is **6DMG** (6D Motion Gesture Database, Georgia Tech). It
contains air-written digits and letters captured with a 6-axis IMU,
accelerometer plus gyroscope, which is the same signal shape the LSM6DS3
produces. Verify the current hosting and license before use.

Two datasets that look relevant but are not:

| Dataset | Why it does not fit |
|---|---|
| UCI Character Trajectories | Pen tip on a tablet surface, 2D velocity and pen force. No gyroscope, and writing on glass is not the same motion as writing in the air. |
| TensorFlow "magic wand" | Accelerometer only, and the gestures are wing, ring and slope. There are no digits in it. Useful as a reference implementation of on-device inference, not as data. |

### Closing the hardware gap without recording anything

Public data was recorded on different hardware, at a different sample rate,
held differently. A card pinched between finger and thumb does not move like a
Wii Remote gripped in a fist. Train-time augmentation covers most of that gap
without collecting a single gesture:

1. Resample every sequence to a fixed length, so the source rate stops
   mattering and fast and slow writers look alike.
2. Subtract gravity, then normalize each gesture to unit scale. This removes
   absolute orientation and the difference between large and small handwriting.
3. Augment hard during training: random rotation about all three axes to
   simulate different hold angles, time warping for speed, amplitude scaling,
   and additive noise.

Rotation augmentation is the important one. It is what lets a model trained on
a fist-held remote generalise to a card held at an unpredictable angle.

Expect this to work less well than data recorded on the card itself,
particularly for the pairs that already confuse models, 3 against 8 and 1
against 7. The gesture recorder above stays in the firmware so that measuring
that gap on real hardware is possible later.

## One thing to verify on first light-up

`cp_set_outputs()` assumes D16-D24 are the output-column LEDs beside the 0-9
silk labels in order. The netlist cannot confirm visual order - check it
against the physical board and permute the mapping if needed.
