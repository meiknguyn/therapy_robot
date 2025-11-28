# hardware/led_ctrl.py
"""
LED Controller Module
Uses the same GPIO pin assignment from Assignment 3.
Supports brightness control and breathing animation.
"""
import time
import threading
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import config
    import simulation
except ImportError:
    # Fallback for different import styles
    from therapy_robot import config
    from therapy_robot import simulation

try:
    from gpiozero import PWMLED
    HAVE_GPIO = True
except ImportError:
    HAVE_GPIO = False
    PWMLED = None


class RealLEDController:
    """
    Real LED controller implementation using gpiozero.
    Uses PWM for smooth brightness transitions.
    """

    def __init__(self, led_pin=None):
        """
        Initialize LED controller.
        
        Args:
            led_pin: GPIO pin number for LED (uses config.LED_PIN if None)
        """
        self.led_pin = led_pin or config.LED_PIN
        self.breathing_active = False
        self.breathing_thread = None
        
        if HAVE_GPIO and self.led_pin is not None:
            try:
                self.led = PWMLED(self.led_pin)
                print(f"[LED] Initialized on GPIO pin {self.led_pin}")
            except Exception as e:
                print(f"[LED] Failed to initialize GPIO pin {self.led_pin}: {e}")
                self.led = None
        else:
            self.led = None
            if not HAVE_GPIO:
                print("[LED] gpiozero not available, falling back to simulation")

    def set_brightness(self, value: float):
        """
        Set LED brightness (0.0 to 1.0).
        
        Args:
            value: Brightness value between 0.0 (off) and 1.0 (full brightness)
        """
        value = max(0.0, min(1.0, value))
        if self.led is not None:
            try:
                self.led.value = value
            except Exception as e:
                print(f"[LED] Error setting brightness: {e}")
        else:
            print(f"[LED] brightness: {value:.2f}")

    def breathing(self, cycles=None, duration=None, min_brightness=None, max_brightness=None, stop_event=None):
        """
        Start breathing animation in a separate thread.
        
        Args:
            cycles: Number of breathing cycles (None = infinite)
            duration: Duration of one complete cycle (in/out) in seconds (uses config if None)
            min_brightness: Minimum brightness during breathing (uses config if None)
            max_brightness: Maximum brightness during breathing (uses config if None)
            stop_event: Threading Event to stop breathing (optional)
        """
        if duration is None:
            duration = config.LED_BREATH_PERIOD_SEC
        if min_brightness is None:
            min_brightness = config.LED_BREATH_MIN_BRIGHTNESS
        if max_brightness is None:
            max_brightness = config.LED_BREATH_MAX_BRIGHTNESS
            
        if self.breathing_active:
            self.stop_breathing()
        
        self.breathing_active = True
        if stop_event is None:
            stop_event = threading.Event()
        
        def breathing_loop():
            cycle_count = 0
            steps = 50  # Smoothness of animation
            
            while self.breathing_active and not stop_event.is_set():
                if cycles is not None and cycle_count >= cycles:
                    break
                
                # Breathe in (fade up)
                for i in range(steps + 1):
                    if not self.breathing_active or stop_event.is_set():
                        break
                    t = i / steps
                    brightness = min_brightness + (max_brightness - min_brightness) * (1 - (1 - t) ** 2)
                    self.set_brightness(brightness)
                    time.sleep(duration / (2 * steps))
                
                # Breathe out (fade down)
                for i in range(steps, -1, -1):
                    if not self.breathing_active or stop_event.is_set():
                        break
                    t = i / steps
                    brightness = min_brightness + (max_brightness - min_brightness) * (1 - t ** 2)
                    self.set_brightness(brightness)
                    time.sleep(duration / (2 * steps))
                
                cycle_count += 1
            
            self.breathing_active = False
            self.set_brightness(0.0)
        
        self.breathing_thread = threading.Thread(target=breathing_loop, daemon=True)
        self.breathing_thread.start()
        return stop_event

    def stop_breathing(self):
        """Stop breathing animation and turn off LED."""
        self.breathing_active = False
        if self.breathing_thread and self.breathing_thread.is_alive():
            time.sleep(0.1)  # Give thread a moment to check flag
        self.set_brightness(0.0)

    def cleanup(self):
        """Clean up resources."""
        self.stop_breathing()
        if self.led is not None:
            try:
                self.led.close()
            except:
                pass


# Export the appropriate LED controller based on simulation mode
if config.USE_SIMULATION:
    LEDController = simulation.SimulatedLED
    print("[LED] Using simulated LED controller")
else:
    LEDController = RealLEDController

