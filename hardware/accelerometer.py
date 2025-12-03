"""Accelerometer reading via MCP3208 ADC on SPI."""

import spidev
import math
from collections import deque
import statistics

from therapy_robot import config

# Try to import calibration values if available
try:
    from therapy_robot.hardware import accelerometer_config
    DEFAULT_X_OFFSET = accelerometer_config.ACCEL_X_OFFSET
    DEFAULT_Y_OFFSET = accelerometer_config.ACCEL_Y_OFFSET
    DEFAULT_Z_OFFSET = accelerometer_config.ACCEL_Z_OFFSET
    DEFAULT_SMOOTHING = accelerometer_config.ACCEL_SMOOTHING_SAMPLES
except (ImportError, AttributeError):
    DEFAULT_X_OFFSET = 0.0
    DEFAULT_Y_OFFSET = 0.0
    DEFAULT_Z_OFFSET = 0.0
    DEFAULT_SMOOTHING = 5


class Accelerometer:
    """Reads accelerometer values from MCP3208 ADC (channels 2, 3, 7 for X, Y, Z)."""
    
    def __init__(self, smoothing_samples: int = None, auto_calibrate: bool = False):
        """
        Initialize SPI connection to MCP3208.
        
        Args:
            smoothing_samples: Number of samples to average for noise reduction 
                               (default: from config or 5)
            auto_calibrate: If True, automatically load saved calibration offsets (default: False)
        """
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # bus 0, device 0 (/dev/spidev0.0)
        self.spi.mode = config.SPI_MODE
        self.spi.max_speed_hz = config.SPI_MAX_SPEED
        
        # Noise filtering with moving average and median
        self.smoothing_samples = smoothing_samples if smoothing_samples is not None else DEFAULT_SMOOTHING
        self.x_history = deque(maxlen=self.smoothing_samples)
        self.y_history = deque(maxlen=self.smoothing_samples)
        self.z_history = deque(maxlen=self.smoothing_samples)
        
        # Use median filter for very noisy signals (better than mean for outliers)
        self.use_median_filter = True
        
        # Calibration offsets (load from config if available)
        if auto_calibrate:
            self.x_offset = DEFAULT_X_OFFSET
            self.y_offset = DEFAULT_Y_OFFSET
            self.z_offset = DEFAULT_Z_OFFSET
        else:
            self.x_offset = 0.0
            self.y_offset = 0.0
            self.z_offset = 0.0
    
    def _read_adc_raw(self, channel: int) -> int:
        """
        Read raw 12-bit value from MCP3208 ADC channel.
        
        Args:
            channel: ADC channel number (0-7)
            
        Returns:
            Raw ADC value (0-4095)
        """
        # MCP3208 12-bit read command format:
        # Byte 1: Start bit (1) + Single-ended mode (1) + Channel D2
        # Byte 2: Channel D1, D0 (shifted left by 6)
        # Byte 3: Dummy byte for reading
        
        channel_bits = channel & 0x07  # Ensure 0-7 range
        # Standard MCP3208 command: [Start, Single-ended+Channel, Dummy]
        cmd = [1, (8 + channel_bits) << 4, 0]
        
        # Send command and read response
        response = self.spi.xfer2(cmd)
        
        # Extract 12-bit value from response
        # Response format: [dummy, high byte (bits 3-0 valid), low byte]
        adc_value = ((response[1] & 0x0F) << 8) | response[2]
        
        return adc_value
    
    def read_x(self, smoothed: bool = True) -> float:
        """
        Read X-axis acceleration (normalized 0.0 to 1.0).
        
        Args:
            smoothed: If True, apply moving average filter (default: True)
        
        Returns:
            Normalized X-axis value (0.0 to 1.0)
        """
        raw_value = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_X)
        value = raw_value / 4095.0 - self.x_offset
        
        if smoothed:
            self.x_history.append(value)
            if len(self.x_history) == self.smoothing_samples:
                if self.use_median_filter:
                    return statistics.median(self.x_history)
                else:
                    return sum(self.x_history) / len(self.x_history)
            else:
                return value
        return value
    
    def read_y(self, smoothed: bool = True) -> float:
        """
        Read Y-axis acceleration (normalized 0.0 to 1.0).
        
        Args:
            smoothed: If True, apply moving average filter (default: True)
        
        Returns:
            Normalized Y-axis value (0.0 to 1.0)
        """
        raw_value = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Y)
        value = raw_value / 4095.0 - self.y_offset
        
        if smoothed:
            self.y_history.append(value)
            if len(self.y_history) == self.smoothing_samples:
                if self.use_median_filter:
                    return statistics.median(self.y_history)
                else:
                    return sum(self.y_history) / len(self.y_history)
            else:
                return value
        return value
    
    def read_z(self, smoothed: bool = True) -> float:
        """
        Read Z-axis acceleration (normalized 0.0 to 1.0).
        
        Args:
            smoothed: If True, apply moving average filter (default: True)
        
        Returns:
            Normalized Z-axis value (0.0 to 1.0)
        """
        raw_value = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Z)
        value = raw_value / 4095.0 - self.z_offset
        
        if smoothed:
            self.z_history.append(value)
            if len(self.z_history) == self.smoothing_samples:
                if self.use_median_filter:
                    return statistics.median(self.z_history)
                else:
                    return sum(self.z_history) / len(self.z_history)
            else:
                return value
        return value
    
    def read_all(self, smoothed: bool = True) -> dict:
        """
        Read all three axes at once.
        
        Args:
            smoothed: If True, apply moving average filter (default: True)
        
        Returns:
            Dictionary with 'x', 'y', 'z' keys (normalized 0.0 to 1.0)
        """
        return {
            'x': self.read_x(smoothed),
            'y': self.read_y(smoothed),
            'z': self.read_z(smoothed)
        }
    
    def calibrate(self, samples: int = 50):
        """
        Calibrate accelerometer by finding rest position.
        Keep accelerometer still during calibration.
        
        Args:
            samples: Number of samples to average for calibration (default: 50)
        """
        print(f"Calibrating accelerometer ({samples} samples)...")
        print("Keep accelerometer STILL during calibration...")
        
        x_values = []
        y_values = []
        z_values = []
        
        for i in range(samples):
            raw_x = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_X) / 4095.0
            raw_y = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Y) / 4095.0
            raw_z = self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Z) / 4095.0
            
            x_values.append(raw_x)
            y_values.append(raw_y)
            z_values.append(raw_z)
            
            if (i + 1) % 10 == 0:
                print(f"  Sample {i+1}/{samples}...")
        
        # Calculate average (rest position)
        self.x_offset = sum(x_values) / len(x_values)
        self.y_offset = sum(y_values) / len(y_values)
        self.z_offset = sum(z_values) / len(z_values)
        
        print(f"\nCalibration complete!")
        print(f"  X offset: {self.x_offset:.3f}")
        print(f"  Y offset: {self.y_offset:.3f}")
        print(f"  Z offset: {self.z_offset:.3f}")
        print(f"\nValues should now be centered around 0.0 when still")
    
    def set_offsets(self, x_offset: float, y_offset: float, z_offset: float):
        """
        Manually set calibration offsets.
        
        Args:
            x_offset: X-axis offset
            y_offset: Y-axis offset
            z_offset: Z-axis offset
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
    
    def read_raw_all(self) -> dict:
        """
        Read all three axes as raw ADC values.
        
        Returns:
            Dictionary with 'x', 'y', 'z' keys (raw 0-4095)
        """
        return {
            'x': self._read_adc_raw(config.ADC_CHANNEL_ACCEL_X),
            'y': self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Y),
            'z': self._read_adc_raw(config.ADC_CHANNEL_ACCEL_Z)
        }
    
    def calculate_magnitude(self, smoothed: bool = True) -> float:
        """
        Calculate acceleration magnitude (vector length).
        
        Args:
            smoothed: If True, use smoothed values (default: True)
        
        Returns:
            Magnitude of acceleration vector
        """
        x, y, z = self.read_x(smoothed), self.read_y(smoothed), self.read_z(smoothed)
        # Values are already offset-corrected, so center around 0.0
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        return magnitude
    
    def detect_movement(self, threshold: float = 0.1) -> bool:
        """
        Detect if accelerometer is moving (magnitude above threshold).
        
        Args:
            threshold: Movement detection threshold (default 0.1)
            
        Returns:
            True if movement detected, False otherwise
        """
        magnitude = self.calculate_magnitude()
        return magnitude > threshold
    
    def close(self):
        """Close SPI connection."""
        self.spi.close()

