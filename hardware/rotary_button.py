"""Rotary encoder button control via gpiod on BeagleY-AI."""

import gpiod

from therapy_robot import config


class RotaryButton:
    """Reads rotary encoder button state using gpiod (BeagleY-AI compatible)."""
    
    def __init__(self):
        """Initialize the rotary button using gpiod."""
        self.chip = gpiod.Chip(config.GPIO_CHIP)  # /dev/gpiochip2
        
        # Configure line settings for input with pull-up
        settings = gpiod.LineSettings()
        settings.direction = gpiod.line.Direction.INPUT
        settings.bias = gpiod.line.Bias.PULL_UP  # Pull-up resistor (button pressed = LOW)
        settings.active_low = True  # Button pressed = LOW (0), released = HIGH (1)
        
        # Request the line
        self.line_request = self.chip.request_lines(
            consumer="therapy_robot_rotary_button",
            config={config.GPIO_ROTARY_BTN: settings}
        )
    
    def is_pressed(self) -> bool:
        """
        Check if button is currently pressed.
        
        Returns:
            True if button is pressed, False if released
        """
        try:
            values = self.line_request.get_values()
            # get_values() returns a list of values in the order lines were requested
            # Since we only requested one line (GPIO_ROTARY_BTN), it's at index 0
            if len(values) > 0:
                button_value = values[0]
                # active_low=True means button pressed = ACTIVE (LOW), released = INACTIVE (HIGH)
                return button_value == gpiod.line.Value.ACTIVE
            return False
        except (IndexError, AttributeError) as e:
            # If there's an error accessing the value, assume button is not pressed
            return False
    
    def wait_for_press(self, timeout: float = None) -> bool:
        """
        Wait for button press.
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            True if button was pressed, False if timeout
        """
        import time
        
        start_time = time.time()
        while True:
            if self.is_pressed():
                return True
            
            if timeout is not None:
                if time.time() - start_time >= timeout:
                    return False
            
            time.sleep(0.01)  # Small delay to avoid CPU spinning
    
    def close(self):
        """Clean up resources."""
        self.line_request.release()
        self.chip.close()

