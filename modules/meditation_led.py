# modules/meditation_led.py
import time

try:
    from gpiozero import PWMLED
    HAVE_GPIO = True
except ImportError:
    HAVE_GPIO = False
    PWMLED = None


class MeditationBreather:
    """
    LED breathing pattern for a short meditation / breathing exercise.
    If no hardware is available, it prints brightness values to console.
    """

    def __init__(self, led_pin=None, speak_callback=None):
        self.speak_callback = speak_callback

        if HAVE_GPIO and led_pin is not None:
            self.led = PWMLED(led_pin)
        else:
            self.led = None

    def _say(self, msg: str):
        if self.speak_callback:
            self.speak_callback(msg)
        else:
            print("[Meditation]", msg)

    def _set_brightness(self, value: float):
        value = max(0.0, min(1.0, value))
        if self.led is not None:
            self.led.value = value
        else:
            # No hardware: just print brightness so you can still demo on laptop
            print(f"[LED] brightness: {value:.2f}")

    def run_breathing_demo(self, cycles: int = 3, step_delay: float = 0.2):
        """
        One breathing cycle = fade in then fade out.
        cycles: how many times to repeat.
        step_delay: how fast the fade animation runs.
        """
        self._say("Starting a short breathing exercise. Breathe in as the light brightens, and out as it dims.")

        for c in range(cycles):
            # Breathe in: 0 → 1
            for level in range(0, 11):
                self._set_brightness(level / 10.0)
                time.sleep(step_delay)
            # Breathe out: 1 → 0
            for level in range(10, -1, -1):
                self._set_brightness(level / 10.0)
                time.sleep(step_delay)

        self._set_brightness(0.0)
        self._say("Breathing exercise complete. I hope you feel a bit calmer.")
