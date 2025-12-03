# LED Troubleshooting Guide

## Problem: LED Not Turning On/Off

If the LED doesn't physically turn on/off when running the code, try these steps:

## Step 1: Run Diagnostic Tool

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_led_diagnostic.py
```

This will:
- Test GPIO12 with both normal and inverted (active_low) settings
- Test other common GPIO pins
- Help you identify which pin actually controls your LED

## Step 2: Check Hardware

### Wiring Check:
1. **LED Anode** (long leg) → GPIO pin (via resistor)
2. **LED Cathode** (short leg) → GND
3. **Resistor** (220-330 ohms) between GPIO and LED anode

### Common Issues:
- LED wired backwards (swap anode/cathode)
- Missing or wrong resistor value
- Wrong GPIO pin
- LED is burned out (test with multimeter)

## Step 3: Test GPIO Pins Manually

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 << 'EOF'
import gpiod
import time

chip = gpiod.Chip('/dev/gpiochip2')

# Test GPIO12 (line offset 12)
print("Testing GPIO12 (line 12)...")
settings = gpiod.LineSettings()
settings.direction = gpiod.line.Direction.OUTPUT
line = chip.request_lines(consumer='test', config={12: settings})

line.set_values({12: gpiod.line.Value.ACTIVE})
print("LED should be ON now - is it?")
time.sleep(3)

line.set_values({12: gpiod.line.Value.INACTIVE})
print("LED should be OFF now - is it?")
time.sleep(1)

line.release()
chip.close()
EOF
```

## Step 4: Check Pin Mapping

On BeagleY-AI, there's a difference between:
- **Line Offset**: The number used in gpiod (0, 1, 2, ...)
- **GPIO Name**: The actual GPIO number (GPIO12, GPIO19, etc.)

Check the mapping:
```bash
python3 -c "
import gpiod
chip = gpiod.Chip('/dev/gpiochip2')
for i in range(20):
    try:
        info = chip.get_line_info(i)
        print(f'Line {i}: {info.name}')
    except:
        pass
chip.close()
"
```

## Step 5: Try Active Low (Inverted)

Some LEDs are wired with active_low logic. Try:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
import gpiod
import time

chip = gpiod.Chip('/dev/gpiochip2')
settings = gpiod.LineSettings()
settings.direction = gpiod.line.Direction.OUTPUT
settings.active_low = True  # Inverted

line = chip.request_lines(consumer='test', config={12: settings})
line.set_values({12: gpiod.line.Value.ACTIVE})
print('LED should be ON (inverted)')
time.sleep(2)
line.set_values({12: gpiod.line.Value.INACTIVE})
line.release()
chip.close()
"
```

## Step 6: Update Configuration

If you find the LED works on a different pin or with active_low=True:

### Option A: Different Pin
Edit `config.py`:
```python
LED_PIN = 16  # Change from 12 to the working pin
```

### Option B: Active Low
Edit `hardware/led_ctrl.py`:
```python
settings.active_low = True  # Change from False to True
```

## Step 7: Verify with Multimeter

If software tests pass but LED doesn't light:
1. Check voltage on GPIO pin with multimeter
2. Check LED with multimeter (diode test)
3. Verify resistor value
4. Check for loose connections

## Common Solutions

### Solution 1: Wrong Pin
- GPIO12 (line offset 12) might not be the correct pin
- Try GPIO16 (line offset 16) which is named "GPIO12"
- Run diagnostic tool to find correct pin

### Solution 2: Active Low
- LED might need inverted logic
- Set `settings.active_low = True` in `led_ctrl.py`

### Solution 3: Hardware Issue
- LED might be burned out
- Resistor might be wrong value
- Wiring might be incorrect

## Quick Test Commands

**Test current pin (GPIO12, line 12):**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "import gpiod; import time; chip = gpiod.Chip('/dev/gpiochip2'); s = gpiod.LineSettings(); s.direction = gpiod.line.Direction.OUTPUT; l = chip.request_lines(consumer='t', config={12: s}); l.set_values({12: gpiod.line.Value.ACTIVE}); time.sleep(2); l.set_values({12: gpiod.line.Value.INACTIVE}); l.release(); chip.close()"
```

**Test with active_low:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && python3 -c "import gpiod; import time; chip = gpiod.Chip('/dev/gpiochip2'); s = gpiod.LineSettings(); s.direction = gpiod.line.Direction.OUTPUT; s.active_low = True; l = chip.request_lines(consumer='t', config={12: s}); l.set_values({12: gpiod.line.Value.ACTIVE}); time.sleep(2); l.set_values({12: gpiod.line.Value.INACTIVE}); l.release(); chip.close()"
```

## Still Not Working?

1. Verify LED works: Connect directly to 3.3V (with resistor) - should light up
2. Check GPIO permissions: `groups | grep gpio`
3. Check chip exists: `ls -l /dev/gpiochip2`
4. Try different GPIO chip: `/dev/gpiochip0` or `/dev/gpiochip1`

