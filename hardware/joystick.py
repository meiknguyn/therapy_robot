# hardware/joystick.py
"""
Joystick Module
Uses the same ADC pins from Assignment 3:
- ADC channel 0 for X-axis
- ADC channel 1 for Y-axis
"""
import time
import threading

try:
    import spidev
    HAVE_SPI = True
except ImportError:
    HAVE_SPI = False
    spidev = None

# ADC Configuration from Assignment 3
ADC_JOY_X = 0  # Joystick X-axis on ADC channel 0
ADC_JOY_Y = 1  # Joystick Y-axis on ADC channel 1
SPI_DEVICE = 0
SPI_CHIP_SELECT = 0
SPI_MAX_SPEED = 1000000  # 1 MHz
ADC_MAX_VALUE = 4095
ADC_CENTER = ADC_MAX_VALUE / 2.0

# Joystick tuning (from Assignment 3)
JOY_DEADZONE = 900  # Deadzone to prevent jitter
JOY_COOLDOWN_MS = 120  # Minimum time between actions


class Joystick:
    """
    Joystick controller using MCP3208 ADC via SPI.
    Same configuration as Assignment 3.
    """

    def __init__(self, volume_callback=None, track_callback=None, play_pause_callback=None, log_callback=None):
        """
        Initialize joystick reader.
        
        Args:
            volume_callback: Function(dir) called when joystick moved up/down
                            dir: +1 for up (increase), -1 for down (decrease)
            track_callback: Function(dir) called when joystick moved left/right
                           dir: +1 for right (next), -1 for left (previous)
            play_pause_callback: Function() called when joystick is pressed (center click)
            log_callback: Optional callback for logging events
        """
        self.volume_callback = volume_callback
        self.track_callback = track_callback
        self.play_pause_callback = play_pause_callback
        self.log_callback = log_callback
        self.spi = None
        self.running = False
        self.poll_thread = None
        
        if HAVE_SPI:
            try:
                self.spi = spidev.SpiDev()
                self.spi.open(SPI_DEVICE, SPI_CHIP_SELECT)
                self.spi.max_speed_hz = SPI_MAX_SPEED
                self.spi.mode = 0
                print("[Joystick] Initialized on ADC channels 0 (X) and 1 (Y)")
            except Exception as e:
                print(f"[Joystick] Failed to initialize SPI: {e}")
                self.spi = None
        else:
            print("[Joystick] spidev not available, using software simulation")

    def _read_adc(self, channel):
        """Read raw ADC value from specified channel."""
        if self.spi is None:
            import random
            return random.randint(0, ADC_MAX_VALUE)
        
        if channel < 0 or channel > 7:
            return -1
        
        try:
            tx = [
                0x06 | ((channel & 0x04) >> 2),
                (channel & 0x03) << 6,
                0x00
            ]
            rx = self.spi.xfer2(tx)
            value = ((rx[1] & 0x0F) << 8) | rx[2]
            return value
        except Exception as e:
            print(f"[Joystick] Error reading ADC channel {channel}: {e}")
            return -1

    def read_position(self):
        """
        Read current joystick position.
        
        Returns:
            Tuple (x, y) where values are normalized (-1.0 to 1.0)
            (0, 0) is center, positive X is right, positive Y is up
        """
        x_raw = self._read_adc(ADC_JOY_X)
        y_raw = self._read_adc(ADC_JOY_Y)
        
        if x_raw < 0 or y_raw < 0:
            return (0.0, 0.0)
        
        # Normalize to -1.0 to 1.0 range (centered at 0)
        x_norm = (x_raw - ADC_CENTER) / ADC_CENTER
        y_norm = (y_raw - ADC_CENTER) / ADC_CENTER
        
        # Clamp to [-1, 1]
        x_norm = max(-1.0, min(1.0, x_norm))
        y_norm = max(-1.0, min(1.0, y_norm))
        
        return (x_norm, y_norm)

    def start_polling(self):
        """Start background polling thread for joystick events."""
        if self.running:
            return
        
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def stop_polling(self):
        """Stop background polling thread."""
        self.running = False
        if self.poll_thread and self.poll_thread.is_alive():
            self.poll_thread.join(timeout=1.0)

    def _poll_loop(self):
        """Background thread that polls joystick and triggers callbacks."""
        last_vol_dir = 0  # -1 = down, 1 = up, 0 = center
        last_vol_time = 0
        
        while self.running:
            try:
                x_norm, y_norm = self.read_position()
                
                # Determine direction with deadzone
                dir_x = 0
                dir_y = 0
                
                # X-axis (left/right)
                if abs(x_norm) > (JOY_DEADZONE / ADC_CENTER):
                    dir_x = 1 if x_norm > 0 else -1
                
                # Y-axis (up/down)
                if abs(y_norm) > (JOY_DEADZONE / ADC_CENTER):
                    dir_y = 1 if y_norm > 0 else -1
                
                current_time = time.time() * 1000  # milliseconds
                
                # Volume control: Up/Down
                if dir_y != 0 and last_vol_dir == 0:
                    if current_time - last_vol_time > JOY_COOLDOWN_MS:
                        if self.volume_callback:
                            try:
                                self.volume_callback(dir_y)
                            except Exception as e:
                                print(f"[Joystick] Error in volume callback: {e}")
                        last_vol_time = current_time
                
                # Track control: Left/Right
                if dir_x != 0:
                    if current_time - last_vol_time > JOY_COOLDOWN_MS:
                        if self.track_callback:
                            try:
                                self.track_callback(dir_x)
                            except Exception as e:
                                print(f"[Joystick] Error in track callback: {e}")
                        last_vol_time = current_time
                
                # Play/Pause: Center press (check if very close to center)
                # Note: Actual button press might need separate GPIO reading
                # For now, we'll treat a quick return to center as a press
                if abs(x_norm) < 0.1 and abs(y_norm) < 0.1:
                    if last_vol_dir != 0:  # Just returned to center
                        if self.play_pause_callback:
                            try:
                                self.play_pause_callback()
                            except Exception as e:
                                print(f"[Joystick] Error in play/pause callback: {e}")
                        last_vol_time = current_time
                
                last_vol_dir = dir_y if dir_y != 0 else (0 if abs(y_norm) < 0.1 else last_vol_dir)
                
                time.sleep(0.01)  # 10ms polling (same as Assignment 3)
            except Exception as e:
                print(f"[Joystick] Error in poll loop: {e}")
                time.sleep(0.1)

    def cleanup(self):
        """Clean up resources."""
        self.stop_polling()
        if self.spi is not None:
            try:
                self.spi.close()
            except:
                pass
            self.spi = None

