# NeuralCard

[![KiCad 9](https://img.shields.io/badge/KiCad-9.0-0066CC)](https://www.kicad.org/)
[![Board](https://img.shields.io/badge/board-85.6%20%C3%97%2054%20mm%20%C2%B7%202--layer-009596)](docs/DESIGN.md)
[![Parts](https://img.shields.io/badge/BOM-52%20placements%20%C2%B7%20~%246.91-3E8635)](docs/BOM.md)

A business card that runs a neural network.

It's a credit card sized PCB (85.6 x 54 mm, 0.8 mm thick) with an ESP32-S3,
a 6-axis IMU, and 24 LEDs arranged as the network it actually runs: 6 input
neurons, 8 hidden, 10 output. You hold the card, draw a digit in the air,
and the LEDs light with the real activations as the inference runs. The
brightest output neuron is the guess.

The front artwork is the network diagram. The synapse lines are drawn at
three different stroke weights, the way a trained model's weights differ.
The card also has an NFC tag (ST25DV04KC) with a PCB coil antenna, so
tapping it with a phone opens [princetekki.com/card](https://www.princetekki.com/card)
and offers my contact as a vCard. That part works even with a dead battery,
since the tag is powered by the phone's field.

![front](render/NeuralCard_front_v21.png)
![back](render/NeuralCard_back_v21.png)

## Hardware

- ESP32-S3-WROOM-1 (radio off, coin cell life)
- LSM6DS3TR-C accelerometer + gyro on I2C. Its six axes map one to one
  onto the six input neurons.
- 24 red LEDs charlieplexed on 6 GPIO, software PWM for the glow
- ST25DV04KC dynamic NFC tag, 9-turn coil etched on the back copper,
  tuned with a single external cap against the chip's internal 28.5 pF
- CR2032 coin cell. No USB connector: you flash once through six UART
  pads with a serial adapter, then it runs on the coin.
- MSK12C02 slide switch (SW3) on the coin's positive terminal, so the card
  has a real off position rather than only a firmware deep sleep.

Runs on a 2-layer board. Everything is assembled by JLCPCB except the coin
cell.

## How it's wired

Power. The coin's positive terminal runs through a real slide switch, so the
card has a hard off rather than only a firmware deep sleep. Pin 2 of SW3 is the
common pole; sliding it the other way parks the coin on a floating contact.

```mermaid
flowchart LR
    BT1["BT1<br/>CR2032 · 3.0 V"] -->|VBAT| SW3{{"SW3 · MSK12C02<br/>SPDT slide"}}
    SW3 -->|"pin 3 · ON"| RAIL[["+3V3 rail"]]
    SW3 -.->|"pin 1 · OFF"| NC(["open throw"])
    PADS["6 UART pads<br/>3V3 during flashing"] --> RAIL
    RAIL --> U1["ESP32-S3-WROOM-1"]
    RAIL --> U2["LSM6DS3TR-C<br/>IMU"]
    RAIL --> U4["ST25DV04KC<br/>NFC"]
    RAIL --> LEDS["24 red LEDs<br/>charlieplexed on 6 GPIO"]

    classDef src fill:#F0AB00,stroke:#795600,color:#151515
    classDef sw fill:#0066CC,stroke:#003366,color:#FFFFFF
    classDef rail fill:#009596,stroke:#005F60,color:#FFFFFF
    classDef load fill:#F0F0F0,stroke:#8A8D90,color:#151515
    classDef off fill:#FFFFFF,stroke:#C9190B,color:#C9190B,stroke-dasharray:4 3
    class BT1,PADS src
    class SW3 sw
    class RAIL rail
    class U1,U2,U4,LEDS load
    class NC off
```

Inference. The six IMU axes map one-to-one onto the six input neurons, and the
LEDs at each node light with the real activations as the net runs.

```mermaid
flowchart LR
    IMU["LSM6DS3TR-C<br/>ax ay az · gx gy gz"] --> IN["INPUT<br/><b>6 neurons</b>"]
    IN --> HID["HIDDEN<br/><b>8 neurons</b>"]
    HID --> OUT["OUTPUT<br/><b>10 neurons</b><br/>digits 0-9"]
    OUT --> GUESS(["brightest neuron<br/>= the guess"])

    classDef sensor fill:#F0AB00,stroke:#795600,color:#151515
    classDef layer fill:#0066CC,stroke:#003366,color:#FFFFFF
    classDef out fill:#5752D1,stroke:#2A265F,color:#FFFFFF
    classDef result fill:#3E8635,stroke:#1F4D19,color:#FFFFFF
    class IMU sensor
    class IN,HID layer
    class OUT out
    class GUESS result
```

All 24 LEDs are driven from 6 GPIO by charlieplexing, which is why there are
6 current-limiting resistors rather than 24.

## Ordering

The `fab/` folder has the current gerber zip, BOM, and pick and place file.
Order settings that matter: 2 layers, 0.8 mm, matte black mask, ENIG
(the hairline under the name is a mask opening over the ground pour, so it
comes out gold), Standard PCBA. One BOM line, the 62 pF antenna tuning cap,
is marked select-at-order: pick any 0603 NP0 in the 56 to 68 pF range from
their catalog. Check the antenna resonance on the first board with a VNA
before ordering a big batch. The math says 13.6 MHz but copper nearby pulls
it down, and the cap value is the knob.

## Status

Hardware is done and verified: ERC clean, 100% routed, DRC clean. The
firmware (IMU capture, the actual digit model, LED playback) is specced in
DESIGN.md but not written yet, so right now the card is a very elaborate
NFC business card. That part alone already works.

## License

CERN-OHL-P v2. See LICENSE. Do whatever you want with it, attribution
appreciated.
