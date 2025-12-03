"""Rotary encoder control via GPIO (stub for future implementation).

GPIO Configuration:
- Chip: /dev/gpiochip2
- Line 15 (GPIO5, Pin 29) → Rotary Encoder CLK (A)
- Line 17 (GPIO6, Pin 31) → Rotary Encoder DT (B)
- Line 18 (GPIO13, Pin 33) → Rotary Encoder Button (not used yet)
"""


class RotaryEncoder:
    """Rotary encoder controller (stub - to be implemented)."""
    
    def __init__(self):
        """Initialize rotary encoder (not yet implemented)."""
        pass
    
    def read_position(self) -> int:
        """Read encoder position (relative)."""
        raise NotImplementedError("Rotary encoder not yet implemented")
    
    def read_button(self) -> bool:
        """Read button state."""
        raise NotImplementedError("Rotary encoder button not yet implemented")

