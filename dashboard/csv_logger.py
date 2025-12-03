"""Thread-safe CSV logging for events and chats."""

import csv
import threading
from datetime import datetime
from pathlib import Path

from therapy_robot import config

# Thread locks for file operations
_event_lock = threading.Lock()
_chat_lock = threading.Lock()


def _ensure_csv_file(file_path: Path, header: list):
    """Ensure CSV file exists with header row."""
    if not file_path.exists():
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)


def log_event(event_type: str, details: dict | None = None):
    """
    Log an event to events.csv.
    
    Args:
        event_type: Type of event (e.g., "ambient_light", "led_change")
        details: Optional dictionary with event details
    """
    _ensure_csv_file(config.EVENT_LOG_PATH, ["timestamp", "event_type", "details"])
    
    timestamp = datetime.now().isoformat()
    details_str = str(details) if details else ""
    
    with _event_lock:
        with open(config.EVENT_LOG_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_type, details_str])


def log_chat(user_text: str, emotion_score: int, bot_reply: str):
    """
    Log a chat interaction to chats.csv.
    
    Args:
        user_text: User's input text
        emotion_score: Emotion score (1-10)
        bot_reply: Bot's response
    """
    _ensure_csv_file(config.CHAT_LOG_PATH, ["timestamp", "user_text", "emotion_score", "bot_reply"])
    
    timestamp = datetime.now().isoformat()
    
    with _chat_lock:
        with open(config.CHAT_LOG_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, user_text, emotion_score, bot_reply])

