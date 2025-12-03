#!/usr/bin/env python3
"""LED Diagnostic Tool - Helps find the correct GPIO pin for the LED."""

import sys
from pathlib import Path
import gpiod
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot import config

def test_pin(chip, pin_offset, name, active_low=False):
    """Test a GPIO pin."""
    try:
        info = chip.get_line_info(pin_offset)
        print(f"\n{'='*60}")
        print(f"Testing Line Offset: {pin_offset}")
        print(f"  GPIO Name: {name}")
        print(f"  Line Name: {info.name}")
        print(f"  Active Low: {active_low}")
        print(f"  Current Consumer: {info.consumer}")
        print(f"  Used: {info.used}")
        
        settings = gpiod.LineSettings()
        settings.direction = gpiod.line.Direction.OUTPUT
        settings.active_low = active_low
        
        line = chip.request_lines(
            consumer=f"led_test_{pin_offset}",
            config={pin_offset: settings}
        )
        
        print(f"\n  → Setting to ACTIVE (should turn LED ON)...")
        line.set_values({pin_offset: gpiod.line.Value.ACTIVE})
        time.sleep(2)
        
        print(f"  → Setting to INACTIVE (should turn LED OFF)...")
        line.set_values({pin_offset: gpiod.line.Value.INACTIVE})
        time.sleep(1)
        
        print(f"  → Setting to ACTIVE again...")
        line.set_values({pin_offset: gpiod.line.Value.ACTIVE})
        time.sleep(2)
        
        print(f"  → Setting to INACTIVE...")
        line.set_values({pin_offset: gpiod.line.Value.INACTIVE})
        
        line.release()
        
        response = input(f"\n  ✓ Did GPIO{name} (line {pin_offset}) control the LED? (y/n): ").strip().lower()
        if response == 'y':
            return True, active_low
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False, False
    
    return False, False

def main():
    print("="*60)
    print("LED Diagnostic Tool")
    print("="*60)
    print("\nThis tool will test different GPIO pins to find your LED.")
    print("Watch the LED physically and answer 'y' when it turns on/off.")
    print("\nPress Ctrl+C to skip a pin or exit.")
    
    chip = gpiod.Chip(config.GPIO_CHIP)
    
    # Test GPIO12 (current config) with both active_low settings
    print("\n" + "="*60)
    print("Testing GPIO12 (current configuration)")
    print("="*60)
    
    # First try normal (active_low=False)
    found, active_low_setting = test_pin(chip, 12, "12", active_low=False)
    
    if not found:
        # Try inverted (active_low=True)
        print("\nTrying with active_low=True (inverted)...")
        found, active_low_setting = test_pin(chip, 12, "12", active_low=True)
    
    if not found:
        # Test other common pins
        print("\n" + "="*60)
        print("GPIO12 didn't work. Testing other pins...")
        print("="*60)
        
        # Common pins to test
        test_pins = [
            (16, "12"),  # GPIO16 is named GPIO12
            (13, "15"),
            (14, "14"),
            (15, "5"),
            (17, "6"),
            (18, "13"),
        ]
        
        for pin_offset, gpio_name in test_pins:
            found, active_low_setting = test_pin(chip, pin_offset, gpio_name, active_low=False)
            if found:
                print(f"\n✓ Found LED on line offset {pin_offset} (GPIO{gpio_name})!")
                print(f"  Active Low: {active_low_setting}")
                print(f"\nUpdate config.py:")
                print(f"  LED_PIN = {pin_offset}")
                break
            
            if not found:
                found, active_low_setting = test_pin(chip, pin_offset, gpio_name, active_low=True)
                if found:
                    print(f"\n✓ Found LED on line offset {pin_offset} (GPIO{gpio_name}) with active_low=True!")
                    print(f"\nUpdate config.py:")
                    print(f"  LED_PIN = {pin_offset}")
                    break
    
    chip.close()
    
    if found:
        print("\n" + "="*60)
        print("SUCCESS! LED found.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("LED not found. Check:")
        print("  1. LED wiring (anode to GPIO, cathode to GND via resistor)")
        print("  2. LED is connected to the correct pin")
        print("  3. Resistor value is correct (typically 220-330 ohms)")
        print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

