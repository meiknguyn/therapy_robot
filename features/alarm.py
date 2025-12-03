"""Alarm feature with time parsing and rotary button control."""

import re
import threading
import time
from datetime import datetime, timedelta

from therapy_robot import config
from therapy_robot.audio import speaker
from therapy_robot.dashboard import csv_logger


class AlarmFeature:
    """Manages alarm functionality with time parsing and button control."""
    
    def __init__(self, rotary_button):
        """
        Initialize alarm feature.
        
        Args:
            rotary_button: RotaryButton instance for alarm dismissal
        """
        self.rotary_button = rotary_button
        self.alarm_time = None  # datetime object for when alarm should trigger
        self.is_set = False
        self.is_ringing = False
        
        self._stop_event = threading.Event()
        self._alarm_thread = None
        self._button_monitor_thread = None
    
    def set_alarm(self, alarm_time: datetime) -> bool:
        """
        Set alarm for a specific time.
        
        Args:
            alarm_time: datetime object for when alarm should trigger
            
        Returns:
            True if alarm was set successfully, False otherwise
        """
        now = datetime.now()
        
        # If alarm time is in the past, assume it's for tomorrow
        if alarm_time < now:
            alarm_time = alarm_time + timedelta(days=1)
        
        self.alarm_time = alarm_time
        self.is_set = True
        self._stop_event.clear()
        
        # Start monitoring thread
        if self._alarm_thread is None or not self._alarm_thread.is_alive():
            self._alarm_thread = threading.Thread(target=self._alarm_monitor, daemon=True)
            self._alarm_thread.start()
        
        # Log the event
        csv_logger.log_event("alarm_set", {
            "alarm_time": alarm_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_until_alarm": str(alarm_time - now)
        })
        
        time_until = alarm_time - now
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        seconds = int(time_until.total_seconds() % 60)
        
        if hours > 0:
            print(f"\n⏰ Alarm set for {alarm_time.strftime('%H:%M:%S')} ({hours}h {minutes}m {seconds}s from now)")
        elif minutes > 0:
            print(f"\n⏰ Alarm set for {alarm_time.strftime('%H:%M:%S')} ({minutes}m {seconds}s from now)")
        else:
            print(f"\n⏰ Alarm set for {alarm_time.strftime('%H:%M:%S')} ({seconds}s from now)")
        
        return True
    
    def cancel_alarm(self) -> None:
        """Cancel the current alarm."""
        if not self.is_set:
            return
        
        self.is_set = False
        self.alarm_time = None
        self._stop_event.set()
        
        # Stop any ringing
        if self.is_ringing:
            self._stop_alarm()
        
        csv_logger.log_event("alarm_cancelled", {})
        print("\n⏰ Alarm cancelled")
    
    def _alarm_monitor(self) -> None:
        """Monitor thread that checks if alarm time has been reached."""
        try:
            while self.is_set and not self._stop_event.is_set():
                now = datetime.now()
                
                if self.alarm_time and now >= self.alarm_time:
                    # Alarm time reached!
                    self._trigger_alarm()
                    break
                
                # Check every second
                time.sleep(1.0)
        except Exception as e:
            print(f"Alarm monitor error: {e}")
            import traceback
            traceback.print_exc()
    
    def _trigger_alarm(self) -> None:
        """Trigger the alarm - start playing windchime sound."""
        if self.is_ringing:
            return  # Already ringing
        
        self.is_ringing = True
        self.is_set = False  # Alarm has triggered
        
        csv_logger.log_event("alarm_triggered", {
            "alarm_time": self.alarm_time.strftime("%Y-%m-%d %H:%M:%S") if self.alarm_time else None
        })
        
        print("\n🔔 ALARM! Press the rotary button to stop.")
        
        # Start playing windchime sound continuously
        alarm_file = "windchime.wav"
        alarm_path = config.MUSIC_DIR / alarm_file
        
        if not alarm_path.exists():
            print(f"⚠️ Alarm sound file not found: {alarm_path}")
            self.is_ringing = False
            return
        
        # Start button monitor thread
        if self._button_monitor_thread is None or not self._button_monitor_thread.is_alive():
            self._button_monitor_thread = threading.Thread(target=self._button_monitor, daemon=True)
            self._button_monitor_thread.start()
        
        # Play alarm sound continuously
        speaker.play_music(alarm_file, loop=True, volume=0.8)
    
    def _stop_alarm(self) -> None:
        """Stop the alarm sound."""
        if not self.is_ringing:
            return
        
        self.is_ringing = False
        speaker.stop_music()
        
        csv_logger.log_event("alarm_stopped", {"method": "button_press"})
        print("\n🔔 Alarm stopped")
    
    def _button_monitor(self) -> None:
        """Monitor button press to stop alarm."""
        try:
            while self.is_ringing:
                try:
                    if self.rotary_button and self.rotary_button.is_pressed():
                        # Button pressed - stop alarm
                        self._stop_alarm()
                        break
                except Exception as e:
                    # If button reading fails, continue monitoring
                    pass
                time.sleep(0.1)  # Check every 100ms
        except Exception as e:
            print(f"Button monitor error: {e}")
            import traceback
            traceback.print_exc()
    
    def get_status(self) -> dict:
        """Get current alarm status."""
        if not self.is_set:
            return {
                "is_set": False,
                "is_ringing": self.is_ringing,
                "alarm_time": None
            }
        
        now = datetime.now()
        time_until = self.alarm_time - now if self.alarm_time else None
        
        return {
            "is_set": True,
            "is_ringing": self.is_ringing,
            "alarm_time": self.alarm_time.strftime("%H:%M:%S") if self.alarm_time else None,
            "time_until_alarm": str(time_until) if time_until else None
        }


def parse_alarm_time(user_text: str) -> datetime:
    """
    Parse alarm time from user text.
    
    Supports formats:
    - "set alarm at 14:30" or "set alarm at 2:30 PM"
    - "wake me up in 30 minutes"
    - "wake me up in 5 minutes"
    - "wake me up in 30 seconds"
    - "alarm in 1 hour"
    
    Args:
        user_text: User input text
        
    Returns:
        datetime object for alarm time, or None if parsing failed
    """
    user_text_lower = user_text.lower().strip()
    now = datetime.now()
    
    # Pattern 1: "set alarm at HH:MM" or "alarm at HH:MM"
    time_pattern = r'(?:set\s+)?alarm\s+at\s+(\d{1,2}):(\d{2})(?:\s*(am|pm))?'
    match = re.search(time_pattern, user_text_lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3)
        
        # Handle 12-hour format
        if am_pm:
            if am_pm == 'pm' and hour != 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
        elif hour > 12:  # Assume 24-hour format if > 12
            pass
        elif hour == 12 and not am_pm:  # Ambiguous, assume 24-hour
            pass
        
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return alarm_time
    
    # Pattern 2: "wake me up in X minutes" or "alarm in X minutes"
    minutes_pattern = r'(?:wake\s+me\s+up\s+in|alarm\s+in|set\s+alarm\s+in)\s+(\d+)\s+minutes?'
    match = re.search(minutes_pattern, user_text_lower)
    if match:
        minutes = int(match.group(1))
        alarm_time = now + timedelta(minutes=minutes)
        return alarm_time
    
    # Pattern 3: "wake me up in X seconds" or "alarm in X seconds"
    seconds_pattern = r'(?:wake\s+me\s+up\s+in|alarm\s+in|set\s+alarm\s+in)\s+(\d+)\s+seconds?'
    match = re.search(seconds_pattern, user_text_lower)
    if match:
        seconds = int(match.group(1))
        alarm_time = now + timedelta(seconds=seconds)
        return alarm_time
    
    # Pattern 4: "wake me up in X hours" or "alarm in X hours"
    hours_pattern = r'(?:wake\s+me\s+up\s+in|alarm\s+in|set\s+alarm\s+in)\s+(\d+)\s+hours?'
    match = re.search(hours_pattern, user_text_lower)
    if match:
        hours = int(match.group(1))
        alarm_time = now + timedelta(hours=hours)
        return alarm_time
    
    return None

