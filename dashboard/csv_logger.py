# dashboard/csv_logger.py
"""
CSV Logger Module
Logs all events and chats to CSV files with timestamps.
"""
import os
import csv
import threading
from datetime import datetime
from pathlib import Path


class CSVLogger:
    """
    Thread-safe CSV logger for events and chats.
    Creates separate CSV files for events and chats.
    """

    def __init__(self, logs_dir="logs"):
        """
        Initialize CSV logger.
        
        Args:
            logs_dir: Directory to store CSV log files
        """
        self.logs_dir = logs_dir
        self.lock = threading.Lock()
        
        # Ensure logs directory exists
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
        
        # CSV file paths
        self.events_csv = os.path.join(self.logs_dir, "events.csv")
        self.chats_csv = os.path.join(self.logs_dir, "chats.csv")
        
        # Initialize CSV files with headers if they don't exist
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Initialize CSV files with headers if they don't exist."""
        # Events CSV
        if not os.path.exists(self.events_csv):
            with open(self.events_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "event_type",
                    "details_json"
                ])
        
        # Chats CSV
        if not os.path.exists(self.chats_csv):
            with open(self.chats_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "user_text",
                    "emotion",
                    "bot_reply"
                ])
    
    def log_event(self, event_type: str, details: dict, timestamp: str = None):
        """
        Log an event to CSV.
        
        Args:
            event_type: Type of event (e.g., "fall_detected", "ambient_music_start")
            details: Dictionary with event details
            timestamp: Optional timestamp string (if None, uses current time)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert details dict to JSON string for CSV storage
        import json
        details_json = json.dumps(details, ensure_ascii=False)
        
        with self.lock:
            try:
                with open(self.events_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        event_type,
                        details_json
                    ])
                print(f"[CSV] Logged event: {event_type}")
            except Exception as e:
                print(f"[CSV] Error logging event: {e}")
    
    def log_chat(self, user_text: str, emotion: str, bot_reply: str, timestamp: str = None):
        """
        Log a chat interaction to CSV.
        
        Args:
            user_text: User's message
            emotion: Detected emotion
            bot_reply: Bot's response
            timestamp: Optional timestamp string (if None, uses current time)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.lock:
            try:
                with open(self.chats_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp,
                        user_text,
                        emotion,
                        bot_reply
                    ])
                print(f"[CSV] Logged chat: {emotion}")
            except Exception as e:
                print(f"[CSV] Error logging chat: {e}")
    
    def get_events_count(self):
        """Get total number of events logged."""
        try:
            with open(self.events_csv, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except:
            return 0
    
    def get_chats_count(self):
        """Get total number of chats logged."""
        try:
            with open(self.chats_csv, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except:
            return 0

