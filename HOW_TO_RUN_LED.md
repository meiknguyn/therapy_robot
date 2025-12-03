# How to Run the LED Controller

## Quick Test

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python3 -c "
from therapy_robot.hardware.led_ctrl import LEDController
import time

led = LEDController()
print('LED ON')
led.on()
time.sleep(1)

print('LED OFF')
led.off()
time.sleep(1)

print('Breathing animation (5 seconds)')
led.breathing_start()
time.sleep(5)
led.breathing_stop()

led.close()
print('Done!')
"
```

## Run Full Project

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key_here'
python -m therapy_robot.main
```

The LED will:
- Start with breathing animation when robot starts
- Change brightness based on mood (0.0 to 1.0)
- Stop and turn off when robot shuts down

## API Reference

```python
from therapy_robot.hardware.led_ctrl import LEDController

led = LEDController()

# Turn LED fully on
led.on()

# Turn LED fully off
led.off()

# Set brightness (0.0 to 1.0)
led.set_brightness(0.5)  # 50% brightness

# Start breathing animation (fade in/out)
led.breathing_start()

# Stop breathing animation
led.breathing_stop()

# Clean up
led.close()
```

## Troubleshooting

If LED doesn't work:
1. Check permissions: `groups | grep gpio`
2. Check GPIO chip: `ls -l /dev/gpiochip2`
3. Check pin: `gpioinfo /dev/gpiochip2 | grep "line  12"`

