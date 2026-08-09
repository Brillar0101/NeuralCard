// NeuralCard v2.3 pin map - extracted from the board netlist, do not guess.
#pragma once

// Charlieplex lines CP1..CP6 (through R1-R6, 220R)
#define PIN_CP1  4
#define PIN_CP2  5
#define PIN_CP3  6
#define PIN_CP4  7
#define PIN_CP5  15
#define PIN_CP6  16

// I2C bus shared by the IMU (U2) and the NFC chip's I2C side (U4)
#define PIN_SDA  8
#define PIN_SCL  17
#define I2C_PORT 0

// LSM6DS3TR-C, SA0 strapped high
#define LSM6DS3_ADDR 0x6B
#define PIN_IMU_INT  18

// ST25DV GPO (field-detect interrupt from a phone tap)
#define PIN_NFC_GPO  21
