# hardware/rotary.py
"""
Rotary Encoder Module
Uses the same CLK & DT pins from Assignment 3:
- gpiochip2 line 15 (GPIO5) for CLK
- gpiochip2 line 17 (GPIO6) for DT
"""
import threading
import time

try:
    import gpiod
    HAVE_GPIOD = True
except ImportError:
    HAVE_GPIOD = False
    gpiod = None

# GPIO Configuration from Assignment 3
CHIP_PATH = "/dev/gpiochip2"
LINE_CLK = 15  # GPIO5 on pin 29
LINE_DT = 17   # GPIO6 on pin 31


class RotaryEncoder:
    """
    Rotary encoder reader using gpiod (same as Assignment 3).
    Provides step counting for volume or other parameter control.
    """

    def __init__(self, value_change_callback=None, log_callback=None):
        """
        Initialize rotary encoder.
        
        Args:
            value_change_callback: Function(delta) called when encoder rotates
                                  delta: +1 for clockwise, -1 for counter-clockwise
            log_callback: Optional callback for logging events
        """
        self.value_change_callback = value_change_callback
        self.log_callback = log_callback
        self.running = False
        self.poll_thread = None
        self.last_clk_state = None
        self.steps = 0  # Accumulated steps
        
        if HAVE_GPIOD:
            try:
                self.chip = gpiod.Chip(CHIP_PATH)
                self.line_clk = self.chip.get_line(LINE_CLK)
                self.line_dt = self.chip.get_line(LINE_DT)
                
                # Configure as inputs with pull-up (if supported)
                config = gpiod.LineSettings()
                config.direction = gpiod.line.Direction.INPUT
                # Note: Pull-up configuration may vary by chip
                
                line_config = gpiod.LineConfig()
                line_config.add_line_settings([LINE_CLK, LINE_DT], config)
                
                request = self.chip.request_lines(
                    consumer="rotary-encoder",
                    config=line_config
                )
                self.request = request
                print(f"[RotaryEncoder] Initialized on gpiochip2 lines {LINE_CLK} (CLK) and {LINE_DT} (DT)")
            except Exception as e:
                print(f"[RotaryEncoder] Failed to initialize gpiod: {e}")
                self.request = None
                self.chip = None
        else:
            print("[RotaryEncoder] gpiod not available, using software simulation")
            self.request = None
            self.chip = None

    def _read_state(self):
        """
        Read current state of CLK and DT lines.
        
        Returns:
            Tuple (clk, dt) where values are 0 or 1, or None on error
        """
        if self.request is None:
            return None
        
        try:
            clk = self.request.get_value(LINE_CLK)
            dt = self.request.get_value(LINE_DT)
            return (clk, dt)
        except Exception as e:
            print(f"[RotaryEncoder] Error reading state: {e}")
            return None

    def start_polling(self):
        """Start background polling thread for encoder rotation."""
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
        """Background thread that polls encoder and tracks rotation."""
        while self.running:
            try:
                state = self._read_state()
                if state is None:
                    time.sleep(0.01)
                    continue
                
                clk, dt = state
                
                # Quadrature decoding: detect state changes
                if self.last_clk_state is not None:
                    # Detect CLK edge (state change)
                    if clk != self.last_clk_state:
                        # CLK changed, check DT to determine direction
                        if clk == dt:
                            # Clockwise
                            delta = 1
                        else:
                            # Counter-clockwise
                            delta = -1
                        
                        self.steps += delta
                        
                        if self.value_change_callback:
                            try:
                                self.value_change_callback(delta)
                            except Exception as e:
                                print(f"[RotaryEncoder] Error in callback: {e}")
                        
                        if self.log_callback:
                            try:
                                self.log_callback("rotary_encoder_rotate", {
                                    "delta": delta,
                                    "total_steps": self.steps
                                })
                            except:
                                pass
                
                self.last_clk_state = clk
                time.sleep(0.001)  # 1ms polling for responsiveness
            except Exception as e:
                print(f"[RotaryEncoder] Error in poll loop: {e}")
                time.sleep(0.01)

    def get_value(self):
        """
        Get accumulated step count.
        
        Returns:
            Current step count (can be positive or negative)
        """
        return self.steps

    def reset(self):
        """Reset step count to zero."""
        self.steps = 0

    def cleanup(self):
        """Clean up resources."""
        self.stop_polling()
        if self.request is not None:
            try:
                self.request.release()
            except:
                pass
        if self.chip is not None:
            try:
                self.chip.close()
            except:
                pass
            self.chip = None

