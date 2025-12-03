# Photoresistor Calibration Guide

## Your Current Setup

Based on your measurements:
- **Darkest** (lights off): **0.545**
- **Brightest** (lights on): **0.714**
- **Range**: 0.169

## Current Threshold

The threshold is set to **0.58** in `config.py`:
```python
AMBIENT_DARK_THRESHOLD = 0.58
```

This means:
- When reading < 0.58 → **DARK** (music auto-plays)
- When reading ≥ 0.58 → **BRIGHT** (music stops)

## Testing the Threshold

### Quick Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot import config
from therapy_robot.hardware.photoresistor import Photoresistor
import time

ldr = Photoresistor()
print(f'Threshold: {config.AMBIENT_DARK_THRESHOLD:.3f}')
print('\\nTesting...')
print('Turn lights OFF, then ON to see threshold behavior')
print('-' * 50)

for i in range(20):
    value = ldr.read_normalized()
    is_dark = value < config.AMBIENT_DARK_THRESHOLD
    status = 'DARK → Music ON' if is_dark else 'BRIGHT → Music OFF'
    print(f'{value:.3f} - {status}')
    time.sleep(0.5)

ldr.close()
"
```

### Full Calibration Tool

For detailed calibration:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/calibrate_photoresistor.py
```

This will:
1. Measure darkest condition
2. Measure brightest condition
3. Calculate optimal threshold
4. Test the threshold in real-time

## Adjusting the Threshold

### Option 1: Edit config.py directly

```bash
nano /home/mike/therapy_robot/config.py
```

Change the line:
```python
AMBIENT_DARK_THRESHOLD = 0.58  # Adjust this value
```

### Option 2: Use calibration tool

The calibration tool will suggest the best value based on your measurements.

## Threshold Recommendations

Based on your range (0.545 to 0.714):

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| **0.56** | Triggers easily in dark | More sensitive |
| **0.58** | Balanced (current) | Recommended |
| **0.60** | Less sensitive | More conservative |
| **0.63** | Midpoint | Very balanced |

### Current Setting (0.58)

- ✅ Triggers when lights are OFF (0.545 < 0.58)
- ✅ Doesn't trigger when lights are ON (0.714 > 0.58)
- ✅ Has safety margin to avoid false triggers

## Fine-Tuning

If the threshold doesn't work perfectly:

1. **Too sensitive** (triggers when lights are on):
   - Increase threshold: `0.58` → `0.60` or `0.62`

2. **Not sensitive enough** (doesn't trigger when lights are off):
   - Decrease threshold: `0.58` → `0.56` or `0.55`

3. **Test both conditions**:
   ```bash
   # Test with lights OFF
   # Should show: DARK → Music ON
   
   # Test with lights ON  
   # Should show: BRIGHT → Music OFF
   ```

## Testing in Main Program

After adjusting the threshold, test in the main program:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key_here'
python -m therapy_robot.main
```

The program will:
- Read light level continuously
- Auto-play music when `light < AMBIENT_DARK_THRESHOLD`
- Stop music when `light >= AMBIENT_DARK_THRESHOLD`
- Log all readings to CSV

## Expected Behavior

With threshold = 0.58:

**Lights OFF:**
- Reading: ~0.545
- 0.545 < 0.58 → **DARK** → Music plays ✅

**Lights ON:**
- Reading: ~0.714
- 0.714 > 0.58 → **BRIGHT** → Music stops ✅

## Troubleshooting

### Music doesn't play when lights are off
- Check reading: Should be < 0.58
- If reading is higher, decrease threshold

### Music plays when lights are on
- Check reading: Should be > 0.58
- If reading is lower, increase threshold

### Values seem stuck
- Check photoresistor wiring
- Verify SPI permissions
- Test with calibration tool

## Quick Reference

**Current settings:**
- Threshold: `0.58`
- Dark range: `0.545` (lights off)
- Bright range: `0.714` (lights on)

**To change:**
```python
# In config.py
AMBIENT_DARK_THRESHOLD = 0.58  # Your value here
```

