"""Pomodoro study timer feature."""

import threading
import time

from therapy_robot import config
from therapy_robot.dashboard import csv_logger


class PomodoroFeature:
    """Manages Pomodoro study sessions with LED feedback."""
    
    def __init__(self, led_controller, study_duration: float = 15.0, rest_duration: float = 5.0):
        """
        Initialize Pomodoro feature.
        
        Args:
            led_controller: LEDController instance for visual feedback
            study_duration: Study session duration in seconds (default: 15 for demo)
            rest_duration: Rest session duration in seconds (default: 5 for demo)
        """
        self.led = led_controller
        self.study_duration = study_duration
        self.rest_duration = rest_duration
        
        self.is_active = False
        self.is_study_session = False
        self.is_rest_session = False
        self.current_session_start = None
        self.remaining_time = 0.0
        
        self._stop_event = threading.Event()
        self._pomodoro_thread = None
        self._flashing_thread = None
        self._flashing_stop_event = threading.Event()
    
    def start(self) -> None:
        """Start a Pomodoro study session."""
        if self.is_active:
            return  # Already running
        
        self.is_active = True
        self.is_study_session = True
        self.is_rest_session = False
        self._stop_event.clear()
        self._flashing_stop_event.clear()
        
        # Start the Pomodoro timer thread
        self._pomodoro_thread = threading.Thread(target=self._pomodoro_loop, daemon=True)
        self._pomodoro_thread.start()
        
        # Log the event
        csv_logger.log_event(
            "pomodoro_started",
            {
                "study_duration": self.study_duration,
                "rest_duration": self.rest_duration
            }
        )
        
        print(f"\n🍅 Pomodoro study session started!")
        print(f"   Study time: {self.study_duration:.0f} seconds")
        print(f"   Rest time: {self.rest_duration:.0f} seconds")
        print(f"   💡 LED will breathe during study, flash during rest")
    
    def stop(self) -> None:
        """Stop the Pomodoro session."""
        if not self.is_active:
            return
        
        self.is_active = False
        self.is_study_session = False
        self.is_rest_session = False
        self._stop_event.set()
        self._flashing_stop_event.set()
        
        # Stop LED animations
        if self.led:
            self.led.breathing_stop()
            self.led.off()
        
        # Wait for threads to finish
        if self._pomodoro_thread and self._pomodoro_thread.is_alive():
            self._pomodoro_thread.join(timeout=2.0)
        
        if self._flashing_thread and self._flashing_thread.is_alive():
            self._flashing_thread.join(timeout=1.0)
        
        # Log the event
        csv_logger.log_event("pomodoro_stopped", {"reason": "user_request"})
        
        print("\n🍅 Pomodoro session stopped")
    
    def _pomodoro_loop(self) -> None:
        """Main Pomodoro timer loop - alternates between study and rest."""
        try:
            while not self._stop_event.is_set() and self.is_active:
                # Study session
                if self.is_study_session:
                    self.current_session_start = time.time()
                    self.remaining_time = self.study_duration
                    
                    # Start LED breathing animation
                    if self.led:
                        self.led.breathing_start()
                    
                    print(f"\n📚 Study session started ({self.study_duration:.0f}s)")
                    
                    # Wait for study duration
                    elapsed = 0.0
                    while elapsed < self.study_duration and not self._stop_event.is_set():
                        time.sleep(0.1)
                        elapsed = time.time() - self.current_session_start
                        self.remaining_time = self.study_duration - elapsed
                    
                    if self._stop_event.is_set():
                        break
                    
                    # Study session complete
                    if self.led:
                        self.led.breathing_stop()
                    
                    csv_logger.log_event("pomodoro_study_complete", {"duration": self.study_duration})
                    print(f"\n✅ Study session complete! Time for a break...")
                    
                    # Transition to rest session
                    self.is_study_session = False
                    self.is_rest_session = True
                
                # Rest session
                if self.is_rest_session:
                    self.current_session_start = time.time()
                    self.remaining_time = self.rest_duration
                    
                    # Start LED flashing
                    if self.led:
                        self._start_flashing()
                    
                    print(f"\n☕ Rest session started ({self.rest_duration:.0f}s)")
                    
                    # Wait for rest duration
                    elapsed = 0.0
                    while elapsed < self.rest_duration and not self._stop_event.is_set():
                        time.sleep(0.1)
                        elapsed = time.time() - self.current_session_start
                        self.remaining_time = self.rest_duration - elapsed
                    
                    if self._stop_event.is_set():
                        break
                    
                    # Rest session complete
                    if self.led:
                        self._stop_flashing()
                    
                    csv_logger.log_event("pomodoro_rest_complete", {"duration": self.rest_duration})
                    print(f"\n⏰ Rest complete! Ready to study again...")
                    
                    # Transition back to study session
                    self.is_rest_session = False
                    self.is_study_session = True
                    
                    # Continue loop (will start next study session)
        
        except Exception as e:
            print(f"Pomodoro loop error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            if self.led:
                self._stop_flashing()
                self.led.breathing_stop()
                self.led.off()
            
            self.is_active = False
            self.is_study_session = False
            self.is_rest_session = False
    
    def _start_flashing(self) -> None:
        """Start LED flashing animation for rest period."""
        if self._flashing_thread and self._flashing_thread.is_alive():
            return  # Already flashing
        
        self._flashing_stop_event.clear()
        self._flashing_thread = threading.Thread(target=self._flashing_animation, daemon=True)
        self._flashing_thread.start()
    
    def _stop_flashing(self) -> None:
        """Stop LED flashing animation."""
        self._flashing_stop_event.set()
        if self.led:
            self.led.off()
    
    def _flashing_animation(self) -> None:
        """LED flashing animation thread - flashes LED on/off rapidly."""
        try:
            flash_interval = 0.3  # Flash every 0.3 seconds
            while not self._flashing_stop_event.is_set():
                if self.led:
                    self.led.on()
                time.sleep(flash_interval)
                
                if self._flashing_stop_event.is_set():
                    break
                
                if self.led:
                    self.led.off()
                time.sleep(flash_interval)
        except Exception as e:
            print(f"Flashing animation error: {e}")
        finally:
            if self.led:
                self.led.off()
    
    def get_status(self) -> dict:
        """Get current status of Pomodoro feature."""
        return {
            "is_active": self.is_active,
            "is_study_session": self.is_study_session,
            "is_rest_session": self.is_rest_session,
            "remaining_time": self.remaining_time,
            "study_duration": self.study_duration,
            "rest_duration": self.rest_duration
        }

