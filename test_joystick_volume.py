"""Test script for joystick Y-axis volume control."""

import sys
import time
from pathlib import Path

# Add project root to path if running as script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from therapy_robot.audio import speaker
from therapy_robot.hardware.joystick import Joystick


def main():
    """Test joystick volume control."""
    print("=" * 60)
    print("Testing Joystick Y-Axis Volume Control")
    print("=" * 60)
    print()
    
    # Initialize joystick
    try:
        joystick = Joystick()
        print("✓ Joystick initialized")
    except Exception as e:
        print(f"✗ Failed to initialize joystick: {e}")
        return
    
    from therapy_robot import config
    
    # Start playing a test sound (if available)
    print("\nNote: This test demonstrates step-based volume control.")
    print("      Push joystick UP (Y < 0.3) and hold for 0.5s to increase volume.")
    print("      Push joystick DOWN (Y > 0.7) and hold for 0.5s to decrease volume.")
    print("      Volume changes in 5% steps and persists when joystick returns to center.")
    print()
    print("=" * 60)
    print("Step-Based Volume Control")
    print("=" * 60)
    print(f"Step size: {int(config.VOLUME_STEP_SIZE * 100)}%")
    print(f"Hold time: {config.VOLUME_HOLD_TIME}s")
    print(f"Cooldown: {config.VOLUME_COOLDOWN}s")
    print(f"Up zone: Y < {config.VOLUME_UP_THRESHOLD}")
    print(f"Down zone: Y > {config.VOLUME_DOWN_THRESHOLD}")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        # Simulate the step-based volume control from main.py
        current_volume = 0.6
        speaker.set_volume(current_volume)
        
        hold_start_time = None
        hold_direction = None
        last_change_time = 0.0
        
        while True:
            # Read joystick Y
            y_position = joystick.read_y()
            current_time = time.time()
            
            # Check up zone
            if y_position < config.VOLUME_UP_THRESHOLD:
                if hold_direction != 'up':
                    hold_direction = 'up'
                    hold_start_time = current_time
                else:
                    hold_duration = current_time - hold_start_time
                    time_since_last_change = current_time - last_change_time
                    
                    if (hold_duration >= config.VOLUME_HOLD_TIME and 
                        time_since_last_change >= config.VOLUME_COOLDOWN):
                        new_volume = min(1.0, current_volume + config.VOLUME_STEP_SIZE)
                        if new_volume != current_volume:
                            current_volume = new_volume
                            speaker.set_volume(current_volume)
                            last_change_time = current_time
                            hold_start_time = current_time
            
            # Check down zone
            elif y_position > config.VOLUME_DOWN_THRESHOLD:
                if hold_direction != 'down':
                    hold_direction = 'down'
                    hold_start_time = current_time
                else:
                    hold_duration = current_time - hold_start_time
                    time_since_last_change = current_time - last_change_time
                    
                    if (hold_duration >= config.VOLUME_HOLD_TIME and 
                        time_since_last_change >= config.VOLUME_COOLDOWN):
                        new_volume = max(0.0, current_volume - config.VOLUME_STEP_SIZE)
                        if new_volume != current_volume:
                            current_volume = new_volume
                            speaker.set_volume(current_volume)
                            last_change_time = current_time
                            hold_start_time = current_time
            else:
                hold_direction = None
                hold_start_time = None
            
            # Display status
            volume_percent = int(current_volume * 100)
            bar_length = 50
            filled = int(current_volume * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            zone = "UP" if y_position < config.VOLUME_UP_THRESHOLD else "DOWN" if y_position > config.VOLUME_DOWN_THRESHOLD else "CENTER"
            hold_info = ""
            if hold_direction:
                hold_duration = current_time - (hold_start_time or current_time)
                hold_info = f" | Holding {hold_direction} for {hold_duration:.1f}s"
            
            print(f"\rY: {y_position:.3f} ({zone:6s}) -> Volume: {volume_percent:3d}% [{bar}]{hold_info}", end="", flush=True)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\nStopping test...")
    
    finally:
        joystick.close()
        print("✓ Test complete")


if __name__ == "__main__":
    main()

