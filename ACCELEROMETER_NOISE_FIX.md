# Accelerometer Noise Reduction Guide

## Problem

Your accelerometer shows jitter in Y and Z axes:
- **Y**: Jitters between 0.122 and 0.622
- **Z**: Jitters between 0.149 and 0.650
- **X**: Stable (good!)

This is caused by:
1. Electrical noise in ADC readings
2. No calibration (unknown rest position)
3. No filtering (raw readings are noisy)

## Solution

I've added two features to reduce noise:

### 1. Moving Average Filter (Smoothing)

The accelerometer now uses a moving average to reduce noise:
- Default: 5 samples averaged
- Configurable: `Accelerometer(smoothing_samples=10)` for more smoothing

### 2. Calibration

Calibration finds the "rest" position and centers values around 0.0:
- Run calibration when accelerometer is still
- Offsets are calculated and applied automatically

## How to Use

### Quick Test with Smoothing

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

# Use more smoothing for noisy readings
accel = Accelerometer(smoothing_samples=10)

print('Testing with smoothing (keep still)...')
for i in range(20):
    values = accel.read_all(smoothed=True)
    print(f'  Y={values[\"y\"]:.3f}, Z={values[\"z\"]:.3f}')
    time.sleep(0.1)

accel.close()
"
```

### Full Calibration (Recommended)

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/calibrate_accelerometer.py
```

This will:
1. Measure current noise level
2. Calibrate rest position (keep still!)
3. Test calibrated readings
4. Show noise reduction percentage

### Manual Calibration in Code

```python
from therapy_robot.hardware.accelerometer import Accelerometer

accel = Accelerometer(smoothing_samples=10)

# Calibrate (keep accelerometer still!)
accel.calibrate(samples=50)

# Now readings are centered around 0.0 when still
values = accel.read_all()
print(f"X={values['x']:.3f}, Y={values['y']:.3f}, Z={values['z']:.3f}")

accel.close()
```

## Expected Results

### Before Calibration:
- Y: 0.122 to 0.622 (jittering)
- Z: 0.149 to 0.650 (jittering)
- Values jump around even when still

### After Calibration + Smoothing:
- Y: ~0.000 ± 0.02 (centered, stable)
- Z: ~0.000 ± 0.02 (centered, stable)
- Values stay near 0.0 when still
- Movement clearly visible when you tilt/move

## Adjusting Smoothing

If values are still too noisy:

**More smoothing (slower response, less noise):**
```python
accel = Accelerometer(smoothing_samples=20)  # More samples
```

**Less smoothing (faster response, more noise):**
```python
accel = Accelerometer(smoothing_samples=3)  # Fewer samples
```

## Testing After Calibration

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer(smoothing_samples=10)
accel.calibrate(samples=50)

print('\\nTesting calibrated readings (keep still)...')
for i in range(10):
    values = accel.read_all()
    magnitude = accel.calculate_magnitude()
    print(f'  Y={values[\"y\"]:7.3f}, Z={values[\"z\"]:7.3f}, Mag={magnitude:.3f}')
    time.sleep(0.2)

print('\\nNow move/tilt the accelerometer...')
for i in range(10):
    values = accel.read_all()
    magnitude = accel.calculate_magnitude()
    print(f'  Y={values[\"y\"]:7.3f}, Z={values[\"z\"]:7.3f}, Mag={magnitude:.3f}')
    time.sleep(0.2)

accel.close()
"
```

## Troubleshooting

### Still jittering after calibration?

1. **Increase smoothing:**
   ```python
   accel = Accelerometer(smoothing_samples=20)
   ```

2. **Check wiring:**
   - Verify connections to ADC channels 3 (Y) and 7 (Z)
   - Check for loose connections
   - Ensure proper grounding

3. **Electrical noise:**
   - Add capacitors near accelerometer
   - Use shielded cables
   - Keep wires away from power lines

### Values don't center at 0.0?

- Make sure accelerometer is completely still during calibration
- Increase calibration samples: `accel.calibrate(samples=100)`
- Re-run calibration if you move the accelerometer

### Too slow to respond?

- Reduce smoothing: `Accelerometer(smoothing_samples=3)`
- Or disable smoothing: `accel.read_all(smoothed=False)`

## Quick Reference

**Create with smoothing:**
```python
accel = Accelerometer(smoothing_samples=10)
```

**Calibrate:**
```python
accel.calibrate(samples=50)  # Keep still!
```

**Read values (with smoothing):**
```python
values = accel.read_all(smoothed=True)
```

**Read raw (no smoothing):**
```python
values = accel.read_all(smoothed=False)
```

## Next Steps

1. Run the calibration tool to reduce noise
2. Test with smoothing enabled
3. Adjust smoothing level if needed
4. Use calibrated values in your application

The accelerometer should now have much less jitter!

