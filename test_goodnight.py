"""Test script for the goodnight feature."""

import sys
import time
from pathlib import Path

# Add project root to path if running as script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from therapy_robot import config
from therapy_robot.features.goodnight import GoodnightFeature
from therapy_robot.hardware.photoresistor import Photoresistor


def main():
    """Test the goodnight feature."""
    print("=" * 60)
    print("Testing Goodnight Feature")
    print("=" * 60)
    print()
    
    # Initialize photoresistor
    try:
        ldr = Photoresistor()
        print("✓ Photoresistor initialized")
    except Exception as e:
        print(f"✗ Failed to initialize photoresistor: {e}")
        return
    
    # Initialize goodnight feature
    try:
        goodnight = GoodnightFeature(
            music_volume=config.GOODNIGHT_MUSIC_VOLUME,
            check_interval=1.0  # Check every second for testing
        )
        print("✓ Goodnight feature initialized")
    except Exception as e:
        print(f"✗ Failed to initialize goodnight feature: {e}")
        ldr.close()
        return
    
    print()
    print("=" * 60)
    print("Testing Goodnight Feature")
    print("=" * 60)
    print()
    print("Instructions:")
    print("  1. Cover the photoresistor (make it dark)")
    print("  2. Music should start playing")
    print("  3. Uncover the photoresistor (make it bright)")
    print("  4. Music should stop")
    print()
    print("Press Ctrl+C to stop")
    print()
    print("-" * 60)
    
    try:
        while True:
            # Read light level
            light = ldr.read_normalized()
            
            # Update goodnight feature
            goodnight.update(light, force_check=True)
            
            # Display status
            status = goodnight.get_status()
            status_icon = "🌙" if status["is_active"] else "☀️"
            
            print(f"[{status_icon}] Light: {light:.3f} | "
                  f"Music: {'Playing' if status['is_active'] else 'Stopped'} | "
                  f"File: {status['current_music'] or 'None'}")
            
            time.sleep(1.0)
    
    except KeyboardInterrupt:
        print("\n\nStopping test...")
    
    finally:
        goodnight.stop()
        ldr.close()
        print("✓ Test complete")


if __name__ == "__main__":
    main()

