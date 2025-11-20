# main.py
import requests

from ai.gemini_client import analyze_emotion, chat_with_gemini
from audio_io.audio_io import listen, speak

from modules.pomodoro import PomodoroTimer
from modules.meditation_led import MeditationBreather

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
    # Create module instances with callbacks wired in
    pomodoro = PomodoroTimer(
        focus_seconds=20,      # SHORT for demo!
        break_seconds=5,
        speak_callback=speak,
        log_event_callback=lambda et, d: log_event(et, d),
    )

    meditation = MeditationBreather(
        led_pin=None,          # set to a GPIO pin number later (e.g., 17 on Pi-like boards)
        speak_callback=speak,
    )

    speak("Hi, I'm your study assistant. You can chat with me, say 'start focus' for a short focus session, or 'start meditation' for a breathing exercise. Type 'quit' when you're done.")

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
            meditation.run_breathing_demo(cycles=3, step_delay=0.2)
            continue

        # Normal AI chat flow
        emotion = analyze_emotion(user_text)
        print(f"[MAIN] Detected emotion: {emotion}")

        bot_reply = chat_with_gemini(user_text, emotion)
        speak(bot_reply)
        log_chat(user_text, emotion, bot_reply)


if __name__ == "__main__":
    main_loop()
