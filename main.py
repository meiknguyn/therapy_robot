# main.py
import requests
import threading
import time

from ai.gemini_client import analyze_emotion, chat_with_gemini
from audio_io.audio_io import listen, speak

from modules.pomodoro import PomodoroTimer
from modules.meditation_led import MeditationBreather

# New hardware modules
from hardware.led_ctrl import LEDController
from hardware.photoresistor import Photoresistor
from hardware.joystick import Joystick
from hardware.rotary import RotaryEncoder

# New audio and module components
from audio.speaker import Speaker
from modules.ambient_music import AmbientMusic
from modules.camera_capture import CameraCapture

# Safety modules
from safety.fall_detector import FallDetector
from safety.health_alert import HealthAlert

DASHBOARD_BASE = "http://127.0.0.1:5000"
CHAT_LOG_URL = f"{DASHBOARD_BASE}/api/log_chat"
EVENT_LOG_URL = f"{DASHBOARD_BASE}/api/log_event"


def log_chat(user_text: str, emotion: str, bot_reply: str):
    payload = {
        "user_text": user_text,
        "emotion": emotion,
        "bot_reply": bot_reply,
    }
    try:
        requests.post(CHAT_LOG_URL, json=payload, timeout=1)
    except Exception as e:
        print("[LOG_CHAT] Failed to log chat:", e)


def log_event(event_type: str, details: dict):
    payload = {
        "event_type": event_type,
        "details": details,
    }
    try:
        requests.post(EVENT_LOG_URL, json=payload, timeout=1)
    except Exception as e:
        print("[LOG_EVENT] Failed to log event:", e)


def main_loop():
    # ============================================================
    # Hardware Initialization (Assignment 3 Pin Assignments)
    # ============================================================
    
    # LED Controller - GPIO pin 26 (common PWM pin, configurable)
    # Note: Update with your Assignment 3 LED pin if different
    led = LEDController(led_pin=26)
    
    # Photoresistor - ADC channel 4 (MCP3208 via SPI)
    photoresistor = Photoresistor(
        adc_channel=4,
        log_callback=lambda et, d: log_event(et, d)
    )
    
    # Speaker for ambient music
    speaker = Speaker(music_dir="assets/music")
    
    # Ambient Music Controller
    ambient_music = AmbientMusic(
        speaker=speaker,
        log_callback=lambda et, d: log_event(et, d)
    )
    
    # Camera Capture
    camera = CameraCapture(
        save_dir="proofs",
        log_callback=lambda et, d: log_event(et, d)
    )
    
    # Joystick callbacks
    def joystick_volume_callback(dir):
        """Joystick up/down: increase/decrease volume"""
        current_vol = speaker.get_volume()
        step = 0.05  # 5% steps
        new_vol = current_vol + (dir * step)
        new_vol = max(0.0, min(1.0, new_vol))
        ambient_music.set_volume(new_vol)
        speak(f"Volume set to {int(new_vol * 100)} percent")
    
    def joystick_track_callback(dir):
        """Joystick left/right: switch tracks"""
        if dir > 0:
            ambient_music.next_track()
            speak("Next track")
        else:
            ambient_music.previous_track()
            speak("Previous track")
    
    def joystick_play_pause_callback():
        """Joystick press: toggle play/pause"""
        ambient_music.toggle_play_pause()
        if speaker.is_playing:
            speak("Music paused")
        else:
            speak("Music playing")
    
    # Initialize joystick (ADC channels 0 and 1)
    joystick = Joystick(
        volume_callback=joystick_volume_callback,
        track_callback=joystick_track_callback,
        play_pause_callback=joystick_play_pause_callback,
        log_callback=lambda et, d: log_event(et, d)
    )
    joystick.start_polling()
    
    # Rotary encoder callback
    def rotary_callback(delta):
        """Rotary encoder: control volume or LED breathing speed"""
        # Control volume based on encoder rotation
        current_vol = speaker.get_volume()
        step = 0.02  # 2% steps per encoder step
        new_vol = current_vol + (delta * step)
        new_vol = max(0.0, min(1.0, new_vol))
        ambient_music.set_volume(new_vol)
        print(f"[Rotary] Volume adjusted to {new_vol:.2f}")
    
    # Initialize rotary encoder (gpiochip2 lines 15 and 17)
    rotary = RotaryEncoder(
        value_change_callback=rotary_callback,
        log_callback=lambda et, d: log_event(et, d)
    )
    rotary.start_polling()
    
    # ============================================================
    # Safety System (Fall Detection & Health Alert)
    # ============================================================
    
    # Health Alert System
    health_alert = HealthAlert(
        speak_callback=speak,
        listen_callback=listen,
        log_callback=lambda et, d: log_event(et, d)
    )
    
    # Fall Detector callback
    def fall_detected_callback():
        """Called when fall is detected - trigger health check"""
        print("[MAIN] Fall detected! Initiating health check...")
        health_alert.check_on_user()
    
    # Initialize fall detector (uses accelerometer ADC channels 2, 3, 7)
    fall_detector = FallDetector(
        fall_callback=fall_detected_callback,
        log_callback=lambda et, d: log_event(et, d)
    )
    fall_detector.start_monitoring()
    
    # ============================================================
    # Existing Module Instances
    # ============================================================
    pomodoro = PomodoroTimer(
        focus_seconds=20,      # SHORT for demo!
        break_seconds=5,
        speak_callback=speak,
        log_event_callback=lambda et, d: log_event(et, d),
    )

    meditation = MeditationBreather(
        led_pin=26,          # Use same LED pin
        speak_callback=speak,
    )
    
    # ============================================================
    # Ambient Light Monitoring Thread
    # ============================================================
    def ambient_light_monitor():
        """Periodically read ambient light and optionally auto-start music"""
        LIGHT_CHECK_INTERVAL = 5.0  # Check every 5 seconds
        DARK_THRESHOLD = 0.3  # Below this is considered dark
        last_light_value = None
        
        while True:
            try:
                normalized = photoresistor.read_normalized()
                
                # Auto-start calm music if environment gets dark
                if normalized < DARK_THRESHOLD:
                    if not ambient_music.is_playing() and (last_light_value is None or last_light_value >= DARK_THRESHOLD):
                        print(f"[AmbientLight] Environment is dark ({normalized:.2f}), auto-starting calm music")
                        ambient_music.start()
                
                last_light_value = normalized
                time.sleep(LIGHT_CHECK_INTERVAL)
            except Exception as e:
                print(f"[AmbientLight] Error in monitor: {e}")
                time.sleep(LIGHT_CHECK_INTERVAL)
    
    light_monitor_thread = threading.Thread(target=ambient_light_monitor, daemon=True)
    light_monitor_thread.start()
    
    # ============================================================
    # Welcome Message
    # ============================================================
    speak("Hi, I'm your therapy assistant. You can chat with me, say 'start focus' for a focus session, 'start meditation' for breathing, 'play music' for ambient music, 'capture' for a photo, 'check light' to see ambient light level, or 'test alert' to test Discord alerts. Type 'quit' when you're done. I'm also monitoring for falls and will check on you if needed.")

    # ============================================================
    # Main Command Loop
    # ============================================================
    while True:
        user_text = listen()
        if not user_text:
            continue

        lowered = user_text.lower().strip()

        # Exit condition
        if lowered in {"quit", "exit", "bye"}:
            speak("Okay, I'll rest now. Good job today.")
            log_event("session_end", {"reason": "user_quit"})
            break

        # Command: Ambient Music Start
        if "play music" in lowered or "calm me" in lowered or "start ambient" in lowered or "relax" in lowered:
            speak("Starting calming ambient music.")
            ambient_music.start()
            continue
        
        # Command: Stop Music
        if "stop music" in lowered or "stop ambient" in lowered:
            speak("Stopping music.")
            ambient_music.stop()
            continue
        
        # Command: Camera Capture
        if "capture" in lowered or "take picture" in lowered or "camera" in lowered:
            speak("Taking a picture now.")
            result = camera.capture_frame()
            if result:
                speak(f"Picture saved successfully.")
            else:
                speak("Sorry, I couldn't take the picture.")
            continue
        
        # Command: Check Light
        if "check light" in lowered or "ambient light" in lowered:
            normalized = photoresistor.read_normalized()
            percentage = int(normalized * 100)
            if normalized < 0.3:
                speak(f"Ambient light is very dark, about {percentage} percent.")
            elif normalized < 0.6:
                speak(f"Ambient light is moderate, about {percentage} percent.")
            else:
                speak(f"Ambient light is bright, about {percentage} percent.")
            continue
        
        # Command: Test Discord Alert
        if "test alert" in lowered or "test discord" in lowered:
            speak("Sending a test Discord alert to verify configuration.")
            success = health_alert.test_discord_alert()
            if success:
                speak("Test alert sent successfully. Check your Discord channel.")
            else:
                speak("Failed to send test alert. Check your Discord webhook configuration.")
            continue

        # Command: Pomodoro / focus
        if "pomodoro" in lowered or "focus" in lowered or "study" in lowered:
            speak("Got it. I'll start a short focus session for this demo.")
            log_event("pomodoro_requested", {"source": "user_text", "text": user_text})
            pomodoro.run_demo_session()
            # After focus, continue back to chatting
            continue

        # Command: Meditation / breathing
        if "meditation" in lowered or "meditate" in lowered or "breathe" in lowered:
            speak("Okay, let's do a short breathing exercise together.")
            log_event("meditation_requested", {"source": "user_text", "text": user_text})
            # Use LED breathing during meditation
            stop_event = led.breathing(cycles=6, duration=4.0)
            meditation.run_breathing_demo(cycles=3, step_delay=0.2)
            led.stop_breathing()
            continue

        # Normal AI chat flow
        emotion = analyze_emotion(user_text)
        print(f"[MAIN] Detected emotion: {emotion}")

        bot_reply = chat_with_gemini(user_text, emotion)
        speak(bot_reply)
        log_chat(user_text, emotion, bot_reply)
    
    # Cleanup on exit
    print("[MAIN] Cleaning up hardware...")
    fall_detector.cleanup()
    joystick.cleanup()
    rotary.cleanup()
    photoresistor.cleanup()
    led.cleanup()
    speaker.cleanup()
    camera.cleanup()


if __name__ == "__main__":
    main_loop()
