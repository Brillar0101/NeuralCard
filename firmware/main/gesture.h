// Gesture recorder: motion-triggered capture, CSV output over USB serial.
// This is how the training dataset gets built - air-write, save, repeat.
#pragma once

// Blocks until a gesture is captured, then prints it as CSV:
//   GESTURE,<label>
//   gx,gy,gz,ax,ay,az        (one line per sample, ~104 Hz)
//   END
void gesture_record_and_print(int label);
