// Minimal LSM6DS3TR-C driver: init, sample, motion-ready check.
#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int16_t gx, gy, gz;   // gyro, raw (245 dps full scale)
    int16_t ax, ay, az;   // accel, raw (4 g full scale)
} imu_sample_t;

bool imu_init(void);                    // true if WHO_AM_I answers
bool imu_read(imu_sample_t *s);         // one 6-axis sample
bool imu_data_ready(void);
