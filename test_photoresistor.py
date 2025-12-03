#!/usr/bin/env python3
"""Interactive Photoresistor Test Tool."""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot.hardware.photoresistor import Photoresistor

def main():
    print("=" * 60)
    print("Photoresistor (LDR) Test Tool")
    print("=" * 60)
    print("\nThis tool tests the photoresistor connected to MCP3208 ADC channel 5.")
    print("Values range from 0.0 (dark) to 1.0 (bright).")
    print("\nPress Ctrl+C to exit")
    print("=" * 60)
    
    try:
        ldr = Photoresistor()
        print("\n✓ Photoresistor initialized")
        
        while True:
            print("\nOptions:")
            print("1. Single reading")
            print("2. Continuous readings (5 seconds)")
            print("3. Monitor with light changes")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                value = ldr.read_normalized()
                print(f"\n  Current light level: {value:.3f}")
                if value < 0.3:
                    print("  → Environment: DARK (music will auto-play)")
                elif value < 0.7:
                    print("  → Environment: MODERATE")
                else:
                    print("  → Environment: BRIGHT")
            
            elif choice == '2':
                print("\n  Taking continuous readings (5 seconds)...")
                print("  " + "-" * 50)
                start_time = time.time()
                count = 0
                while time.time() - start_time < 5:
                    value = ldr.read_normalized()
                    count += 1
                    bar = "█" * int(value * 40)
                    print(f"  [{count:3d}] {value:.3f} {bar}")
                    time.sleep(0.2)
                print(f"\n  Total readings: {count}")
            
            elif choice == '3':
                print("\n  Monitoring light changes...")
                print("  Cover/uncover the photoresistor and watch the values change")
                print("  Press Enter to stop monitoring")
                print("  " + "-" * 50)
                
                import threading
                stop_monitoring = threading.Event()
                
                def monitor():
                    count = 0
                    while not stop_monitoring.is_set():
                        value = ldr.read_normalized()
                        count += 1
                        bar = "█" * int(value * 50)
                        status = "DARK" if value < 0.3 else "BRIGHT" if value > 0.7 else "MODERATE"
                        print(f"\r  [{count:4d}] {value:.3f} {bar:50s} {status}", end="", flush=True)
                        time.sleep(0.1)
                    print()  # New line after stopping
                
                monitor_thread = threading.Thread(target=monitor, daemon=True)
                monitor_thread.start()
                
                input()  # Wait for Enter
                stop_monitoring.set()
                monitor_thread.join(timeout=1)
                print("\n  Monitoring stopped")
            
            elif choice == '4':
                break
            else:
                print("  Invalid choice")
        
        ldr.close()
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

