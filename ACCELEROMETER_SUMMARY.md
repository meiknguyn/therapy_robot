# Accelerometer - Complete Fix Summary

## Problem Identified

Your accelerometer had severe jitter:
- **Y axis**: Jumping between 0.124 and 0.624 (0.5 range)
- **Z axis**: Jumping between 0.149 and 0.650 (0.5 range)
- **X axis**: Stable (good!)

## Solutions Applied

### 1. Median Filter ✅
- Better than average for noisy signals with outliers
- Filters out the jumping values
- Uses median of last N samples

### 2. Calibration Offsets ✅
- Found rest position: X=0.314, Y=0.442, Z=0.469
- Centers values around 0.0 when still
- Saved in `hardware/accelerometer_config.py`

### 3. Increased Smoothing ✅
- Default: 15-20 samples
- More samples = more stable, slower response
- Configurable per your needs

## How to Use (Recommended)

### Simple Usage (Auto-calibrated)

```python
from therapy_robot.hardware.accelerometer import Accelerometer

# Auto-loads your calibration offsets
accel = Accelerometer(smoothing_samples=20, auto_calibrate=True)

# Read stable values
values = accel.read_all(smoothed=True)
print(f"Y={values['y']:.3f}, Z={values['z']:.3f}")  # Should be stable!

accel.close()
```

### Manual Calibration

```python
accel = Accelerometer(smoothing_samples=20)
accel.set_offsets(0.314, 0.442, 0.469)  # Your calibration values
values = accel.read_all(smoothed=True)
```

## Test Commands

### Quick Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer(smoothing_samples=20, auto_calibrate=True)
print('Testing stabilized accelerometer...')
for i in range(10):
    values = accel.read_all(smoothed=True)
    print(f'Y={values[\"y\"]:.3f}, Z={values[\"z\"]:7.3f}')
    time.sleep(0.2)
accel.close()
"
```

### Full Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_accelerometer.py
```

## Your Calibration Values

**Saved in:** `hardware/accelerometer_config.py`
- X offset: **0.314**
- Y offset: **0.442**
- Z offset: **0.469**
- Smoothing: **15 samples** (recommended: 20 for your noisy signal)

## Adjusting for Your Noise Level

If you still see some jitter:

**More smoothing (recommended for your setup):**
```python
accel = Accelerometer(smoothing_samples=25, auto_calibrate=True)
```

**Less smoothing (faster response):**
```python
accel = Accelerometer(smoothing_samples=10, auto_calibrate=True)
```

## Expected Results

**With smoothing=20 and calibration:**
- Y: Stable around 0.0 ± 0.05 (much better!)
- Z: Stable around 0.0 ± 0.05 (much better!)
- Clear movement detection when you tilt/move

## Files Created/Modified

1. ✅ `hardware/accelerometer.py` - Added median filter, calibration, smoothing
2. ✅ `hardware/accelerometer_config.py` - Your saved calibration values
3. ✅ `test_accelerometer.py` - Interactive test tool
4. ✅ `calibrate_accelerometer.py` - Calibration tool
5. ✅ `HOW_TO_TEST_ACCELEROMETER.md` - Testing guide
6. ✅ `ACCELEROMETER_NOISE_FIX.md` - Noise reduction guide
7. ✅ `HOW_TO_USE_ACCELEROMETER.md` - Usage guide

## Quick Reference

**Best settings for your accelerometer:**
```python
accel = Accelerometer(smoothing_samples=20, auto_calibrate=True)
```

**Your offsets:**
```python
accel.set_offsets(0.314, 0.442, 0.469)
```

The accelerometer is now much more stable! The median filter eliminates most of the jitter. 🎉

