# How to Test the Accelerometer

## Quick Tests

### Test 1: Basic Reading Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

print('Testing Accelerometer...')
accel = Accelerometer()
print('✓ Accelerometer initialized')

print('\\nTaking 5 readings (move/tilt the accelerometer)...')
for i in range(5):
    values = accel.read_all()
    magnitude = accel.calculate_magnitude()
    print(f'  Reading {i+1}: X={values[\"x\"]:.3f}, Y={values[\"y\"]:.3f}, Z={values[\"z\"]:.3f}, Mag={magnitude:.3f}')
    time.sleep(0.5)

accel.close()
print('\\n✓ Test complete!')
"
```

### Test 2: Continuous Monitoring

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer()
print('Monitoring accelerometer (10 seconds)...')
print('Move/tilt the accelerometer to see values change')
print('-' * 60)
print(f'{'Time':<8} {'X':<8} {'Y':<8} {'Z':<8} {'Magnitude':<10}')
print('-' * 60)

for i in range(50):
    values = accel.read_all()
    magnitude = accel.calculate_magnitude()
    elapsed = i * 0.2
    print(f'{elapsed:6.2f}s {values[\"x\"]:7.3f} {values[\"y\"]:7.3f} {values[\"z\"]:7.3f} {magnitude:9.3f}')
    time.sleep(0.2)

accel.close()
print('\\n✓ Monitoring complete!')
"
```

### Test 3: Movement Detection

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer()
print('Movement Detection Test')
print('Keep accelerometer still, then move it')
print('Press Ctrl+C to stop')
print('-' * 50)

try:
    while True:
        is_moving = accel.detect_movement(threshold=0.1)
        magnitude = accel.calculate_magnitude()
        status = 'MOVING' if is_moving else 'STILL'
        print(f'Magnitude: {magnitude:.3f} - {status}')
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

accel.close()
print('\\n✓ Test complete!')
"
```

### Test 4: Interactive Test Tool

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_accelerometer.py
```

This provides an interactive menu with options:
- Single reading (all axes)
- Continuous readings (5 seconds)
- Real-time monitoring with movement detection
- Movement detection test with configurable threshold

## Understanding the Values

### Value Range
- **X, Y, Z axes**: 0.0 to 1.0 (normalized from ADC 0-4095)
- **Typical rest position**: ~0.5 (middle of range)
- **Movement**: Values change when accelerometer is tilted or moved

### Magnitude
- **Magnitude**: Calculated from all three axes
- **Still**: Low magnitude (~0.0-0.1)
- **Moving**: Higher magnitude (>0.1)

### Expected Behavior
- **Keep still**: Values should be relatively stable around ~0.5
- **Tilt X-axis**: X value changes, Y and Z relatively stable
- **Tilt Y-axis**: Y value changes, X and Z relatively stable
- **Tilt Z-axis**: Z value changes, X and Y relatively stable
- **Move/shake**: All values change, magnitude increases

## Quick One-Liners

**Single reading:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.accelerometer import Accelerometer; accel = Accelerometer(); v = accel.read_all(); print(f'X={v[\"x\"]:.3f}, Y={v[\"y\"]:.3f}, Z={v[\"z\"]:.3f}'); accel.close()"
```

**Watch values change:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.accelerometer import Accelerometer; import time; accel = Accelerometer(); [print(f'X={accel.read_x():.3f}, Y={accel.read_y():.3f}, Z={accel.read_z():.3f}') or time.sleep(0.5) for _ in range(10)]; accel.close()"
```

**Check if moving:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.accelerometer import Accelerometer; accel = Accelerometer(); print('MOVING' if accel.detect_movement() else 'STILL'); accel.close()"
```

## Testing Individual Axes

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.accelerometer import Accelerometer
import time

accel = Accelerometer()

print('Testing individual axes...')
print('Tilt the accelerometer in different directions')
print('-' * 50)

for i in range(20):
    x = accel.read_x()
    y = accel.read_y()
    z = accel.read_z()
    
    x_bar = '█' * int(x * 40)
    y_bar = '█' * int(y * 40)
    z_bar = '█' * int(z * 40)
    
    print(f'X: {x:.3f} {x_bar}')
    print(f'Y: {y:.3f} {y_bar}')
    print(f'Z: {z:.3f} {z_bar}')
    print()
    time.sleep(0.3)

accel.close()
"
```

## Troubleshooting

### No readings / Always same value
1. Check SPI permissions: `ls -l /dev/spidev0.0`
2. Check if device exists: `ls -l /dev/spidev0.0`
3. Verify wiring to MCP3208 ADC channels 2, 3, 7

### Values don't change
1. Check accelerometer is connected correctly
2. Move/tilt the accelerometer to test response
3. Verify accelerometer is connected to correct ADC channels (2=X, 3=Y, 7=Z)

### Permission denied
```bash
sudo chmod 666 /dev/spidev0.0
```

### Test ADC channels directly
```bash
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000

# Test channels 2, 3, 7
for channel in [2, 3, 7]:
    cmd = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(cmd)
    adc_value = ((response[1] & 0x0F) << 8) | response[2]
    print(f'Channel {channel}: {adc_value} / 4095 = {adc_value/4095.0:.3f}')

spi.close()
"
```

## Expected Results

✅ **Working accelerometer:**
- Values change when tilting/moving
- Values range from ~0.0 to ~1.0
- Responds quickly to movement
- Stable readings when still
- Magnitude increases with movement

❌ **Not working:**
- Always same value (stuck)
- No response to movement
- Permission errors
- SPI device not found errors

## Integration Test

Test with the full system:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_project.py
```

This will test the accelerometer along with all other components.

## ADC Channel Mapping

- **Channel 2**: X-axis (ADC_CHANNEL_ACCEL_X)
- **Channel 3**: Y-axis (ADC_CHANNEL_ACCEL_Y)
- **Channel 7**: Z-axis (ADC_CHANNEL_ACCEL_Z)

Make sure your accelerometer is wired to these MCP3208 ADC channels.

