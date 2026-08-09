// 24-LED charlieplex driver for the neuron display.
// Set per-LED brightness 0..8 in cp_frame[]; the scanner does the rest.
#pragma once
#include <stdint.h>

#define CP_NUM_LEDS 24

// Brightness framebuffer, index 0 = D1 ... 23 = D24. 0=off, 8=full.
extern volatile uint8_t cp_frame[CP_NUM_LEDS];

// Output-column helpers: D16..D24 sit next to the 0-9 silk labels.
// cp_set_outputs() maps ten 0..255 confidences onto the output column.
void cp_init(void);
void cp_clear(void);
void cp_set_outputs(const uint8_t conf[10]);
