"""Test script to determine joystick Y-axis thresholds for volume control."""

import sys
import time
from pathlib import Path

# Add project root to path if running as script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from therapy_robot import config
from therapy_robot.hardware.joystick import Joystick


def main():
    """Test joystick thresholds."""
    print("=" * 70)
    print("Joystick Y-Axis Threshold Test")
    print("=" * 70)
    print()
    print("This test will help determine the correct thresholds for volume control.")
    print()
    print("Instructions:")
    print("  1. Keep joystick in CENTER position for 5 seconds")
    print("  2. Push joystick UP and hold for 5 seconds")
    print("  3. Return to CENTER for 2 seconds")
    print("  4. Push joystick DOWN and hold for 5 seconds")
    print("  5. Return to CENTER")
    print()
    print("Press Ctrl+C to stop at any time")
    print()
    print("=" * 70)
    print()
    
    try:
        joystick = Joystick()
        print("✓ Joystick initialized")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize joystick: {e}")
        return
    
    # Statistics tracking
    all_values = []
    center_values = []
    up_values = []
    down_values = []
    
    current_zone = "UNKNOWN"
    zone_start_time = None
    
    print("Starting in 3 seconds...")
    time.sleep(3)
    print()
    print("=" * 70)
    print(f"{'Time':<8} {'Y Value':<10} {'Zone':<10} {'Min':<8} {'Max':<8} {'Avg':<8}")
    print("=" * 70)
    
    start_time = time.time()
    last_zone = None
    
    try:
        while True:
            y = joystick.read_y()
            all_values.append(y)
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Determine zone based on current thresholds
            center_pos = 0.62
            y_diff = y - center_pos
            
            if y < config.VOLUME_UP_THRESHOLD or y_diff < -0.1:
                zone = "UP"
                up_values.append(y)
            elif y > config.VOLUME_DOWN_THRESHOLD or y_diff > 0.1:
                zone = "DOWN"
                down_values.append(y)
            else:
                zone = "CENTER"
                center_values.append(y)
            
            # Track zone changes
            if zone != last_zone:
                if last_zone is not None:
                    duration = current_time - zone_start_time if zone_start_time else 0
                    print(f"\n  → Zone changed: {last_zone} → {zone} (held {duration:.1f}s)")
                zone_start_time = current_time
                last_zone = zone
            
            # Calculate stats for current zone
            if zone == "CENTER" and center_values:
                zone_min = min(center_values[-50:])  # Last 50 readings
                zone_max = max(center_values[-50:])
                zone_avg = sum(center_values[-50:]) / len(center_values[-50:])
            elif zone == "UP" and up_values:
                zone_min = min(up_values[-50:])
                zone_max = max(up_values[-50:])
                zone_avg = sum(up_values[-50:]) / len(up_values[-50:])
            elif zone == "DOWN" and down_values:
                zone_min = min(down_values[-50:])
                zone_max = max(down_values[-50:])
                zone_avg = sum(down_values[-50:]) / len(down_values[-50:])
            else:
                zone_min = zone_max = zone_avg = y
            
            # Display current reading
            print(f"\r{elapsed:7.1f}s  {y:9.3f}  {zone:9s}  {zone_min:7.3f}  {zone_max:7.3f}  {zone_avg:7.3f}", 
                  end="", flush=True)
            
            time.sleep(0.1)  # Read every 0.1 seconds
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Test Complete - Statistics Summary")
        print("=" * 70)
        print()
        
        if all_values:
            print(f"Overall Statistics:")
            print(f"  Total readings: {len(all_values)}")
            print(f"  Overall min: {min(all_values):.3f}")
            print(f"  Overall max: {max(all_values):.3f}")
            print(f"  Overall avg: {sum(all_values) / len(all_values):.3f}")
            print()
        
        if center_values:
            print(f"CENTER Zone Statistics:")
            print(f"  Readings: {len(center_values)}")
            print(f"  Min: {min(center_values):.3f}")
            print(f"  Max: {max(center_values):.3f}")
            print(f"  Avg: {sum(center_values) / len(center_values):.3f}")
            print()
        
        if up_values:
            print(f"UP Zone Statistics:")
            print(f"  Readings: {len(up_values)}")
            print(f"  Min: {min(up_values):.3f}")
            print(f"  Max: {max(up_values):.3f}")
            print(f"  Avg: {sum(up_values) / len(up_values):.3f}")
            print()
        
        if down_values:
            print(f"DOWN Zone Statistics:")
            print(f"  Readings: {len(down_values)}")
            print(f"  Min: {min(down_values):.3f}")
            print(f"  Max: {max(down_values):.3f}")
            print(f"  Avg: {sum(down_values) / len(down_values):.3f}")
            print()
        
        # Recommendations
        print("=" * 70)
        print("Recommended Thresholds:")
        print("=" * 70)
        
        if center_values and up_values and down_values:
            center_avg = sum(center_values) / len(center_values)
            up_max = max(up_values)
            down_min = min(down_values)
            
            # Calculate thresholds
            # UP threshold should be between center and up max
            up_threshold = (center_avg + up_max) / 2
            
            # DOWN threshold should be between center and down min
            down_threshold = (center_avg + down_min) / 2
            
            print(f"  Center position: ~{center_avg:.3f}")
            print(f"  UP zone range: {min(up_values):.3f} to {max(up_values):.3f}")
            print(f"  DOWN zone range: {min(down_values):.3f} to {max(down_values):.3f}")
            print()
            print(f"  Recommended VOLUME_UP_THRESHOLD: {up_threshold:.2f}")
            print(f"  Recommended VOLUME_DOWN_THRESHOLD: {down_threshold:.2f}")
            print()
            print("  Add these to config.py:")
            print(f"    VOLUME_UP_THRESHOLD = {up_threshold:.2f}")
            print(f"    VOLUME_DOWN_THRESHOLD = {down_threshold:.2f}")
        else:
            print("  Not enough data collected.")
            print("  Make sure to:")
            print("    - Keep joystick in center")
            print("    - Push joystick UP")
            print("    - Push joystick DOWN")
        
        print()
    
    finally:
        joystick.close()
        print("✓ Test complete")


if __name__ == "__main__":
    main()

