#!/usr/bin/env python3
"""Accelerometer Calibration Tool - Find rest position and reduce noise."""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot.hardware.accelerometer import Accelerometer

def main():
    print("=" * 60)
    print("Accelerometer Calibration Tool")
    print("=" * 60)
    print("\nThis tool helps calibrate your accelerometer to reduce noise.")
    print("It will find the 'rest' position and calculate offsets.")
    print("\nIMPORTANT: Keep the accelerometer COMPLETELY STILL during calibration!")
    print("=" * 60)
    
    try:
        accel = Accelerometer(smoothing_samples=10)  # More smoothing for calibration
        
        print("\nStep 1: Measuring current noise level...")
        print("Taking 20 readings to see jitter...")
        print("-" * 60)
        
        x_values = []
        y_values = []
        z_values = []
        
        for i in range(20):
            raw_x = accel._read_adc_raw(2) / 4095.0
            raw_y = accel._read_adc_raw(3) / 4095.0
            raw_z = accel._read_adc_raw(7) / 4095.0
            
            x_values.append(raw_x)
            y_values.append(raw_y)
            z_values.append(raw_z)
            
            print(f"  [{i+1:2d}] X={raw_x:.3f}, Y={raw_y:.3f}, Z={raw_z:.3f}")
            time.sleep(0.1)
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        z_min, z_max = min(z_values), max(z_values)
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min
        
        print(f"\nNoise Analysis (before calibration):")
        print(f"  X: range = {x_range:.3f} ({x_min:.3f} to {x_max:.3f})")
        print(f"  Y: range = {y_range:.3f} ({y_min:.3f} to {y_max:.3f})")
        print(f"  Z: range = {z_range:.3f} ({z_min:.3f} to {z_max:.3f})")
        
        print("\n" + "=" * 60)
        print("Step 2: Calibration")
        print("=" * 60)
        input("\nPress Enter when accelerometer is STILL and ready for calibration...")
        
        # Perform calibration
        accel.calibrate(samples=50)
        
        print("\n" + "=" * 60)
        print("Step 3: Testing Calibration")
        print("=" * 60)
        print("\nTaking 20 readings with calibration and smoothing...")
        print("Keep accelerometer STILL...")
        print("-" * 60)
        
        # Clear history to start fresh
        accel.x_history.clear()
        accel.y_history.clear()
        accel.z_history.clear()
        
        calibrated_x = []
        calibrated_y = []
        calibrated_z = []
        
        for i in range(20):
            values = accel.read_all(smoothed=True)
            calibrated_x.append(values['x'])
            calibrated_y.append(values['y'])
            calibrated_z.append(values['z'])
            
            print(f"  [{i+1:2d}] X={values['x']:7.3f}, Y={values['y']:7.3f}, Z={values['z']:7.3f}")
            time.sleep(0.1)
        
        cal_x_min, cal_x_max = min(calibrated_x), max(calibrated_x)
        cal_y_min, cal_y_max = min(calibrated_y), max(calibrated_y)
        cal_z_min, cal_z_max = min(calibrated_z), max(calibrated_z)
        
        cal_x_range = cal_x_max - cal_x_min
        cal_y_range = cal_y_max - cal_y_min
        cal_z_range = cal_z_max - cal_z_min
        
        print(f"\nNoise Analysis (after calibration):")
        print(f"  X: range = {cal_x_range:.3f} ({cal_x_min:.3f} to {cal_x_max:.3f})")
        print(f"  Y: range = {cal_y_range:.3f} ({cal_y_min:.3f} to {cal_y_max:.3f})")
        print(f"  Z: range = {cal_z_range:.3f} ({cal_z_min:.3f} to {cal_z_max:.3f})")
        
        print("\n" + "=" * 60)
        print("Calibration Results")
        print("=" * 60)
        print(f"\nOffsets calculated:")
        print(f"  X offset: {accel.x_offset:.3f}")
        print(f"  Y offset: {accel.y_offset:.3f}")
        print(f"  Z offset: {accel.z_offset:.3f}")
        
        print(f"\nNoise reduction:")
        print(f"  X: {x_range:.3f} → {cal_x_range:.3f} ({((1 - cal_x_range/x_range) * 100):.1f}% reduction)")
        print(f"  Y: {y_range:.3f} → {cal_y_range:.3f} ({((1 - cal_y_range/y_range) * 100):.1f}% reduction)")
        print(f"  Z: {z_range:.3f} → {cal_z_range:.3f} ({((1 - cal_z_range/z_range) * 100):.1f}% reduction)")
        
        print("\n" + "=" * 60)
        print("Next Steps")
        print("=" * 60)
        print("\nTo use these offsets in your code, you can:")
        print("1. Call accel.calibrate() at startup")
        print("2. Or set manually: accel.set_offsets(x, y, z)")
        print(f"\nManual offsets:")
        print(f"  accel.set_offsets({accel.x_offset:.3f}, {accel.y_offset:.3f}, {accel.z_offset:.3f})")
        
        accel.close()
        
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

