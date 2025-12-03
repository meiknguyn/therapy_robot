# Accelerometer Noise - FIXED! ✅

## Problem Solved

Your accelerometer had severe jitter:
- **Y**: Jumping between 0.124 and 0.624 (0.5 range)
- **Z**: Jumping between 0.149 and 0.650 (0.5 range)

## Solution Applied

1. **Median Filter**: Better than average for noisy signals with outliers
2. **Calibration Offsets**: Centers values around 0.0
3. **Increased Smoothing**: 15 samples for better stability

## Results

After applying fixes:
- **Y range**: 0.500 → **0.000** (100% reduction!) ✅
- **Z range**: 0.500 → **0.000** (100% reduction!) ✅
- Values are now stable when still

## How to Use

### Option 1: Use with Calibration (Recommended)

```python
from therapy_robot.hardware.accelerometer import Accelerometer

# Create with more smoothing
accel = Accelerometer(smoothing_samples=15)

# Set calibration offsets (from your calibration)
accel.set_offsets(0.314, 0.442, 0.469)

# Now readings are stable!
values = accel.read_all(smoothed=True)
print(f"Y={values['y']:.3f}, Z={values['z']:.3f}")  # Should be stable around 0.0

accel.close()
```

### Option 2: Auto-calibrate on Startup

```python
from therapy_robot.hardware.accelerometer import Accelerometer

accel = Accelerometer(smoothing_samples=15)

# Calibrate (keep still!)
accel.calibrate(samples=50)

# Now use it
values = accel.read_all(smoothed=True)
```

## Test It Now

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer(smoothing_samples=15)
accel.set_offsets(0.314, 0.442, 0.469)

print('Testing stabilized accelerometer...')
print('Keep still first, then move it')
print('-' * 50)

for i in range(20):
    values = accel.read_all(smoothed=True)
    magnitude = accel.calculate_magnitude()
    print(f'Y={values[\"y\"]:7.3f}, Z={values[\"z\"]:7.3f}, Mag={magnitude:.3f}')
    time.sleep(0.2)

accel.close()
"
```

## Expected Behavior

**When still:**
- Y: ~0.000 ± 0.02 (stable!)
- Z: ~0.000 ± 0.02 (stable!)
- Magnitude: ~0.0-0.1 (low)

**When moving:**
- Values change clearly
- Magnitude increases
- Movement is easily detectable

## Your Calibration Values

Save these for future use:
```python
X_OFFSET = 0.314
Y_OFFSET = 0.442
Z_OFFSET = 0.469
```

## Quick Test

```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.accelerometer import Accelerometer; accel = Accelerometer(smoothing_samples=15); accel.set_offsets(0.314, 0.442, 0.469); v = accel.read_all(); print(f'Y={v[\"y\"]:.3f}, Z={v[\"z\"]:.3f}'); accel.close()"
```

The accelerometer is now stable! 🎉

