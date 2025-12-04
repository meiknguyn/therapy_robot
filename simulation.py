# simulation.py
"""
Hardware simulation module for running therapy_robot without physical hardware.
Provides simulated implementations of all hardware components.
"""
import math
import time
import threading
import random
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Simulated LED
# ============================================================
class SimulatedLED:
    """
    Simulated LED controller that logs actions instead of controlling hardware.
    Implements the same interface as LEDController.
    """
    
    def __init__(self, led_pin=None):
        """Initialize simulated LED."""
        self.led_pin = led_pin
        self.current_brightness = 0.0
        self.breathing_active = False
        self.breathing_thread = None
        
        logger.info(f"[SIMULATION] Simulated LED initialized (pin {led_pin})")
    
    def set_brightness(self, value: float):
        """Set LED brightness (simulated)."""
        value = max(0.0, min(1.0, value))
        self.current_brightness = value
        logger.info(f"[SIMULATION] LED brightness set to {value:.2f}")
        print(f"[SIM] LED brightness: {value:.2f}")
    
    def breathing(self, cycles=None, duration=4.0, min_brightness=0.1, max_brightness=0.8, stop_event=None):
        """Start breathing animation (simulated)."""
        if self.breathing_active:
            self.stop_breathing()
        
        self.breathing_active = True
        if stop_event is None:
            stop_event = threading.Event()
        
        logger.info(f"[SIMULATION] LED breathing started (cycles={cycles}, duration={duration}s)")
        print(f"[SIM] LED breathing animation started")
        
        def breathing_loop():
            cycle_count = 0
            steps = 50
            
            while self.breathing_active and not stop_event.is_set():
                if cycles is not None and cycle_count >= cycles:
                    break
                
                # Simulate breathing cycle
                for i in range(steps + 1):
                    if not self.breathing_active or stop_event.is_set():
                        break
                    t = i / steps
                    brightness = min_brightness + (max_brightness - min_brightness) * (1 - (1 - t) ** 2)
                    self.set_brightness(brightness)
                    time.sleep(duration / (2 * steps))
                
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
        """Stop breathing animation."""
        self.breathing_active = False
        if self.breathing_thread and self.breathing_thread.is_alive():
            time.sleep(0.1)
        self.set_brightness(0.0)
        logger.info("[SIMULATION] LED breathing stopped")
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_breathing()


# ============================================================
# Simulated ADC Channel
# ============================================================
class SimulatedADCChannel:
    """
    Simulated ADC channel that returns reasonable fake values.
    """
    
    def __init__(self, channel, center_value=2047, noise_range=100, drift_range=50):
        """
        Initialize simulated ADC channel.
        
        Args:
            channel: Channel number (for logging)
            center_value: Center value around which readings fluctuate
            noise_range: Random noise range (±noise_range)
            drift_range: Slow drift range
        """
        self.channel = channel
        self.center_value = center_value
        self.noise_range = noise_range
        self.drift_range = drift_range
        self.time_offset = random.random() * 1000  # For deterministic-ish behavior
    
    def read(self):
        """Read simulated ADC value."""
        # Add some slow sine wave drift and noise
        drift = math.sin(time.time() / 10.0 + self.time_offset) * self.drift_range
        noise = random.randint(-self.noise_range, self.noise_range)
        value = int(self.center_value + drift + noise)
        # Clamp to valid ADC range
        return max(0, min(4095, value))


# ============================================================
# Simulated Photoresistor
# ============================================================
class SimulatedPhotoresistor:
    """
    Simulated photoresistor that returns normalized light readings.
    """
    
    def __init__(self, adc_channel=4, log_callback=None):
        """Initialize simulated photoresistor."""
        self.adc_channel = adc_channel
        self.log_callback = log_callback
        self.base_light = 0.6  # Simulate moderate lighting
        
        logger.info(f"[SIMULATION] Simulated Photoresistor initialized (channel {adc_channel})")
    
    def read_raw(self):
        """Read raw ADC value (simulated)."""
        # Simulate varying light levels
        variation = math.sin(time.time() / 30.0) * 0.1 + random.uniform(-0.05, 0.05)
        normalized = max(0.1, min(1.0, self.base_light + variation))
        raw = int(normalized * 4095)
        return raw
    
    def read_normalized(self):
        """Read normalized value (0.0-1.0)."""
        raw = self.read_raw()
        normalized = raw / 4095.0
        
        if self.log_callback:
            try:
                self.log_callback("ambient_light", {"value": normalized, "raw": raw})
            except Exception as e:
                logger.error(f"[SIMULATION] Error in log callback: {e}")
        
        return normalized
    
    def is_dark(self, threshold=0.3):
        """Check if environment is dark."""
        return self.read_normalized() < threshold
    
    def cleanup(self):
        """Clean up resources."""
        pass


# ============================================================
# Simulated Joystick
# ============================================================
class SimulatedJoystick:
    """
    Simulated joystick that uses simulated ADC channels.
    """
    
    def __init__(self, volume_callback=None, track_callback=None, play_pause_callback=None, log_callback=None):
        """Initialize simulated joystick."""
        self.volume_callback = volume_callback
        self.track_callback = track_callback
        self.play_pause_callback = play_pause_callback
        self.log_callback = log_callback
        self.running = False
        self.poll_thread = None
        
        # Simulated ADC channels (centered)
        self.adc_x = SimulatedADCChannel(0, center_value=2047)
        self.adc_y = SimulatedADCChannel(1, center_value=2047)
        
        logger.info("[SIMULATION] Simulated Joystick initialized")
        print("[SIM] Joystick initialized (simulation mode - controls won't work)")
    
    def read_position(self):
        """Read current joystick position (simulated, returns centered)."""
        x_raw = self.adc_x.read()
        y_raw = self.adc_y.read()
        
        # Normalize to -1.0 to 1.0 range
        x_norm = (x_raw - 2047) / 2047.0
        y_norm = (y_raw - 2047) / 2047.0
        
        return (x_norm, y_norm)
    
    def start_polling(self):
        """Start background polling (simulated - no actual polling)."""
        if self.running:
            return
        self.running = True
        logger.info("[SIMULATION] Joystick polling started (simulated - no input)")
        print("[SIM] Joystick polling active (simulation - no hardware input)")
    
    def stop_polling(self):
        """Stop background polling."""
        self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_polling()


# ============================================================
# Simulated Rotary Encoder
# ============================================================
class SimulatedRotaryEncoder:
    """
    Simulated rotary encoder that logs actions.
    """
    
    def __init__(self, value_change_callback=None, log_callback=None):
        """Initialize simulated rotary encoder."""
        self.value_change_callback = value_change_callback
        self.log_callback = log_callback
        self.running = False
        self.steps = 0
        
        logger.info("[SIMULATION] Simulated Rotary Encoder initialized")
        print("[SIM] Rotary Encoder initialized (simulation mode - no input)")
    
    def start_polling(self):
        """Start polling (simulated - no actual polling)."""
        if self.running:
            return
        self.running = True
        logger.info("[SIMULATION] Rotary encoder polling started (simulated)")
    
    def stop_polling(self):
        """Stop polling."""
        self.running = False
    
    def get_value(self):
        """Get accumulated step count (always 0 in simulation)."""
        return self.steps
    
    def reset(self):
        """Reset step count."""
        self.steps = 0
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_polling()


# ============================================================
# Simulated Fall Detector
# ============================================================
class SimulatedFallDetector:
    """
    Simulated fall detector that never detects falls (for safety).
    """
    
    def __init__(self, fall_callback=None, log_callback=None):
        """Initialize simulated fall detector."""
        self.fall_callback = fall_callback
        self.log_callback = log_callback
        self.running = False
        self.monitor_thread = None
        
        logger.info("[SIMULATION] Simulated Fall Detector initialized (no falls will be detected)")
        print("[SIM] Fall Detector initialized (simulation - no fall detection)")
    
    def start_monitoring(self):
        """Start monitoring (simulated - no actual monitoring)."""
        if self.running:
            return
        self.running = True
        logger.info("[SIMULATION] Fall detector monitoring started (simulated)")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
    
    def get_current_acceleration(self):
        """Get current acceleration (simulated, returns stable values)."""
        # Return stable, centered values (no fall)
        return (2047, 2047, 2047)
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_monitoring()

