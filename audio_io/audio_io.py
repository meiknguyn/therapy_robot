# audio_io/audio_io.py
# Simple placeholder audio functions for milestone demo

def listen():
    """
    Simulates listening on the Beagle board.
    For now, just return a fixed string.
    Replace with real microphone code later.
    """
    print("[audio] Listening... (placeholder)")
    return input("You: ")   # Text input instead of microphone


def speak(text: str):
    """
    Simulates speaking on the Beagle board.
    Later we can add actual speakers or LEDs.
    """
    print(f"[robot]: {text}")
