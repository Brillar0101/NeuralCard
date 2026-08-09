#include "lsm6ds3.h"
#include "board.h"
#include "driver/i2c_master.h"
#include "esp_log.h"

#define REG_WHO_AM_I  0x0F
#define REG_CTRL1_XL  0x10
#define REG_CTRL2_G   0x11
#define REG_STATUS    0x1E
#define REG_OUTX_L_G  0x22

static const char *TAG = "lsm6ds3";
static i2c_master_dev_handle_t dev;

static bool wr(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = { reg, val };
    return i2c_master_transmit(dev, b, 2, 100) == ESP_OK;
}

static bool rd(uint8_t reg, uint8_t *buf, size_t len)
{
    return i2c_master_transmit_receive(dev, &reg, 1, buf, len, 100) == ESP_OK;
}

bool imu_init(void)
{
    i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_PORT,
        .sda_io_num = PIN_SDA,
        .scl_io_num = PIN_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = false,  // R11/R12 4.7k on board
    };
    i2c_master_bus_handle_t bus;
    if (i2c_new_master_bus(&bus_cfg, &bus) != ESP_OK) return false;

    i2c_device_config_t dev_cfg = {
        .device_address = LSM6DS3_ADDR,
        .scl_speed_hz = 400000,
    };
    if (i2c_master_bus_add_device(bus, &dev_cfg, &dev) != ESP_OK) return false;

    uint8_t who = 0;
    if (!rd(REG_WHO_AM_I, &who, 1)) return false;
    ESP_LOGI(TAG, "WHO_AM_I = 0x%02X", who);
    if (who != 0x6A && who != 0x69) return false;   // TR-C / plain

    // 104 Hz, accel 4 g, gyro 245 dps - plenty for hand gestures.
    wr(REG_CTRL1_XL, 0x48);
    wr(REG_CTRL2_G,  0x40);
    return true;
}

bool imu_data_ready(void)
{
    uint8_t s = 0;
    return rd(REG_STATUS, &s, 1) && (s & 0x03);
}

bool imu_read(imu_sample_t *out)
{
    uint8_t b[12];
    if (!rd(REG_OUTX_L_G, b, 12)) return false;
    int16_t *w = (int16_t *)out;
    for (int i = 0; i < 6; i++)
        w[i] = (int16_t)(b[2 * i] | (b[2 * i + 1] << 8));
    return true;
}
