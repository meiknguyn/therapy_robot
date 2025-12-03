"""Accelerometer calibration offsets - save your calibration values here.

These values were obtained from running calibrate_accelerometer.py.
They center the accelerometer readings around 0.0 when still.
"""

# Calibration offsets from calibrate_accelerometer.py
# These values center the accelerometer readings around 0.0 when still
ACCEL_X_OFFSET = 0.314
ACCEL_Y_OFFSET = 0.442
ACCEL_Z_OFFSET = 0.469

# Smoothing samples (higher = more smoothing, less noise, slower response)
# Recommended: 15 for noisy signals, 5-10 for cleaner signals
ACCEL_SMOOTHING_SAMPLES = 15

