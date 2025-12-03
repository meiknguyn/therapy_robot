# How to Test the Photoresistor (LDR)

## Quick Tests

### Test 1: Basic Reading Test

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.photoresistor import Photoresistor
import time

print('Testing Photoresistor...')
ldr = Photoresistor()
print('✓ Photoresistor initialized')

print('\\nTaking 5 readings...')
for i in range(5):
    value = ldr.read_normalized()
    print(f'  Reading {i+1}: {value:.3f} (0.0=dark, 1.0=bright)')
    time.sleep(0.5)

ldr.close()
print('\\n✓ Test complete!')
"
```

### Test 2: Continuous Monitoring

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.photoresistor import Photoresistor
import time

ldr = Photoresistor()
print('Monitoring light levels (10 seconds)...')
print('Cover/uncover the photoresistor to see values change')
print('-' * 50)

for i in range(50):
    value = ldr.read_normalized()
    bar = '█' * int(value * 40)
    status = 'DARK' if value < 0.3 else 'BRIGHT' if value > 0.7 else 'MODERATE'
    print(f'[{i+1:3d}] {value:.3f} {bar} {status}')
    time.sleep(0.2)

ldr.close()
print('\\n✓ Monitoring complete!')
"
```

### Test 3: Light/Dark Detection

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot.hardware.photoresistor import Photoresistor
import time

ldr = Photoresistor()
print('Testing light/dark detection...')
print('Cover the photoresistor (make it dark), then uncover it (make it bright)')
print('Press Ctrl+C to stop')
print('-' * 50)

try:
    while True:
        value = ldr.read_normalized()
        if value < 0.3:
            print(f'DARK: {value:.3f} (music would auto-play)')
        elif value > 0.7:
            print(f'BRIGHT: {value:.3f}')
        else:
            print(f'MODERATE: {value:.3f}')
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

ldr.close()
print('\\n✓ Test complete!')
"
```

### Test 4: Interactive Test Tool

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_photoresistor.py
```

This provides an interactive menu with options:
- Single reading
- Continuous readings
- Real-time monitoring with light changes

## Understanding the Values

### Value Range
- **0.0 - 0.3**: DARK (music auto-plays in main program)
- **0.3 - 0.7**: MODERATE light
- **0.7 - 1.0**: BRIGHT

### Expected Behavior
- **Cover photoresistor**: Value should decrease (toward 0.0)
- **Uncover/expose to light**: Value should increase (toward 1.0)
- **Normal room light**: Usually around 0.4-0.6

## Quick One-Liners

**Single reading:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.photoresistor import Photoresistor; ldr = Photoresistor(); print(f'Light: {ldr.read_normalized():.3f}'); ldr.close()"
```

**Watch values change:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "from therapy_robot.hardware.photoresistor import Photoresistor; import time; ldr = Photoresistor(); [print(f'{ldr.read_normalized():.3f}') or time.sleep(0.5) for _ in range(10)]; ldr.close()"
```

## Testing in Main Program

The photoresistor is automatically tested when you run the main program:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key_here'
python -m therapy_robot.main
```

The program will:
- Read ambient light continuously
- Auto-play music when dark (< 0.3)
- Log light readings to CSV

## Troubleshooting

### No readings / Always same value
1. Check SPI permissions: `ls -l /dev/spidev0.0`
2. Check if device exists: `ls -l /dev/spidev0.0`
3. Verify wiring to MCP3208 ADC channel 5

### Values don't change
1. Check photoresistor is exposed to light
2. Cover/uncover to test response
3. Verify photoresistor is connected to correct ADC channel (5)

### Permission denied
```bash
sudo chmod 666 /dev/spidev0.0
# Or add to spi group (if it exists)
```

### Test SPI directly
```bash
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000

# Read channel 5 (LDR)
channel = 5
cmd = [1, (8 + channel) << 4, 0]
response = spi.xfer2(cmd)
adc_value = ((response[1] & 0x0F) << 8) | response[2]
print(f'Raw ADC value: {adc_value} / 4095')
print(f'Normalized: {adc_value / 4095.0:.3f}')

spi.close()
"
```

## Expected Results

✅ **Working photoresistor:**
- Values change when covering/uncovering
- Values range from ~0.1 (very dark) to ~0.9 (very bright)
- Responds quickly to light changes
- Stable readings in same lighting conditions

❌ **Not working:**
- Always same value (stuck)
- No response to light changes
- Permission errors
- SPI device not found errors

## Integration Test

Test with the full system:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_project.py
```

This will test the photoresistor along with all other components.

