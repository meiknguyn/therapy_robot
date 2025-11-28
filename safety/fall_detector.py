# safety/fall_detector.py
"""
Fall Detector Module
Uses accelerometer (ADC channels 2, 3, 7) from Assignment 3 to detect falls.
Triggers health alert when a fall is detected.
"""
import time
import threading
import math

try:
    import spidev
    HAVE_SPI = True
except ImportError:
    HAVE_SPI = False
    spidev = None

# ADC Configuration from Assignment 3
ADC_ACC_X = 2  # Accelerometer X-axis on ADC channel 2
ADC_ACC_Y = 3  # Accelerometer Y-axis on ADC channel 3
ADC_ACC_Z = 7  # Accelerometer Z-axis on ADC channel 7
SPI_DEVICE = 0
SPI_CHIP_SELECT = 0
SPI_MAX_SPEED = 1000000  # 1 MHz
ADC_MAX_VALUE = 4095
ADC_CENTER = ADC_MAX_VALUE / 2.0

# Fall detection parameters
FALL_THRESHOLD = 2000  # Threshold for detecting sudden acceleration change
FALL_DURATION_MS = 100  # Minimum duration of impact (ms)
STABLE_DURATION_MS = 500  # Time after fall to confirm it's not just a shake
SAMPLING_INTERVAL_MS = 10  # Sampling interval (same as Assignment 3)


class FallDetector:
    """
    Fall detector using accelerometer readings.
    Monitors acceleration changes to detect falls and triggers health check.
    """

    def __init__(self, fall_callback=None, log_callback=None):
        """
        Initialize fall detector.
        
        Args:
            fall_callback: Function() called when a fall is detected
            log_callback: Optional callback function(event_type, details) for logging
        """
        self.fall_callback = fall_callback
        self.log_callback = log_callback
        self.spi = None
        self.running = False
        self.monitor_thread = None
        
        # Fall detection state
        self.last_accel = [0, 0, 0]  # Last acceleration readings
        self.fall_start_time = None
        self.is_falling = False
        
        if HAVE_SPI:
            try:
                self.spi = spidev.SpiDev()
                self.spi.open(SPI_DEVICE, SPI_CHIP_SELECT)
                self.spi.max_speed_hz = SPI_MAX_SPEED
                self.spi.mode = 0
                print("[FallDetector] Initialized on ADC channels 2 (X), 3 (Y), 7 (Z)")
            except Exception as e:
                print(f"[FallDetector] Failed to initialize SPI: {e}")
                self.spi = None
        else:
            print("[FallDetector] spidev not available, using software simulation")

    def _read_adc(self, channel):
        """Read raw ADC value from specified channel."""
        if self.spi is None:
            # Simulate normal readings (near center)
            import random
            return random.randint(int(ADC_CENTER - 500), int(ADC_CENTER + 500))
        
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
            print(f"[FallDetector] Error reading ADC channel {channel}: {e}")
            return -1

    def _calculate_magnitude(self, x, y, z):
        """Calculate acceleration magnitude from X, Y, Z components."""
        # Normalize to -1.0 to 1.0 range (centered at 0)
        x_norm = (x - ADC_CENTER) / ADC_CENTER
        y_norm = (y - ADC_CENTER) / ADC_CENTER
        z_norm = (z - ADC_CENTER) / ADC_CENTER
        
        # Calculate magnitude
        magnitude = math.sqrt(x_norm**2 + y_norm**2 + z_norm**2)
        return magnitude

    def _detect_fall(self, x, y, z):
        """
        Detect if a fall has occurred based on acceleration readings.
        
        Fall detection logic:
        1. Monitor acceleration magnitude
        2. Detect sudden change (impact)
        3. Verify sustained change (robot is down)
        """
        current_time = time.time() * 1000  # milliseconds
        
        # Calculate current acceleration magnitude
        magnitude = self._calculate_magnitude(x, y, z)
        
        # Calculate change from last reading
        if self.last_accel[0] != 0:  # Not first reading
            last_magnitude = self._calculate_magnitude(
                self.last_accel[0], self.last_accel[1], self.last_accel[2]
            )
            delta_magnitude = abs(magnitude - last_magnitude)
            
            # Check for sudden impact (large change in acceleration)
            if delta_magnitude > (FALL_THRESHOLD / ADC_CENTER):
                if not self.is_falling:
                    # Start of potential fall
                    self.fall_start_time = current_time
                    self.is_falling = True
                    print(f"[FallDetector] Potential fall detected (delta: {delta_magnitude:.3f})")
                else:
                    # Already in fall state, check duration
                    if self.fall_start_time and (current_time - self.fall_start_time) > FALL_DURATION_MS:
                        # Confirmed fall - sustained impact
                        if self.log_callback:
                            try:
                                self.log_callback("fall_detected", {
                                    "magnitude": magnitude,
                                    "delta": delta_magnitude,
                                    "x": x,
                                    "y": y,
                                    "z": z
                                })
                            except Exception as e:
                                print(f"[FallDetector] Error in log callback: {e}")
                        
                        if self.fall_callback:
                            try:
                                self.fall_callback()
                            except Exception as e:
                                print(f"[FallDetector] Error in fall callback: {e}")
                        
                        # Reset fall state after callback
                        self.is_falling = False
                        self.fall_start_time = None
                        return True
            else:
                # Acceleration is stable, reset fall state after stable period
                if self.is_falling:
                    if self.fall_start_time and (current_time - self.fall_start_time) > STABLE_DURATION_MS:
                        self.is_falling = False
                        self.fall_start_time = None
                        print("[FallDetector] False alarm - acceleration stabilized")
        
        # Update last readings
        self.last_accel = [x, y, z]
        return False

    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[FallDetector] Started monitoring accelerometer")

    def stop_monitoring(self):
        """Stop background monitoring thread."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        print("[FallDetector] Stopped monitoring")

    def _monitor_loop(self):
        """Background thread that continuously monitors accelerometer."""
        while self.running:
            try:
                # Read accelerometer values
                x = self._read_adc(ADC_ACC_X)
                y = self._read_adc(ADC_ACC_Y)
                z = self._read_adc(ADC_ACC_Z)
                
                if x >= 0 and y >= 0 and z >= 0:
                    # Detect fall
                    self._detect_fall(x, y, z)
                
                time.sleep(SAMPLING_INTERVAL_MS / 1000.0)  # Convert ms to seconds
            except Exception as e:
                print(f"[FallDetector] Error in monitor loop: {e}")
                time.sleep(0.1)

    def get_current_acceleration(self):
        """
        Get current acceleration readings (for testing/debugging).
        
        Returns:
            Tuple (x, y, z) of raw ADC values
        """
        x = self._read_adc(ADC_ACC_X)
        y = self._read_adc(ADC_ACC_Y)
        z = self._read_adc(ADC_ACC_Z)
        return (x, y, z)

    def cleanup(self):
        """Clean up resources."""
        self.stop_monitoring()
        if self.spi is not None:
            try:
                self.spi.close()
            except:
                pass
            self.spi = None

