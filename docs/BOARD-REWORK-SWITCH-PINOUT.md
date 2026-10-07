# NeuralCard switch pinout rework

## Finding

The reset and boot switches use XKB Connection TS-1187A-B-A-B (LCSC C318884).
The manufacturer drawing shows terminals A-B as one common contact and C-D as
the other; pressing the actuator closes the normally-open connection between
those two contact groups. See the [manufacturer's part page](https://www.helloxkb.com/Home/Goods/goodsInfoxq/id/1913)
and [LCSC datasheet](https://datasheet.lcsc.com/lcsc/2304140030_XKB-Connectivity-TS-1187A-B-A-B_C318884.pdf).

In v2.3.1 and the v3.0.0-dev board, the KiCad symbol/PCB assigned pads 1 and 3
to EN or IO0 and pads 2 and 4 to GND. The footprint places pads 1-2 in one row
and pads 3-4 in the other. This split each internally common row across signal
and GND, so both control lines were shorted to GND with the buttons released.
That matches the prototype's 0 V EN measurement, IO0-to-GND beep, and failure
to enumerate over USB. The 0.3 ohm reading is not conclusive on its own because
the meter leads measured about 0.4 ohm.

## Repair on an assembled v2.3.1 board

Disconnect USB and remove any battery before solder work. Do not try to flash
the board while the RESET switch is still holding EN low.

The lowest-risk temporary route is to have an electronics rework technician
remove the RST/SW2 switch. This should release EN. The BOOT/SW1 switch will
still hold IO0 low, which requests the ESP32-S3 ROM download mode at power-up;
if USB then enumerates, the firmware can be flashed. The BOOT switch must also
be removed or rewired before normal application startup and normal button use.

For a complete prototype repair, remove both switches and verify the old
signal-to-ground paths are open. Reinstall or wire each switch so both pads in
one internally common group go to the control signal and both pads in the other
group go to GND. On this footprint, pads 1-2 form one row and pads 3-4 the
other; which row gets signal depends on how the switch is rotated. An
experienced technician should inspect and isolate the existing copper before
adding jumpers; the v2.3.1 traces were routed for the incorrect pad grouping.
Do not bridge EN directly to 3V3 while the original switch short is present.

## Verification after prototype rework

1. With USB and battery disconnected, check that EN-GND and IO0-GND no longer
   read at the same level as shorted probe leads with both switches released.
2. Power over USB and measure EN to GND: it should be near 3.3 V released and
   near 0 V only while RST is pressed. IO0 should be near 3.3 V released and
   near 0 V only while BOOT is pressed.
3. Confirm that the host enumerates the ESP32-S3 USB Serial/JTAG device, then
   flash the intended firmware. If it still does not enumerate, continue with
   the USB D+/D- path and ESP32 power/reset checks.

## PCB correction for v3.0.1-dev

The revised design keeps each physical pad row on one net. SW1 (BOOT) assigns
pads 1-2 to IO0 and pads 3-4 to GND; SW2 (RESET) assigns pads 1-2 to GND and
pads 3-4 to EN, matching their existing copper orientation. The old vertical
signal bridges are removed. KiCad reports zero unconnected items and no
`shorting_items` entries, but the full DRC still has 410 violations and 191
schematic-parity issues, including two net conflicts and an EN/GND track
crossing; this is not proof that the whole board is short-free. ERC reports 42 missing project-library warnings in
the CLI environment. See [`drc/v3.0.1-dev-verification.md`](drc/v3.0.1-dev-verification.md)
and its attached full reports. The revision is not ready for fabrication.
This documentation does not change or replace the already released v2.3.1 tag.
