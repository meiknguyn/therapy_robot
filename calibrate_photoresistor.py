#!/usr/bin/env python3
"""Photoresistor Calibration Tool - Find optimal threshold for your setup."""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot.hardware.photoresistor import Photoresistor
from therapy_robot import config

def main():
    print("=" * 60)
    print("Photoresistor Calibration Tool")
    print("=" * 60)
    print("\nThis tool helps you find the optimal threshold for your setup.")
    print("You'll measure the darkest and brightest conditions.")
    print("\nPress Ctrl+C to exit at any time")
    print("=" * 60)
    
    try:
        ldr = Photoresistor()
        print("\n✓ Photoresistor initialized")
        
        # Measure darkest condition
        print("\n" + "=" * 60)
        print("STEP 1: Measure DARKEST condition")
        print("=" * 60)
        print("Please turn OFF all lights or cover the photoresistor")
        input("Press Enter when ready to measure dark condition...")
        
        print("\nTaking 10 readings in dark condition...")
        dark_readings = []
        for i in range(10):
            value = ldr.read_normalized()
            dark_readings.append(value)
            print(f"  Reading {i+1}: {value:.3f}")
            time.sleep(0.2)
        
        dark_min = min(dark_readings)
        dark_max = max(dark_readings)
        dark_avg = sum(dark_readings) / len(dark_readings)
        
        print(f"\nDark condition results:")
        print(f"  Minimum: {dark_min:.3f}")
        print(f"  Maximum: {dark_max:.3f}")
        print(f"  Average: {dark_avg:.3f}")
        
        # Measure brightest condition
        print("\n" + "=" * 60)
        print("STEP 2: Measure BRIGHTEST condition")
        print("=" * 60)
        print("Please turn ON all lights or expose photoresistor to bright light")
        input("Press Enter when ready to measure bright condition...")
        
        print("\nTaking 10 readings in bright condition...")
        bright_readings = []
        for i in range(10):
            value = ldr.read_normalized()
            bright_readings.append(value)
            print(f"  Reading {i+1}: {value:.3f}")
            time.sleep(0.2)
        
        bright_min = min(bright_readings)
        bright_max = max(bright_readings)
        bright_avg = sum(bright_readings) / len(bright_readings)
        
        print(f"\nBright condition results:")
        print(f"  Minimum: {bright_min:.3f}")
        print(f"  Maximum: {bright_max:.3f}")
        print(f"  Average: {bright_avg:.3f}")
        
        # Calculate recommendations
        print("\n" + "=" * 60)
        print("CALIBRATION RESULTS")
        print("=" * 60)
        
        print(f"\nMeasured Range:")
        print(f"  Darkest:  {dark_avg:.3f} (range: {dark_min:.3f} - {dark_max:.3f})")
        print(f"  Brightest: {bright_avg:.3f} (range: {bright_min:.3f} - {bright_max:.3f})")
        print(f"  Total range: {bright_avg - dark_avg:.3f}")
        
        # Calculate threshold options
        midpoint = (dark_avg + bright_avg) / 2
        conservative = dark_avg + (bright_avg - dark_avg) * 0.2  # 20% above dark
        aggressive = dark_avg + (bright_avg - dark_avg) * 0.1   # 10% above dark
        
        print(f"\nRecommended Thresholds:")
        print(f"  Conservative (20% above dark): {conservative:.3f}")
        print(f"  Midpoint:                      {midpoint:.3f}")
        print(f"  Aggressive (10% above dark):   {aggressive:.3f}")
        print(f"\n  Current threshold:            {config.AMBIENT_DARK_THRESHOLD:.3f}")
        
        # Test the recommended threshold
        print("\n" + "=" * 60)
        print("TESTING RECOMMENDED THRESHOLD")
        print("=" * 60)
        
        test_threshold = conservative
        print(f"\nTesting threshold: {test_threshold:.3f}")
        print("Turn lights OFF, then ON to see if threshold works correctly")
        print("Press Enter to start test, Ctrl+C to skip...")
        input()
        
        print("\nMonitoring (10 seconds)...")
        print("Cover/uncover photoresistor to test threshold")
        print("-" * 60)
        
        for i in range(50):
            value = ldr.read_normalized()
            is_dark = value < test_threshold
            status = "DARK (music ON)" if is_dark else "BRIGHT (music OFF)"
            bar = "█" * int(value * 50)
            print(f"[{i+1:3d}] {value:.3f} {bar:50s} {status}")
            time.sleep(0.2)
        
        print("\n" + "=" * 60)
        print("CALIBRATION COMPLETE")
        print("=" * 60)
        print(f"\nRecommended threshold: {conservative:.3f}")
        print(f"\nTo update config.py, change:")
        print(f"  AMBIENT_DARK_THRESHOLD = {conservative:.3f}")
        print(f"\nOr use midpoint for balanced detection:")
        print(f"  AMBIENT_DARK_THRESHOLD = {midpoint:.3f}")
        
        ldr.close()
        
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

