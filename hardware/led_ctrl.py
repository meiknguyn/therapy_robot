"""LED controller using gpiod on BeagleY-AI (GPIO16, line offset 16, named GPIO12)."""

import time
import threading
import gpiod

from therapy_robot import config


class LEDController:
    """Controls a PWM LED on GPIO16 (line offset 16) using gpiod (BeagleY-AI compatible)."""
    
    def __init__(self):
        """Initialize the LED controller using gpiod."""
        self.chip = gpiod.Chip(config.GPIO_CHIP)  # /dev/gpiochip2
        
        # Configure line settings for output
        settings = gpiod.LineSettings()
        settings.direction = gpiod.line.Direction.OUTPUT
        # Try active_low=False first (can be changed if LED is inverted)
        settings.active_low = False
        
        # Request the line
        self.line_request = self.chip.request_lines(
            consumer="therapy_robot_led",
            config={config.LED_PIN: settings}
        )
        
        self._breathing_active = False
        self._breathing_thread = None
        self._breathing_stop_event = threading.Event()
        
        # Software PWM parameters
        self._pwm_frequency = 100  # Hz
        self._pwm_period = 1.0 / self._pwm_frequency
        self._current_brightness = 0.0
    
    def on(self):
        """Turn LED fully on."""
        self._breathing_stop_event.set()  # Stop breathing if active
        self._current_brightness = 1.0
        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.ACTIVE})
    
    def off(self):
        """Turn LED fully off."""
        self._breathing_stop_event.set()  # Stop breathing if active
        self._current_brightness = 0.0
        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
    
    def set_brightness(self, value: float):
        """
        Set LED brightness using software PWM.
        
        Args:
            value: Brightness value between 0.0 and 1.0 (clamped automatically)
        """
        # Stop breathing animation if active
        if self._breathing_active:
            self.breathing_stop()
        
        # Clamp value between 0.0 and 1.0
        clamped_value = max(0.0, min(1.0, value))
        self._current_brightness = clamped_value
        
        # Use software PWM for smooth brightness control
        if clamped_value == 0.0:
            self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
        elif clamped_value == 1.0:
            self.line_request.set_values({config.LED_PIN: gpiod.line.Value.ACTIVE})
        else:
            # Software PWM: turn on for a fraction of the period
            self._pwm_loop(clamped_value)
    
    def _pwm_loop(self, brightness: float, duration: float = 0.1):
        """
        Software PWM loop for a short duration.
        
        Args:
            brightness: Brightness level (0.0 to 1.0)
            duration: How long to maintain this brightness (seconds)
        """
        cycles = int(duration * self._pwm_frequency)
        on_time = brightness * self._pwm_period
        off_time = self._pwm_period - on_time
        
        for _ in range(cycles):
            if brightness > 0:
                self.line_request.set_values({config.LED_PIN: gpiod.line.Value.ACTIVE})
                time.sleep(on_time)
            if brightness < 1.0:
                self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
                time.sleep(off_time)
    
    def _breathing_animation(self):
        """Breathing animation thread - fades LED in and out continuously."""
        try:
            while not self._breathing_stop_event.is_set():
                # Fade in (0.0 to 1.0)
                for i in range(0, 101, 2):  # 0 to 100 in steps of 2
                    if self._breathing_stop_event.is_set():
                        break
                    brightness = i / 100.0
                    self._current_brightness = brightness
                    # Use software PWM for smooth fade
                    on_time = brightness * self._pwm_period
                    off_time = self._pwm_period - on_time
                    if brightness > 0:
                        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.ACTIVE})
                        time.sleep(on_time)
                    if brightness < 1.0:
                        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
                        time.sleep(off_time)
                
                # Fade out (1.0 to 0.0)
                for i in range(100, -1, -2):  # 100 to 0 in steps of 2
                    if self._breathing_stop_event.is_set():
                        break
                    brightness = i / 100.0
                    self._current_brightness = brightness
                    # Use software PWM for smooth fade
                    on_time = brightness * self._pwm_period
                    off_time = self._pwm_period - on_time
                    if brightness > 0:
                        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.ACTIVE})
                        time.sleep(on_time)
                    if brightness < 1.0:
                        self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
                        time.sleep(off_time)
        except Exception as e:
            print(f"Breathing animation error: {e}")
        finally:
            # Turn off LED when breathing stops
            try:
                self.line_request.set_values({config.LED_PIN: gpiod.line.Value.INACTIVE})
            except:
                pass
            self._current_brightness = 0.0
    
    def breathing_start(self):
        """Start breathing effect (fade in/out animation)."""
        if self._breathing_active:
            return  # Already breathing
        
        self._breathing_active = True
        self._breathing_stop_event.clear()
        self._breathing_thread = threading.Thread(
            target=self._breathing_animation,
            daemon=True
        )
        self._breathing_thread.start()
    
    def breathing_stop(self):
        """Stop breathing effect and turn off LED."""
        if not self._breathing_active:
            return
        
        self._breathing_active = False
        self._breathing_stop_event.set()
        
        # Wait for thread to finish (with timeout)
        if self._breathing_thread and self._breathing_thread.is_alive():
            self._breathing_thread.join(timeout=1.0)
        
        self.off()
    
    def close(self):
        """Clean up resources."""
        self.breathing_stop()
        self.off()
        self.line_request.release()
        self.chip.close()
