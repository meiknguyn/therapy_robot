"""Joystick control via MCP3208 ADC."""

import spidev

from therapy_robot import config


class Joystick:
    """Reads joystick X and Y positions from MCP3208 ADC (channels 0 and 1)."""
    
    def __init__(self):
        """Initialize SPI connection to MCP3208."""
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # bus 0, device 0 (/dev/spidev0.0)
        self.spi.mode = config.SPI_MODE
        self.spi.max_speed_hz = config.SPI_MAX_SPEED
    
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
    
    def read_x(self) -> float:
        """
        Read X-axis position (normalized 0.0 to 1.0).
        
        Returns:
            Normalized X position (0.0 = left, 1.0 = right)
        """
        raw_value = self._read_adc_raw(config.ADC_CHANNEL_JOYSTICK_X)
        normalized = raw_value / 4095.0
        return normalized
    
    def read_y(self) -> float:
        """
        Read Y-axis position (normalized 0.0 to 1.0).
        
        Returns:
            Normalized Y position (0.0 = up, 1.0 = down)
        """
        raw_value = self._read_adc_raw(config.ADC_CHANNEL_JOYSTICK_Y)
        normalized = raw_value / 4095.0
        return normalized
    
    def read_both(self) -> dict:
        """
        Read both X and Y axes.
        
        Returns:
            Dict with 'x' and 'y' keys (both 0.0 to 1.0)
        """
        return {
            'x': self.read_x(),
            'y': self.read_y()
        }
    
    def close(self):
        """Close SPI connection."""
        self.spi.close()

