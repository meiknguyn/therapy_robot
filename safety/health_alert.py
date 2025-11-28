# safety/health_alert.py
"""
Health Alert Module
Handles user check-in after fall detection and sends Discord alerts if needed.
"""
import os
import time
import threading
import requests
from datetime import datetime

# Configuration
CHECK_IN_TIMEOUT_SECONDS = 30  # Time to wait for user response
DISCORD_WEBHOOK_URL_ENV = "DISCORD_WEBHOOK_URL"  # Environment variable name


class HealthAlert:
    """
    Health alert system that checks on user after fall and sends Discord alerts.
    """

    def __init__(self, speak_callback=None, listen_callback=None, log_callback=None):
        """
        Initialize health alert system.
        
        Args:
            speak_callback: Function(text) to speak messages to user
            listen_callback: Function() to listen for user input (returns text or None)
            log_callback: Optional callback function(event_type, details) for logging
        """
        self.speak_callback = speak_callback
        self.listen_callback = listen_callback
        self.log_callback = log_callback
        self.discord_webhook_url = os.getenv(DISCORD_WEBHOOK_URL_ENV)
        self.check_in_active = False
        self.check_in_thread = None
        
        if not self.discord_webhook_url:
            print(f"[HealthAlert] Warning: {DISCORD_WEBHOOK_URL_ENV} not set. Discord alerts will be disabled.")
            print("[HealthAlert] Set the environment variable or add it to config/secrets.env")

    def _say(self, text: str):
        """Speak text using callback or print."""
        if self.speak_callback:
            try:
                self.speak_callback(text)
            except Exception as e:
                print(f"[HealthAlert] Error speaking: {e}")
        else:
            print(f"[HealthAlert]: {text}")

    def _listen(self, timeout_seconds=30):
        """Listen for user input with timeout."""
        if self.listen_callback:
            try:
                # Start listening in a separate thread with timeout
                result = [None]
                exception_occurred = [False]
                
                def listen_thread():
                    try:
                        result[0] = self.listen_callback()
                    except Exception as e:
                        exception_occurred[0] = True
                        print(f"[HealthAlert] Error listening: {e}")
                
                listen_th = threading.Thread(target=listen_thread, daemon=True)
                listen_th.start()
                listen_th.join(timeout=timeout_seconds)
                
                if exception_occurred[0]:
                    return None
                
                return result[0]
            except Exception as e:
                print(f"[HealthAlert] Error in listen wrapper: {e}")
                return None
        else:
            # Fallback: simulate listening with user input
            print(f"[HealthAlert] Waiting for response (timeout: {timeout_seconds}s)...")
            return input("Your response: ").strip()

    def _log(self, event_type: str, details: dict):
        """Log event using callback."""
        if self.log_callback:
            try:
                self.log_callback(event_type, details)
            except Exception as e:
                print(f"[HealthAlert] Error in log callback: {e}")

    def send_discord_alert(self, message: str):
        """
        Send alert message to Discord webhook.
        
        Args:
            message: Message to send
        
        Returns:
            True if successful, False otherwise
        """
        if not self.discord_webhook_url:
            print("[HealthAlert] Discord webhook URL not configured")
            return False
        
        try:
            # Create webhook payload
            payload = {
                "content": message,
                "username": "Therapy Robot Alert",
                "embeds": [{
                    "title": "🚨 Health Alert",
                    "description": message,
                    "color": 15158332,  # Red color
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {
                        "text": "Therapy Robot Safety System"
                    }
                }]
            }
            
            # Send POST request to Discord webhook
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                print("[HealthAlert] Discord alert sent successfully")
                self._log("discord_alert_sent", {"message": message})
                return True
            else:
                print(f"[HealthAlert] Failed to send Discord alert: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[HealthAlert] Error sending Discord alert: {e}")
            return False

    def check_on_user(self):
        """
        Check on user after fall detection.
        Asks if they're okay and sends Discord alert if no response or negative response.
        
        Returns:
            True if user is okay, False if assistance needed
        """
        if self.check_in_active:
            print("[HealthAlert] Check-in already in progress")
            return True
        
        self.check_in_active = True
        
        try:
            self._say("I detected a fall. Are you okay? Please respond with 'yes' or 'I'm okay' if you're fine.")
            
            self._log("health_check_initiated", {
                "timestamp": datetime.now().isoformat(),
                "timeout": CHECK_IN_TIMEOUT_SECONDS
            })
            
            # Wait for user response
            response = self._listen(timeout_seconds=CHECK_IN_TIMEOUT_SECONDS)
            
            if response is None or not response:
                # No response - send alert
                self._say("I didn't hear a response. I'm sending an alert to your emergency contact.")
                alert_message = (
                    "🚨 **FALL DETECTED - NO RESPONSE**\n\n"
                    f"A fall was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
                    "The robot did not receive a response from the user.\n"
                    "Please check on them immediately."
                )
                self.send_discord_alert(alert_message)
                self.check_in_active = False
                return False
            
            # Normalize response
            response_lower = response.lower().strip()
            
            # Check for positive responses
            positive_keywords = ["yes", "okay", "ok", "fine", "good", "alright", "i'm okay", "im okay", "yes i'm okay"]
            is_okay = any(keyword in response_lower for keyword in positive_keywords)
            
            if is_okay:
                self._say("I'm glad you're okay. Take care!")
                self._log("health_check_passed", {
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                self.check_in_active = False
                return True
            else:
                # Negative or unclear response - send alert
                self._say("I understand you need help. I'm sending an alert to your emergency contact right away.")
                alert_message = (
                    "🚨 **FALL DETECTED - ASSISTANCE NEEDED**\n\n"
                    f"A fall was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
                    f"User response: \"{response}\"\n"
                    "The user may need assistance. Please check on them immediately."
                )
                self.send_discord_alert(alert_message)
                self._log("health_check_failed", {
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                self.check_in_active = False
                return False
                
        except Exception as e:
            print(f"[HealthAlert] Error during health check: {e}")
            # On error, send alert to be safe
            self.send_discord_alert(
                f"🚨 **FALL DETECTED - SYSTEM ERROR**\n\n"
                f"A fall was detected but an error occurred during the health check.\n"
                f"Error: {str(e)}\n"
                f"Please check on the user."
            )
            self.check_in_active = False
            return False
        finally:
            self.check_in_active = False

    def test_discord_alert(self):
        """
        Send a test Discord alert to verify webhook configuration.
        
        Returns:
            True if successful, False otherwise
        """
        test_message = (
            "🧪 **TEST ALERT**\n\n"
            "This is a test message from the Therapy Robot safety system.\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "If you receive this, your Discord webhook is configured correctly."
        )
        return self.send_discord_alert(test_message)

