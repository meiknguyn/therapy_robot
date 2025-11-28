# hardware/photoresistor.py
"""
Photoresistor (LDR) Module
Uses the same ADC pin/path from Assignment 3 (MCP3208 via SPI).
Provides normalized readings (0.0 to 1.0) and event logging.
"""
import time

try:
    import spidev
    HAVE_SPI = True
except ImportError:
    HAVE_SPI = False
    spidev = None

# ADC Configuration from Assignment 3
ADC_CHANNEL = 4  # Using channel 4 for photoresistor (unused in A3)
SPI_DEVICE = 0   # SPI device 0
SPI_CHIP_SELECT = 0  # CS0
SPI_MAX_SPEED = 1000000  # 1 MHz
ADC_MAX_VALUE = 4095  # 12-bit ADC


class Photoresistor:
    """
    Photoresistor (LDR) reader using MCP3208 ADC via SPI.
    Uses the same SPI configuration as Assignment 3.
    """

    def __init__(self, adc_channel=ADC_CHANNEL, log_callback=None):
        """
        Initialize photoresistor reader.
        
        Args:
            adc_channel: ADC channel number (0-7) on MCP3208
            log_callback: Optional callback function(event_type, details) for logging
        """
        self.adc_channel = adc_channel
        self.log_callback = log_callback
        self.spi = None
        
        if HAVE_SPI:
            try:
                self.spi = spidev.SpiDev()
                self.spi.open(SPI_DEVICE, SPI_CHIP_SELECT)
                self.spi.max_speed_hz = SPI_MAX_SPEED
                self.spi.mode = 0  # SPI mode 0 (CPOL=0, CPHA=0)
                print(f"[Photoresistor] Initialized on ADC channel {adc_channel}")
            except Exception as e:
                print(f"[Photoresistor] Failed to initialize SPI: {e}")
                self.spi = None
        else:
            print("[Photoresistor] spidev not available, using software simulation")

    def _read_adc_raw(self):
        """
        Read raw ADC value from MCP3208.
        Uses the same protocol as Assignment 3.
        
        Returns:
            Raw ADC value (0-4095) or -1 on error
        """
        if self.spi is None:
            # Simulate reading (returns random-ish value for testing)
            import random
            return random.randint(500, 3500)
        
        if self.adc_channel < 0 or self.adc_channel > 7:
            return -1
        
        try:
            # MCP3208 protocol (same as Assignment 3):
            # Byte 0: Start bit (1) + Single-ended (1) + Channel bit D2
            # Byte 1: Channel bits D1, D0 shifted left by 6
            # Byte 2: Don't care (0)
            tx = [
                0x06 | ((self.adc_channel & 0x04) >> 2),
                (self.adc_channel & 0x03) << 6,
                0x00
            ]
            rx = self.spi.xfer2(tx)
            
            # Extract 12-bit value from response
            # rx[1] contains upper 4 bits, rx[2] contains lower 8 bits
            value = ((rx[1] & 0x0F) << 8) | rx[2]
            return value
        except Exception as e:
            print(f"[Photoresistor] Error reading ADC: {e}")
            return -1

    def read_raw(self):
        """
        Read raw ADC value.
        
        Returns:
            Raw ADC value (0-4095) or -1 on error
        """
        return self._read_adc_raw()

    def read_normalized(self):
        """
        Read normalized photoresistor value (0.0 to 1.0).
        0.0 = very dark, 1.0 = very bright.
        
        Returns:
            Normalized value between 0.0 and 1.0
        """
        raw = self._read_adc_raw()
        if raw < 0:
            return 0.0
        
        # Normalize to 0.0-1.0 range
        normalized = raw / ADC_MAX_VALUE
        
        # Log the reading
        if self.log_callback:
            try:
                self.log_callback("ambient_light", {"value": normalized, "raw": raw})
            except Exception as e:
                print(f"[Photoresistor] Error in log callback: {e}")
        
        return normalized

    def is_dark(self, threshold=0.3):
        """
        Check if environment is dark based on threshold.
        
        Args:
            threshold: Threshold value (0.0-1.0), below which is considered dark
        
        Returns:
            True if dark, False otherwise
        """
        normalized = self.read_normalized()
        return normalized < threshold

    def cleanup(self):
        """Clean up SPI resources."""
        if self.spi is not None:
            try:
                self.spi.close()
            except:
                pass
            self.spi = None

