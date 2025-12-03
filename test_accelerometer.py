#!/usr/bin/env python3
"""Interactive Accelerometer Test Tool."""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot.hardware.accelerometer import Accelerometer

def main():
    print("=" * 60)
    print("Accelerometer Test Tool")
    print("=" * 60)
    print("\nThis tool tests the accelerometer connected to MCP3208 ADC.")
    print("Channels: X=2, Y=3, Z=7")
    print("\nPress Ctrl+C to exit")
    print("=" * 60)
    
    try:
        accel = Accelerometer()
        print("\n✓ Accelerometer initialized")
        
        while True:
            print("\nOptions:")
            print("1. Single reading (all axes)")
            print("2. Continuous readings (5 seconds)")
            print("3. Monitor movement in real-time")
            print("4. Test movement detection")
            print("5. Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                values = accel.read_all()
                raw_values = accel.read_raw_all()
                magnitude = accel.calculate_magnitude()
                
                print(f"\n  Accelerometer Reading:")
                print(f"    X: {values['x']:.3f} (raw: {raw_values['x']})")
                print(f"    Y: {values['y']:.3f} (raw: {raw_values['y']})")
                print(f"    Z: {values['z']:.3f} (raw: {raw_values['z']})")
                print(f"    Magnitude: {magnitude:.3f}")
            
            elif choice == '2':
                print("\n  Taking continuous readings (5 seconds)...")
                print("  " + "-" * 56)
                print(f"  {'Time':<8} {'X':<8} {'Y':<8} {'Z':<8} {'Magnitude':<10}")
                print("  " + "-" * 56)
                
                start_time = time.time()
                count = 0
                while time.time() - start_time < 5:
                    values = accel.read_all()
                    magnitude = accel.calculate_magnitude()
                    count += 1
                    elapsed = time.time() - start_time
                    print(f"  {elapsed:6.2f}s {values['x']:7.3f} {values['y']:7.3f} {values['z']:7.3f} {magnitude:9.3f}")
                    time.sleep(0.2)
                print(f"\n  Total readings: {count}")
            
            elif choice == '3':
                print("\n  Monitoring accelerometer in real-time...")
                print("  Move/tilt the accelerometer and watch values change")
                print("  Press Enter to stop monitoring")
                print("  " + "-" * 56)
                print(f"  {'X':<8} {'Y':<8} {'Z':<8} {'Magnitude':<10} {'Status':<15}")
                print("  " + "-" * 56)
                
                import threading
                stop_monitoring = threading.Event()
                
                def monitor():
                    count = 0
                    while not stop_monitoring.is_set():
                        values = accel.read_all()
                        magnitude = accel.calculate_magnitude()
                        is_moving = magnitude > 0.1
                        status = "MOVING" if is_moving else "STATIONARY"
                        count += 1
                        print(f"\r  {values['x']:7.3f} {values['y']:7.3f} {values['z']:7.3f} {magnitude:9.3f} {status:15s}", end="", flush=True)
                        time.sleep(0.1)
                    print()  # New line after stopping
                
                monitor_thread = threading.Thread(target=monitor, daemon=True)
                monitor_thread.start()
                
                input()  # Wait for Enter
                stop_monitoring.set()
                monitor_thread.join(timeout=1)
                print("\n  Monitoring stopped")
            
            elif choice == '4':
                print("\n  Movement Detection Test")
                print("  Keep accelerometer still, then move it")
                print("  Press Enter to stop")
                print("  " + "-" * 56)
                
                threshold = 0.1
                try:
                    user_threshold = input(f"  Enter threshold (default {threshold}): ").strip()
                    if user_threshold:
                        threshold = float(user_threshold)
                except:
                    pass
                
                print(f"\n  Using threshold: {threshold}")
                print("  " + "-" * 56)
                
                import threading
                stop_monitoring = threading.Event()
                
                def monitor():
                    count = 0
                    movement_count = 0
                    while not stop_monitoring.is_set():
                        is_moving = accel.detect_movement(threshold)
                        magnitude = accel.calculate_magnitude()
                        count += 1
                        if is_moving:
                            movement_count += 1
                        status = "⚠ MOVING" if is_moving else "✓ STILL"
                        print(f"\r  [{count:4d}] Magnitude: {magnitude:.3f} - {status}", end="", flush=True)
                        time.sleep(0.1)
                    print()  # New line
                    print(f"\n  Total readings: {count}")
                    print(f"  Movement detected: {movement_count} times ({movement_count/count*100:.1f}%)")
                
                monitor_thread = threading.Thread(target=monitor, daemon=True)
                monitor_thread.start()
                
                input()  # Wait for Enter
                stop_monitoring.set()
                monitor_thread.join(timeout=1)
            
            elif choice == '5':
                break
            else:
                print("  Invalid choice")
        
        accel.close()
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

