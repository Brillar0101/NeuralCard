// NeuralCard firmware - bring-up scaffold.
//
// On boot: LED self-test sweep, IMU check, then an idle "thinking" pattern.
// Serial commands (USB-C console, 115200-agnostic):
//   s        stream raw IMU samples as CSV until any key
//   0-9      record one labelled gesture (for the training set)
//   t        LED sweep test
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "charlieplex.h"
#include "lsm6ds3.h"
#include "gesture.h"
#include <stdio.h>
#include <math.h>

static bool imu_ok;

static void sweep(void)
{
    for (int i = 0; i < CP_NUM_LEDS; i++) {
        cp_clear();
        cp_frame[i] = 8;
        vTaskDelay(pdMS_TO_TICKS(60));
    }
    cp_clear();
}

// Idle animation: hidden-layer LEDs breathe softly.
static void idle_tick(int t)
{
    for (int i = 0; i < 15; i++) {
        float ph = (float)t / 30.0f + (float)i * 0.7f;
        cp_frame[i] = (uint8_t)(4.0f + 4.0f * sinf(ph));
    }
}

static void stream_imu(void)
{
    printf("# streaming - press any key to stop\n");
    printf("gx,gy,gz,ax,ay,az\n");
    imu_sample_t s;
    while (getchar() == EOF) {
        if (imu_data_ready() && imu_read(&s))
            printf("%d,%d,%d,%d,%d,%d\n", s.gx, s.gy, s.gz, s.ax, s.ay, s.az);
        vTaskDelay(1);
    }
}

void app_main(void)
{
    printf("\nNeuralCard v2.3 - firmware scaffold\n");

    cp_init();
    sweep();                       // proves every LED and the scan mapping

    imu_ok = imu_init();
    printf("IMU: %s\n", imu_ok ? "OK" : "NOT FOUND - check U2 soldering");

    int t = 0;
    for (;;) {
        int c = getchar();
        if (c == 's' && imu_ok) stream_imu();
        else if (c == 't') sweep();
        else if (c >= '0' && c <= '9' && imu_ok) {
            cp_clear();
            gesture_record_and_print(c - '0');
        }
        idle_tick(t++);
        vTaskDelay(pdMS_TO_TICKS(33));
    }
}
