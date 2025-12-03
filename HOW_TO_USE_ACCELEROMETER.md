# How to Use the Accelerometer (Fixed Version)

## Quick Start

The accelerometer is now fixed with noise reduction! Use it like this:

### Basic Usage

```python
from therapy_robot.hardware.accelerometer import Accelerometer

# Create with auto-calibration (uses saved offsets)
accel = Accelerometer(smoothing_samples=15, auto_calibrate=True)

# Read values (stable, no jitter!)
values = accel.read_all(smoothed=True)
print(f"X={values['x']:.3f}, Y={values['y']:.3f}, Z={values['z']:.3f}")

accel.close()
```

### Manual Calibration

```python
from therapy_robot.hardware.accelerometer import Accelerometer

accel = Accelerometer(smoothing_samples=15)

# Set your calibration offsets
accel.set_offsets(0.314, 0.442, 0.469)

# Or calibrate automatically
accel.calibrate(samples=50)  # Keep still!

# Now use it
values = accel.read_all(smoothed=True)
```

## Your Calibration Values

Your accelerometer has been calibrated with:
- **X offset**: 0.314
- **Y offset**: 0.442
- **Z offset**: 0.469
- **Smoothing**: 15 samples

These are saved in `hardware/accelerometer_config.py` and loaded automatically when you use `auto_calibrate=True`.

## Test Commands

### Quick Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer(smoothing_samples=15, auto_calibrate=True)

print('Testing stabilized accelerometer...')
for i in range(10):
    values = accel.read_all(smoothed=True)
    magnitude = accel.calculate_magnitude()
    print(f'Y={values[\"y\"]:.3f}, Z={values[\"z\"]:7.3f}, Mag={magnitude:.3f}')
    time.sleep(0.2)

accel.close()
"
```

### Movement Detection

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer(smoothing_samples=15, auto_calibrate=True)

print('Movement Detection Test')
print('Keep still, then move it...')
print('-' * 50)

for i in range(20):
    is_moving = accel.detect_movement(threshold=0.1)
    magnitude = accel.calculate_magnitude()
    status = 'MOVING' if is_moving else 'STILL'
    print(f'Magnitude: {magnitude:.3f} - {status}')
    time.sleep(0.5)

accel.close()
"
```

## Expected Behavior

**When still:**
- Y: ~0.000 ± 0.02 (stable, no jitter!)
- Z: ~0.000 ± 0.02 (stable, no jitter!)
- Magnitude: ~0.0-0.1

**When moving:**
- Values change clearly
- Magnitude increases
- Easy to detect movement

## Adjusting Settings

### More Smoothing (less noise, slower response)
```python
accel = Accelerometer(smoothing_samples=20, auto_calibrate=True)
```

### Less Smoothing (faster response, more noise)
```python
accel = Accelerometer(smoothing_samples=5, auto_calibrate=True)
```

### Disable Smoothing (raw values)
```python
values = accel.read_all(smoothed=False)  # Raw, noisy values
```

## Troubleshooting

### Still seeing jitter?

1. Increase smoothing: `smoothing_samples=20`
2. Re-run calibration: `python therapy_robot/calibrate_accelerometer.py`
3. Check wiring connections

### Values not centered at 0.0?

- Make sure `auto_calibrate=True` or call `accel.set_offsets(0.314, 0.442, 0.469)`
- Re-calibrate if you moved the accelerometer

## Summary

✅ **Noise fixed** - Median filter eliminates jitter  
✅ **Calibrated** - Offsets center values at 0.0  
✅ **Stable** - Y and Z now stable when still  
✅ **Ready to use** - Just use `auto_calibrate=True`  

The accelerometer is now production-ready! 🎉

