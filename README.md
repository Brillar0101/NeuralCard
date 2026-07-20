# NeuralCard

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

Runs on a 2-layer board. Everything is assembled by JLCPCB except the coin
cell.
