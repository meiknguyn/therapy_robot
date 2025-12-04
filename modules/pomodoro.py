# modules/pomodoro.py
import time
from datetime import datetime


class PomodoroTimer:
    """
    Simple demo Pomodoro timer.
    In real life you'd use 25 min; here we use short seconds for demo.
    """

    def __init__(self,
                 focus_seconds=20,
                 break_seconds=5,
                 speak_callback=None,
                 log_event_callback=None):
        self.focus_seconds = focus_seconds
        self.break_seconds = break_seconds
        self.speak_callback = speak_callback
        self.log_event_callback = log_event_callback

    def _say(self, msg: str):
        if self.speak_callback:
            self.speak_callback(msg)
        else:
            print("[Pomodoro]", msg)

    def _log(self, event_type: str, details: dict):
        if self.log_event_callback:
            self.log_event_callback(event_type, details)
        else:
            print("[Pomodoro LOG]", event_type, details)

    def run_demo_session(self):
        """
        Blocking demo: runs a single short focus + break cycle.
        """
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._say("Starting a short focus session now.")
        self._log("pomodoro_start", {
            "start_time": start_time,
            "focus_seconds": self.focus_seconds
        })

        # Simple countdown in chunks so it “feels alive”
        remaining = self.focus_seconds
        step = max(5, min(10, self.focus_seconds))  # 5–10 second steps
        while remaining > 0:
            self._say(f"Focus… about {remaining} seconds left in this demo session.")
            sleep_time = min(step, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._say("Focus session complete! Nice work. Time for a short break.")
        self._log("pomodoro_end", {
            "end_time": end_time
        })

        # Short break
        if self.break_seconds > 0:
            self._say("Starting a short break.")
            time.sleep(self.break_seconds)
            self._say("Break finished. You can start another focus session whenever you're ready.")
            self._log("pomodoro_break_complete", {
                "break_seconds": self.break_seconds
            })
