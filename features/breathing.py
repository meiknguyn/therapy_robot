"""Breathing exercise feature with LED visual guidance."""

import threading
import time

from therapy_robot import config
from therapy_robot.dashboard import csv_logger


class BreathingExercise:
    """Manages breathing exercise sessions with LED visual feedback."""
    
    def __init__(self, led_controller, inhale_duration: float = 3.0, hold_duration: float = 3.0, exhale_duration: float = 3.0):
        """
        Initialize breathing exercise feature.
        
        Args:
            led_controller: LEDController instance for visual feedback
            inhale_duration: Duration for inhale phase in seconds (default: 3.0)
            hold_duration: Duration for hold phase in seconds (default: 3.0)
            exhale_duration: Duration for exhale phase in seconds (default: 3.0)
        """
        self.led = led_controller
        self.inhale_duration = inhale_duration
        self.hold_duration = hold_duration
        self.exhale_duration = exhale_duration
        
        self.is_active = False
        self.current_phase = None  # 'inhale', 'hold', 'exhale'
        self.remaining_time = 0.0
        self.cycle_count = 0
        
        self._stop_event = threading.Event()
        self._breathing_thread = None
        self._led_animation_thread = None
        self._led_stop_event = threading.Event()
    
    def start(self) -> None:
        """Start a breathing exercise session."""
        if self.is_active:
            return  # Already running
        
        self.is_active = True
        self.cycle_count = 0
        self._stop_event.clear()
        self._led_stop_event.clear()
        
        # Start the breathing exercise thread
        self._breathing_thread = threading.Thread(target=self._breathing_loop, daemon=True)
        self._breathing_thread.start()
        
        # Log the event
        csv_logger.log_event(
            "breathing_exercise_started",
            {
                "inhale_duration": self.inhale_duration,
                "hold_duration": self.hold_duration,
                "exhale_duration": self.exhale_duration
            }
        )
        
        print(f"\n🧘 Breathing exercise started!")
        print(f"   Inhale: {self.inhale_duration:.0f}s (LED bright)")
        print(f"   Hold: {self.hold_duration:.0f}s (LED breathing)")
        print(f"   Exhale: {self.exhale_duration:.0f}s (LED rapid flash)")
        print(f"   💡 Follow the LED pattern to guide your breathing")
    
    def stop(self) -> None:
        """Stop the breathing exercise session."""
        if not self.is_active:
            return
        
        self.is_active = False
        self.current_phase = None
        self._stop_event.set()
        self._led_stop_event.set()
        
        # Stop LED animations
        if self.led:
            self.led.breathing_stop()
            self.led.off()
        
        # Wait for threads to finish (only if not calling from within the thread)
        if self._breathing_thread and self._breathing_thread.is_alive():
            # Check if we're calling from within the thread itself
            if threading.current_thread() != self._breathing_thread:
                try:
                    self._breathing_thread.join(timeout=2.0)
                except RuntimeError:
                    # Thread is trying to join itself, skip
                    pass
        
        if self._led_animation_thread and self._led_animation_thread.is_alive():
            if threading.current_thread() != self._led_animation_thread:
                try:
                    self._led_animation_thread.join(timeout=1.0)
                except RuntimeError:
                    # Thread is trying to join itself, skip
                    pass
        
        # Log the event
        csv_logger.log_event("breathing_exercise_stopped", {
            "reason": "user_request" if self._stop_event.is_set() else "completed",
            "cycles_completed": self.cycle_count
        })
        
        print(f"\n🧘 Breathing exercise stopped (completed {self.cycle_count} cycles)")
    
    def _breathing_loop(self) -> None:
        """Main breathing exercise loop - runs once through inhale, hold, exhale."""
        try:
            # Phase 1: Inhale - LED stays bright
            self.current_phase = 'inhale'
            self.remaining_time = self.inhale_duration
            phase_start = time.time()
            
            print(f"\n💨 INHALE ({self.inhale_duration:.0f}s) - Keep the LED bright...")
            
            # Start LED bright animation
            if self.led:
                self._start_bright_led()
            
            # Wait for inhale duration
            elapsed = 0.0
            while elapsed < self.inhale_duration and not self._stop_event.is_set():
                time.sleep(0.1)
                elapsed = time.time() - phase_start
                self.remaining_time = self.inhale_duration - elapsed
            
            if self._stop_event.is_set():
                return
            
            # Phase 2: Hold - LED breathing animation
            self.current_phase = 'hold'
            self.remaining_time = self.hold_duration
            phase_start = time.time()
            
            print(f"\n⏸️  HOLD ({self.hold_duration:.0f}s) - Follow the breathing LED...")
            
            # Start LED breathing animation
            if self.led:
                self._start_breathing_led()
            
            # Wait for hold duration
            elapsed = 0.0
            while elapsed < self.hold_duration and not self._stop_event.is_set():
                time.sleep(0.1)
                elapsed = time.time() - phase_start
                self.remaining_time = self.hold_duration - elapsed
            
            if self._stop_event.is_set():
                return
            
            # Phase 3: Exhale - LED rapid flashing
            self.current_phase = 'exhale'
            self.remaining_time = self.exhale_duration
            phase_start = time.time()
            
            print(f"\n💨 EXHALE ({self.exhale_duration:.0f}s) - Follow the rapid flash...")
            
            # Start LED rapid flashing
            if self.led:
                self._start_rapid_flash()
            
            # Wait for exhale duration
            elapsed = 0.0
            while elapsed < self.exhale_duration and not self._stop_event.is_set():
                time.sleep(0.1)
                elapsed = time.time() - phase_start
                self.remaining_time = self.exhale_duration - elapsed
            
            if self._stop_event.is_set():
                return
            
            # Exercise complete (single cycle)
            self.cycle_count = 1
            csv_logger.log_event("breathing_exercise_complete", {
                "inhale_duration": self.inhale_duration,
                "hold_duration": self.hold_duration,
                "exhale_duration": self.exhale_duration
            })
            
            print(f"\n✅ Breathing exercise complete!")
            
            # Mark as inactive and let thread exit naturally (don't call stop() from within thread)
            self.is_active = False
        
        except Exception as e:
            print(f"Breathing exercise loop error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            if self.led:
                self._stop_led_animation()
                self.led.breathing_stop()
                self.led.off()
            
            # Mark as inactive
            self.is_active = False
            self.current_phase = None
            
            # Log completion if it ended naturally (not stopped by user)
            if not self._stop_event.is_set() and self.cycle_count > 0:
                csv_logger.log_event("breathing_exercise_stopped", {
                    "reason": "completed",
                    "cycles_completed": self.cycle_count
                })
                print(f"\n🧘 Breathing exercise stopped (completed {self.cycle_count} cycles)")
    
    def _start_bright_led(self) -> None:
        """Start LED bright (stationary) animation for inhale phase."""
        self._stop_led_animation()
        self._led_stop_event.clear()
        
        if self.led:
            self.led.on()  # Keep LED fully bright
    
    def _start_breathing_led(self) -> None:
        """Start LED breathing animation for hold phase."""
        self._stop_led_animation()
        self._led_stop_event.clear()
        
        if self.led:
            self.led.breathing_start()  # Use existing breathing animation
    
    def _start_rapid_flash(self) -> None:
        """Start LED rapid flashing animation for exhale phase."""
        self._stop_led_animation()
        self._led_stop_event.clear()
        
        if self._led_animation_thread and self._led_animation_thread.is_alive():
            return  # Already flashing
        
        self._led_animation_thread = threading.Thread(target=self._rapid_flash_animation, daemon=True)
        self._led_animation_thread.start()
    
    def _stop_led_animation(self) -> None:
        """Stop all LED animations."""
        self._led_stop_event.set()
        if self.led:
            self.led.breathing_stop()
    
    def _rapid_flash_animation(self) -> None:
        """LED rapid flashing animation thread - flashes LED on/off rapidly."""
        try:
            flash_interval = 0.15  # Flash every 0.15 seconds (rapid)
            while not self._led_stop_event.is_set():
                if self.led:
                    self.led.on()
                time.sleep(flash_interval)
                
                if self._led_stop_event.is_set():
                    break
                
                if self.led:
                    self.led.off()
                time.sleep(flash_interval)
        except Exception as e:
            print(f"Rapid flash animation error: {e}")
        finally:
            if self.led:
                self.led.off()
    
    def get_status(self) -> dict:
        """Get current status of breathing exercise."""
        return {
            "is_active": self.is_active,
            "current_phase": self.current_phase,
            "remaining_time": self.remaining_time,
            "cycle_count": self.cycle_count,
            "inhale_duration": self.inhale_duration,
            "hold_duration": self.hold_duration,
            "exhale_duration": self.exhale_duration
        }

