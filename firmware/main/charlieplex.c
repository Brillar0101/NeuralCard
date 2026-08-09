#include "charlieplex.h"
#include "board.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include <string.h>

// LED n lights when anode pin is driven HIGH and cathode pin LOW,
// all other CP lines high-impedance. Table extracted from the netlist.
typedef struct { uint8_t anode, cathode; } led_t;

static const uint8_t cp_pin[6] = { PIN_CP1, PIN_CP2, PIN_CP3,
                                   PIN_CP4, PIN_CP5, PIN_CP6 };

static const led_t leds[CP_NUM_LEDS] = {
    /* D1  */ {0,1}, /* D2  */ {0,2}, /* D3  */ {0,3}, /* D4  */ {0,4},
    /* D5  */ {0,5}, /* D6  */ {1,0}, /* D7  */ {1,2}, /* D8  */ {1,3},
    /* D9  */ {1,4}, /* D10 */ {1,5}, /* D11 */ {2,0}, /* D12 */ {2,1},
    /* D13 */ {2,3}, /* D14 */ {2,4}, /* D15 */ {2,5}, /* D16 */ {3,0},
    /* D17 */ {3,1}, /* D18 */ {3,2}, /* D19 */ {3,4}, /* D20 */ {3,5},
    /* D21 */ {4,0}, /* D22 */ {4,1}, /* D23 */ {4,2}, /* D24 */ {4,3},
};

volatile uint8_t cp_frame[CP_NUM_LEDS];

static void all_hiz(void)
{
    for (int i = 0; i < 6; i++)
        gpio_set_direction(cp_pin[i], GPIO_MODE_INPUT);
}

// One LED per tick, 8-tick software PWM per LED.
// 24 LEDs * 8 levels * 60 Hz refresh -> ~11.5 kHz tick; 80 us is comfortable.
static void scan_cb(void *arg)
{
    static uint8_t led = 0, phase = 0;

    all_hiz();
    if (cp_frame[led] > phase) {
        const led_t *l = &leds[led];
        gpio_set_direction(cp_pin[l->anode],   GPIO_MODE_OUTPUT);
        gpio_set_direction(cp_pin[l->cathode], GPIO_MODE_OUTPUT);
        gpio_set_level(cp_pin[l->anode], 1);
        gpio_set_level(cp_pin[l->cathode], 0);
    }
    if (++led >= CP_NUM_LEDS) { led = 0; phase = (phase + 1) & 7; }
}

void cp_init(void)
{
    for (int i = 0; i < 6; i++) {
        gpio_reset_pin(cp_pin[i]);
        gpio_set_direction(cp_pin[i], GPIO_MODE_INPUT);
    }
    memset((void *)cp_frame, 0, sizeof cp_frame);

    const esp_timer_create_args_t t = {
        .callback = scan_cb, .name = "cpscan",
        .dispatch_method = ESP_TIMER_TASK,
    };
    esp_timer_handle_t h;
    esp_timer_create(&t, &h);
    esp_timer_start_periodic(h, 80);   // microseconds
}

void cp_clear(void) { memset((void *)cp_frame, 0, sizeof cp_frame); }

// Output column: D16..D24 are the nine LEDs beside the 0-9 labels on the
// right edge (verify label order against your board on first light-up and
// permute here if needed - this is the one mapping silk can't tell us).
void cp_set_outputs(const uint8_t conf[10])
{
    for (int i = 0; i < 9; i++)
        cp_frame[15 + i] = (uint8_t)((conf[i] * 8u) / 255u);
}
