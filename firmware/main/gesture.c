#include "gesture.h"
#include "lsm6ds3.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <stdlib.h>

#define MAX_SAMPLES   300     // ~3 s at 104 Hz
#define QUIET_MS      400     // this long below threshold = gesture over
#define START_THRESH  3000    // raw accel delta that counts as "moving"

static imu_sample_t buf[MAX_SAMPLES];

static int32_t motion_energy(const imu_sample_t *s, const imu_sample_t *prev)
{
    int32_t e = 0;
    e += abs(s->ax - prev->ax);
    e += abs(s->ay - prev->ay);
    e += abs(s->az - prev->az);
    return e;
}

void gesture_record_and_print(int label)
{
    imu_sample_t prev = {0}, cur;
    int n = 0, quiet = 0;

    printf("# waiting for motion... (write your digit)\n");

    // Arm: wait until motion exceeds threshold
    imu_read(&prev);
    for (;;) {
        while (!imu_data_ready()) vTaskDelay(1);
        imu_read(&cur);
        if (motion_energy(&cur, &prev) > START_THRESH) break;
        prev = cur;
    }

    // Record until it goes quiet
    buf[n++] = cur;
    while (n < MAX_SAMPLES) {
        while (!imu_data_ready()) vTaskDelay(1);
        prev = buf[n - 1];
        imu_read(&buf[n]);
        quiet = (motion_energy(&buf[n], &prev) < START_THRESH / 4)
                    ? quiet + 1 : 0;
        n++;
        if (quiet > QUIET_MS / 10) break;   // ~10 ms per sample at 104 Hz
    }

    printf("GESTURE,%d\n", label);
    for (int i = 0; i < n; i++)
        printf("%d,%d,%d,%d,%d,%d\n",
               buf[i].gx, buf[i].gy, buf[i].gz,
               buf[i].ax, buf[i].ay, buf[i].az);
    printf("END\n");
}
