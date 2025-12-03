"""Test and calibrate accelerometer for fall detection."""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from therapy_robot.hardware.accelerometer import Accelerometer
from therapy_robot import config


def test_accelerometer_readings():
    """Test accelerometer readings and show statistics."""
    print("=" * 70)
    print("Accelerometer Test & Calibration Tool")
    print("=" * 70)
    print()
    print("This tool will help you understand accelerometer readings")
    print("and calibrate it for better fall detection.")
    print()
    
    try:
        accel = Accelerometer(smoothing_samples=5, auto_calibrate=False)
        print("✓ Accelerometer initialized")
        print()
    except Exception as e:
        print(f"✗ Error initializing accelerometer: {e}")
        return
    
    # Test 1: Raw readings (no smoothing)
    print("=" * 70)
    print("Test 1: Raw Readings (No Smoothing)")
    print("=" * 70)
    print("Keep the board STILL for 10 seconds...")
    print()
    time.sleep(2)
    
    raw_readings = []
    for i in range(100):  # 10 seconds at 0.1s intervals
        x = accel.read_x(smoothed=False)
        y = accel.read_y(smoothed=False)
        z = accel.read_z(smoothed=False)
        raw_readings.append((x, y, z))
        
        if i % 10 == 0:
            print(f"[{i+1:3d}/100] X={x:6.3f} Y={y:6.3f} Z={z:6.3f}")
        time.sleep(0.1)
    
    # Calculate statistics
    x_values = [r[0] for r in raw_readings]
    y_values = [r[1] for r in raw_readings]
    z_values = [r[2] for r in raw_readings]
    
    x_avg = sum(x_values) / len(x_values)
    y_avg = sum(y_values) / len(y_values)
    z_avg = sum(z_values) / len(z_values)
    
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    z_min, z_max = min(z_values), max(z_values)
    
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min
    
    print()
    print("Raw Readings Statistics (Board Still):")
    print("-" * 70)
    print(f"X-axis: avg={x_avg:6.3f} min={x_min:6.3f} max={x_max:6.3f} range={x_range:6.3f}")
    print(f"Y-axis: avg={y_avg:6.3f} min={y_min:6.3f} max={y_max:6.3f} range={y_range:6.3f}")
    print(f"Z-axis: avg={z_avg:6.3f} min={z_min:6.3f} max={z_max:6.3f} range={z_range:6.3f}")
    print()
    
    # Test 2: Smoothed readings
    print("=" * 70)
    print("Test 2: Smoothed Readings (With Filtering)")
    print("=" * 70)
    print("Keep the board STILL for 5 seconds...")
    print()
    time.sleep(2)
    
    smoothed_readings = []
    for i in range(50):  # 5 seconds at 0.1s intervals
        x = accel.read_x(smoothed=True)
        y = accel.read_y(smoothed=True)
        z = accel.read_z(smoothed=True)
        smoothed_readings.append((x, y, z))
        
        if i % 10 == 0:
            print(f"[{i+1:2d}/50] X={x:6.3f} Y={y:6.3f} Z={z:6.3f}")
        time.sleep(0.1)
    
    x_smooth = [r[0] for r in smoothed_readings]
    y_smooth = [r[1] for r in smoothed_readings]
    z_smooth = [r[2] for r in smoothed_readings]
    
    x_smooth_avg = sum(x_smooth) / len(x_smooth)
    y_smooth_avg = sum(y_smooth) / len(y_smooth)
    z_smooth_avg = sum(z_smooth) / len(z_smooth)
    
    x_smooth_range = max(x_smooth) - min(x_smooth)
    y_smooth_range = max(y_smooth) - min(y_smooth)
    z_smooth_range = max(z_smooth) - min(z_smooth)
    
    print()
    print("Smoothed Readings Statistics (Board Still):")
    print("-" * 70)
    print(f"X-axis: avg={x_smooth_avg:6.3f} range={x_smooth_range:6.3f}")
    print(f"Y-axis: avg={y_smooth_avg:6.3f} range={y_smooth_range:6.3f}")
    print(f"Z-axis: avg={z_smooth_avg:6.3f} range={z_smooth_range:6.3f}")
    print()
    
    # Test 3: Movement detection (automatic after delay)
    print("=" * 70)
    print("Test 3: Movement Detection Test")
    print("=" * 70)
    print("Starting movement test in 3 seconds...")
    print("Please DROP or SHAKE the board when you see 'NOW'")
    print()
    time.sleep(3)
    print("NOW - Drop or shake the board!")
    print()
    
    movement_readings = []
    for i in range(50):  # 5 seconds
        x = accel.read_x(smoothed=True)
        y = accel.read_y(smoothed=True)
        z = accel.read_z(smoothed=True)
        z_abs = abs(z)
        magnitude = (x**2 + y**2 + z**2)**0.5
        movement_readings.append((x, y, z, z_abs, magnitude))
        
        if i % 5 == 0:
            print(f"[{i+1:2d}/50] X={x:6.3f} Y={y:6.3f} Z={z:6.3f} Z_abs={z_abs:6.3f} Mag={magnitude:6.3f}")
        time.sleep(0.1)
    
    # Calculate movement statistics
    z_movement = [r[2] for r in movement_readings]
    z_abs_movement = [r[3] for r in movement_readings]
    z_movement_min = min(z_movement)
    z_movement_max = max(z_movement)
    z_movement_range = z_movement_max - z_movement_min
    
    z_abs_min = min(z_abs_movement)
    z_abs_max = max(z_abs_movement)
    z_abs_range = z_abs_max - z_abs_min
    
    magnitudes = [r[4] for r in movement_readings]
    mag_min = min(magnitudes)
    mag_max = max(magnitudes)
    mag_range = mag_max - mag_min
    
    print()
    print("Movement Test Statistics:")
    print("-" * 70)
    print(f"Z-axis during movement: min={z_movement_min:6.3f} max={z_movement_max:6.3f} range={z_movement_range:6.3f}")
    print(f"Z_abs during movement: min={z_abs_min:6.3f} max={z_abs_max:6.3f} range={z_abs_range:6.3f}")
    print(f"Magnitude during movement: min={mag_min:6.3f} max={mag_max:6.3f} range={mag_range:6.3f}")
    print()
    
    # Recommendations
    print("=" * 70)
    print("Calibration Recommendations")
    print("=" * 70)
    print()
    print("Based on your readings:")
    print()
    
    # Z-axis analysis
    z_still_avg = z_smooth_avg
    z_still_range = z_smooth_range
    z_still_min = min(z_smooth)
    z_still_max = max(z_smooth)
    
    print(f"Z-axis Analysis (for fall detection):")
    print(f"  - Still position average: {z_still_avg:.3f}")
    print(f"  - Still position range: {z_still_range:.3f} ({z_still_min:.3f} to {z_still_max:.3f})")
    print(f"  - Movement range: {z_movement_range:.3f}")
    print()
    
    # Calculate recommended thresholds based on actual data
    # Z-axis has significant jitter - need to account for this
    
    # Find the two main Z values (seems to jump between two states)
    z_unique = sorted(set([round(z, 2) for z in z_smooth]))
    if len(z_unique) >= 2:
        z_low = z_unique[0]
        z_high = z_unique[-1]
        z_jump_size = z_high - z_low
        print(f"  - Z-axis appears to jump between: {z_low:.3f} and {z_high:.3f} (jump size: {z_jump_size:.3f})")
        print()
    
    # Normal range: cover both jitter states
    z_normal_min = max(0.0, min(z_smooth) - 0.05)
    z_normal_max = min(1.0, max(z_smooth) + 0.05)
    
    # Free-fall threshold (below normal range)
    z_free_fall = max(0.0, z_normal_min - 0.1)
    
    # Impact threshold (above normal range) 
    z_impact = min(1.0, z_normal_max + 0.15)
    
    # Change threshold: needs to be larger than the jitter jump
    # If Z jumps between two states, change threshold should detect rapid switching
    if z_still_range > 0.3:
        # Large jitter - use pattern detection instead
        z_change = z_still_range * 0.8  # Detect when jumping between states rapidly
        print("⚠️  WARNING: Z-axis has large jitter!")
        print(f"   Consider using pattern detection (rapid state changes)")
        print()
    else:
        # Normal jitter - use standard change detection
        z_change = max(0.2, z_still_range * 1.5)
    
    print("Recommended Z-axis thresholds:")
    print(f"  - Normal range: {z_normal_min:.3f} to {z_normal_max:.3f}")
    print(f"  - Free-fall threshold: < {z_free_fall:.3f}")
    print(f"  - Impact threshold: > {z_impact:.3f}")
    print(f"  - Change threshold: > {z_change:.3f}")
    print()
    
    # Show current config values
    print("Current safety.py settings:")
    print(f"  - free_fall_threshold: 0.3")
    print(f"  - impact_threshold: 0.8")
    print(f"  - z_change_threshold: 0.2")
    print(f"  - normal_range: 0.1 to 0.7")
    print()
    
    # Calibration offsets
    print("=" * 70)
    print("Calibration Offsets")
    print("=" * 70)
    print()
    print("To center readings around zero when still:")
    print(f"  X offset: {x_smooth_avg:.3f}")
    print(f"  Y offset: {y_smooth_avg:.3f}")
    print(f"  Z offset: {z_smooth_avg:.3f}")
    print()
    print("You can apply these offsets using:")
    print(f"  accel.set_offsets({x_smooth_avg:.3f}, {y_smooth_avg:.3f}, {z_smooth_avg:.3f})")
    print()
    
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)
    
    accel.close()


if __name__ == "__main__":
    try:
        test_accelerometer_readings()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
