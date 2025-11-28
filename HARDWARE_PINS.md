# Hardware Pin Assignments (Assignment 3)

This document lists the GPIO and ADC pin assignments used in this project, matching Assignment 3 configurations.

## ADC (MCP3208 via SPI)

**SPI Configuration:**
- Device: `/dev/spidev0.0`
- Mode: SPI_MODE_0
- Speed: 1 MHz
- Resolution: 12-bit (0-4095)

**Channel Assignments:**
- Channel 0: Joystick X-axis
- Channel 1: Joystick Y-axis  
- Channel 2: Accelerometer X (Assignment 3, not used in therapy robot)
- Channel 3: Accelerometer Y (Assignment 3, not used in therapy robot)
- Channel 4: **Photoresistor (LDR)** ← New for therapy robot
- Channel 7: Accelerometer Z (Assignment 3, not used in therapy robot)

## GPIO (Rotary Encoder)

**GPIO Chip:** `/dev/gpiochip2`

**Pin Assignments:**
- Line 15 (GPIO5, Pin 29): Rotary Encoder CLK (Clock)
- Line 17 (GPIO6, Pin 31): Rotary Encoder DT (Data)
- Line 18 (GPIO13, Pin 33): Rotary Encoder Button (not used in current implementation)

## LED

**GPIO Pin:** 26 (default, configurable)
- Common PWM-capable pin
- Can be changed in `main.py` if your Assignment 3 used a different pin

## Notes

- All pin assignments match Assignment 3 where applicable
- The LED pin (26) is a reasonable default but should be updated if your Assignment 3 used a different GPIO pin
- If hardware is not available, all modules provide software simulation mode

