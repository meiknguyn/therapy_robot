"""Safety feature with fall detection and emergency Discord notifications."""

import os
import threading
import time
from datetime import datetime

import requests

from therapy_robot import config
from therapy_robot.dashboard import csv_logger


class SafetyFeature:
    """Manages fall detection and emergency response."""
    
    def __init__(self, accelerometer, led_controller):
        """
        Initialize safety feature.
        
        Args:
            accelerometer: Accelerometer instance for motion detection
            led_controller: LEDController instance for emergency flashing
        """
        self.accelerometer = accelerometer
        self.led = led_controller
        
        # Load Discord webhook URL from environment
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        
        self.is_active = False
        self.fall_detected = False
        self.waiting_for_response = False
        self.emergency_mode = False
        
        # Fall detection parameters (normalized values 0.0-1.0)
        # Using only Z-axis for vertical movement detection
        # Z-axis jitter: jumps between ~0.15 and ~0.65 (0.5 jump) even when still
        # Calibrated based on test results: Z jumps between 0.148-0.149 and 0.649
        # During fall: Z-axis changes significantly (vertical movement)
        # On impact: Z-axis spikes
        self.free_fall_threshold = 0.1  # Z-axis threshold for free-fall (below jitter lower bound ~0.15)
        self.impact_threshold = 0.75  # Z-axis threshold for impact (above jitter upper bound ~0.65)
        self.check_interval = 0.06  # Check accelerometer every 60ms (balanced)
        
        # Track previous Z value for change detection
        self.previous_z = None
        self.z_change_threshold = 0.45  # Sudden Z-axis change threshold (must be > jitter jump of ~0.5)
        
        # Require sustained detection (multiple consecutive detections)
        self.detection_count = 0
        self.detection_threshold = 3  # Require 3 consecutive detections (180ms) - reduce false positives from jitter
        
        # Use smoothed readings to reduce jitter
        self.use_smoothed_readings = True
        
        # Normal range for filtering jitter (Z value should be in this range when still)
        # Z-axis jitter: ~0.15 to ~0.65, so normal range covers this with buffer
        self.normal_range_min = 0.1  # Lower bound (Z only, covers jitter lower bound)
        self.normal_range_max = 0.7  # Upper bound (Z only, covers jitter upper bound)
        
        # Track Z value history for pattern detection (rapid state switching)
        self.z_history = []
        self.z_history_size = 5  # Track last 5 readings
        
        # Z-axis jitter states (detected from calibration)
        self.z_jitter_low = 0.15  # Lower jitter state
        self.z_jitter_high = 0.65  # Higher jitter state
        self.z_jitter_jump = 0.5  # Size of jitter jump
        
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._led_flash_thread = None
        self._led_flash_stop_event = threading.Event()
        self.previous_z = None  # Track previous Z value for change detection
    
    def start(self) -> None:
        """Start fall detection monitoring."""
        if self.is_active:
            return
        
        self.is_active = True
        self.fall_detected = False
        self.waiting_for_response = False
        self.emergency_mode = False
        self._stop_event.clear()
        self._led_flash_stop_event.clear()
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        csv_logger.log_event("safety_feature_started", {})
        print("\n🛡️ Safety feature activated - Fall detection monitoring...")
    
    def stop(self) -> None:
        """Stop fall detection monitoring."""
        if not self.is_active:
            return
        
        self.is_active = False
        self.fall_detected = False
        self.waiting_for_response = False
        self.emergency_mode = False
        self._stop_event.set()
        self._led_flash_stop_event.set()
        
        # Stop LED flashing
        if self.led:
            self.led.breathing_stop()
            self.led.off()
        
        # Wait for threads to finish
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
        
        if self._led_flash_thread and self._led_flash_thread.is_alive():
            self._led_flash_thread.join(timeout=1.0)
        
        csv_logger.log_event("safety_feature_stopped", {})
        print("\n🛡️ Safety feature deactivated")
    
    def _monitor_loop(self) -> None:
        """Monitor accelerometer for fall detection."""
        try:
            while self.is_active and not self._stop_event.is_set():
                try:
                    # Read accelerometer values (use smoothed to reduce jitter)
                    # Use only Z-axis for vertical movement detection
                    smoothed = self.use_smoothed_readings
                    z = self.accelerometer.read_z(smoothed=smoothed)
                    # x = self.accelerometer.read_x(smoothed=smoothed)  # Not used
                    # y = self.accelerometer.read_y(smoothed=smoothed)  # Not used
                    
                    # Use absolute Z value for detection (normalized 0.0-1.0)
                    # Z-axis detects vertical movement (fall/impact)
                    z_abs = abs(z)
                    
                    # Track Z history for pattern detection
                    self.z_history.append(z_abs)
                    if len(self.z_history) > self.z_history_size:
                        self.z_history.pop(0)
                    
                    # Detect sudden changes (fall or impact)
                    if self.previous_z is not None:
                        z_change = abs(z - self.previous_z)
                        
                        # Detect free-fall, impact, or sudden change in Z-axis
                        is_free_fall = z_abs < self.free_fall_threshold
                        is_impact = z_abs > self.impact_threshold
                        is_sudden_change = z_change > self.z_change_threshold
                        
                        # Pattern detection: detect when Z stays consistently outside jitter range
                        # Z-axis jitters between 0.15 and 0.65, so detect when it stays outside this range
                        z_outside_jitter = sum(1 for z_val in self.z_history 
                                             if z_val < self.z_jitter_low or z_val > self.z_jitter_high)
                        is_pattern_detected = z_outside_jitter >= 3  # 3 out of 5 readings outside jitter range
                        
                        # Detect if Z is consistently in a new state (not just jittering)
                        # Check if all recent readings are significantly different from jitter states
                        z_avg_recent = sum(self.z_history) / len(self.z_history) if self.z_history else z_abs
                        z_far_from_jitter = (abs(z_avg_recent - self.z_jitter_low) > 0.1 and 
                                            abs(z_avg_recent - self.z_jitter_high) > 0.1)
                        
                        # For sudden changes, check if it's a significant change
                        # Allow detection if change is very large OR if pattern detected
                        if is_sudden_change:
                            # If change is very large (> 0.5), always trigger (real fall/impact)
                            # Or if Z is consistently far from jitter states
                            if z_change > 0.5:
                                is_sudden_change = True  # Very large change = real fall/impact
                            elif is_pattern_detected and z_far_from_jitter:
                                is_sudden_change = True  # Pattern detected + far from jitter = real movement
                            else:
                                is_sudden_change = False  # Normal jitter between states
                        
                        if is_free_fall or is_impact or is_sudden_change:
                            # Require sustained detection to reduce false positives from jitter
                            self.detection_count += 1
                            if self.detection_count >= self.detection_threshold:
                                if not self.fall_detected:
                                    print(f"[Safety] Fall detected! Z={z:.3f}, Z_abs={z_abs:.3f}, Change={z_change:.3f}, Pattern={is_pattern_detected}")
                                    self._detect_fall()
                        else:
                            # Reset detection count if no detection
                            self.detection_count = 0
                    else:
                        # Initialize previous Z value
                        self.previous_z = z
                        self.detection_count = 0
                        self.z_history = [z_abs]
                        continue
                    
                    self.previous_z = z
                    time.sleep(self.check_interval)
                except Exception as e:
                    # Skip reading if it fails
                    time.sleep(self.check_interval)
        except Exception as e:
            print(f"Safety monitor error: {e}")
            import traceback
            traceback.print_exc()
    
    def _detect_fall(self) -> None:
        """Handle fall detection."""
        if self.fall_detected:
            return  # Already detected, don't trigger again
        
        self.fall_detected = True
        self.waiting_for_response = True
        self.detection_count = 0  # Reset for next detection
        
        csv_logger.log_event("fall_detected", {
            "timestamp": datetime.now().isoformat(),
            "free_fall_threshold": self.free_fall_threshold,
            "impact_threshold": self.impact_threshold,
            "z_value": self.previous_z
        })
        
        print("\n⚠️ FALL DETECTION!")
        print("Are you okay? Please reply 'I'm okay' or 'I'm fine' if you're safe.")
        print("(If no response, emergency protocol will activate in 30 seconds)")
        
        # Start response timer (30 seconds)
        response_timer = threading.Timer(30.0, self._timeout_emergency)
        response_timer.daemon = True
        response_timer.start()
    
    def handle_user_response(self, user_text: str) -> bool:
        """
        Handle user response to fall detection.
        
        Args:
            user_text: User's response text
            
        Returns:
            True if response was handled (user is okay), False otherwise
        """
        if not self.waiting_for_response:
            return False
        
        user_text_lower = user_text.lower().strip()
        
        # Check for "I'm okay" responses
        okay_phrases = [
            "i'm okay",
            "im okay",
            "i am okay",
            "i'm fine",
            "im fine",
            "i am fine",
            "yes i'm okay",
            "yes im okay",
            "yes i am okay",
            "yes i'm fine",
            "yes im fine",
            "yes i am fine",
            "okay",
            "fine",
            "yes",
            "i'm safe",
            "im safe",
            "i am safe"
        ]
        
        if any(phrase in user_text_lower for phrase in okay_phrases):
            # User is okay - cancel emergency
            self._cancel_emergency()
            csv_logger.log_event("fall_response_okay", {"user_response": user_text})
            print("\n✅ Good to hear you're okay! Safety feature resuming normal monitoring.")
            return True
        
        # If response doesn't indicate user is okay, continue with emergency
        return False
    
    def cancel_fall_detection(self) -> None:
        """Cancel fall detection and return to normal monitoring."""
        self._cancel_emergency()
        csv_logger.log_event("fall_detection_cancelled", {"method": "user_command"})
    
    def _timeout_emergency(self) -> None:
        """Activate emergency protocol after timeout."""
        if not self.waiting_for_response:
            return
        
        # User didn't respond - activate emergency
        self._activate_emergency()
    
    def _cancel_emergency(self) -> None:
        """Cancel emergency protocol."""
        self.fall_detected = False
        self.waiting_for_response = False
        self.emergency_mode = False
        self.detection_count = 0  # Reset detection count
        self._led_flash_stop_event.set()
        
        if self.led:
            self.led.breathing_stop()
            self.led.off()
    
    def _activate_emergency(self) -> None:
        """Activate emergency protocol - Discord webhook and LED flashing."""
        if self.emergency_mode:
            return  # Already in emergency mode
        
        self.emergency_mode = True
        self.waiting_for_response = False
        
        csv_logger.log_event("emergency_activated", {
            "timestamp": datetime.now().isoformat(),
            "discord_webhook_available": bool(self.discord_webhook_url)
        })
        
        print("\n🚨 EMERGENCY PROTOCOL ACTIVATED!")
        print("Sending emergency notifications...")
        
        # Start LED rapid flashing
        if self.led:
            self._start_emergency_flash()
        
        # Send Discord webhook notification
        if self.discord_webhook_url:
            self._send_discord_alert()
        else:
            print("⚠️ Discord webhook URL not configured in .env file")
        
        # Continue sending periodic alerts
        self._start_periodic_alerts()
    
    def _start_emergency_flash(self) -> None:
        """Start LED rapid flashing for emergency."""
        self._led_flash_stop_event.clear()
        
        if self._led_flash_thread and self._led_flash_thread.is_alive():
            return
        
        self._led_flash_thread = threading.Thread(target=self._emergency_flash_animation, daemon=True)
        self._led_flash_thread.start()
    
    def _emergency_flash_animation(self) -> None:
        """LED rapid flashing animation for emergency."""
        try:
            flash_interval = 0.1  # Flash every 0.1 seconds (very rapid)
            while not self._led_flash_stop_event.is_set() and self.emergency_mode:
                if self.led:
                    self.led.on()
                time.sleep(flash_interval)
                
                if self._led_flash_stop_event.is_set():
                    break
                
                if self.led:
                    self.led.off()
                time.sleep(flash_interval)
        except Exception as e:
            print(f"Emergency flash animation error: {e}")
        finally:
            if self.led:
                self.led.off()
    
    def _send_discord_alert(self) -> None:
        """Send emergency alert to Discord webhook."""
        if not self.discord_webhook_url:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            payload = {
                "content": f"🚨 **EMERGENCY ALERT** 🚨",
                "embeds": [{
                    "title": "Fall Detection Alert",
                    "description": "Therapy Robot has detected a potential fall and user has not confirmed they are okay.",
                    "color": 15158332,  # Red color
                    "fields": [
                        {
                            "name": "Timestamp",
                            "value": timestamp,
                            "inline": False
                        },
                        {
                            "name": "Status",
                            "value": "Emergency protocol activated",
                            "inline": False
                        },
                        {
                            "name": "Action Required",
                            "value": "Please check on the user immediately",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "Therapy Robot Safety System"
                    }
                }]
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=5.0
            )
            
            if response.status_code == 204:
                print("✅ Emergency alert sent to Discord successfully")
                csv_logger.log_event("discord_alert_sent", {"timestamp": timestamp})
            else:
                print(f"⚠️ Failed to send Discord alert: HTTP {response.status_code}")
                csv_logger.log_event("discord_alert_failed", {
                    "status_code": response.status_code,
                    "timestamp": timestamp
                })
        except Exception as e:
            print(f"⚠️ Error sending Discord alert: {e}")
            csv_logger.log_event("discord_alert_error", {"error": str(e)})
    
    def _start_periodic_alerts(self) -> None:
        """Start sending periodic Discord alerts every 60 seconds."""
        def send_periodic():
            while self.emergency_mode and not self._stop_event.is_set():
                time.sleep(60.0)  # Wait 60 seconds
                if self.emergency_mode and not self._stop_event.is_set():
                    self._send_discord_alert()
        
        periodic_thread = threading.Thread(target=send_periodic, daemon=True)
        periodic_thread.start()
    
    def get_status(self) -> dict:
        """Get current safety feature status."""
        return {
            "is_active": self.is_active,
            "fall_detected": self.fall_detected,
            "waiting_for_response": self.waiting_for_response,
            "emergency_mode": self.emergency_mode,
            "discord_webhook_configured": bool(self.discord_webhook_url)
        }

