# dashboard/csv_logger.py
"""
CSV Logger Module
Logs all events and chats to CSV files with timestamps.
Supports log rotation by size or daily.
"""
import os
import csv
import threading
from datetime import datetime
from pathlib import Path
import json

# Import config for rotation settings
try:
    from therapy_robot import config
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import config


class CSVLogger:
    """
    Thread-safe CSV logger for events and chats.
    Creates separate CSV files for events and chats.
    """

    def __init__(self, logs_dir=None):
        """
        Initialize CSV logger.
        
        Args:
            logs_dir: Directory to store CSV log files (uses config if None)
        """
        self.logs_dir = logs_dir or config.LOG_DIR
        self.lock = threading.Lock()
        self.rotation_enabled = config.LOG_ROTATION_ENABLED
        self.max_bytes = config.LOG_MAX_BYTES
        self.rotation_strategy = config.LOG_ROTATION_STRATEGY
        self.last_rotation_date = None
        
        # Ensure logs directory exists
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
        
        # CSV file paths
        self.events_csv = os.path.join(self.logs_dir, "events.csv")
        self.chats_csv = os.path.join(self.logs_dir, "chats.csv")
        
        # Initialize CSV files with headers if they don't exist
        self._init_csv_files()
        
        # Initialize rotation tracking
        if self.rotation_strategy == "daily":
            self.last_rotation_date = datetime.now().date()
    
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
    
    def _check_and_rotate(self, csv_file: str, headers: list):
        """
        Check if log rotation is needed and perform rotation if necessary.
        
        Args:
            csv_file: Path to CSV file to check
            headers: List of header column names
        """
        if not self.rotation_enabled:
            return
        
        with self.lock:
            try:
                if not os.path.exists(csv_file):
                    return
                
                should_rotate = False
                
                # Check rotation strategy
                if self.rotation_strategy == "size":
                    # Size-based rotation
                    file_size = os.path.getsize(csv_file)
                    if file_size >= self.max_bytes:
                        should_rotate = True
                        print(f"[CSV] Log file {csv_file} reached size limit ({file_size} bytes), rotating...")
                
                elif self.rotation_strategy == "daily":
                    # Daily rotation
                    current_date = datetime.now().date()
                    if self.last_rotation_date is None or current_date > self.last_rotation_date:
                        should_rotate = True
                        self.last_rotation_date = current_date
                        print(f"[CSV] Daily rotation triggered for {csv_file}")
                
                if should_rotate:
                    # Generate rotated filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.basename(csv_file)
                    name_without_ext = os.path.splitext(base_name)[0]
                    rotated_name = f"{name_without_ext}_{timestamp}.csv"
                    rotated_path = os.path.join(self.logs_dir, rotated_name)
                    
                    # Rename current file
                    os.rename(csv_file, rotated_path)
                    print(f"[CSV] Rotated {base_name} to {rotated_name}")
                    
                    # Create new file with headers
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                    
            except Exception as e:
                print(f"[CSV] Error during rotation: {e}")

    def log_event(self, event_type: str, details: dict, timestamp: str = None):
        """
        Log an event to CSV with rotation support.
        
        Args:
            event_type: Type of event (e.g., "fall_detected", "ambient_music_start")
            details: Dictionary with event details
            timestamp: Optional timestamp string (if None, uses current time)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert details dict to JSON string for CSV storage
        details_json = json.dumps(details, ensure_ascii=False)
        
        # Check and rotate if needed
        headers = ["timestamp", "event_type", "details_json"]
        self._check_and_rotate(self.events_csv, headers)
        
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
        Log a chat interaction to CSV with rotation support.
        
        Args:
            user_text: User's message
            emotion: Detected emotion
            bot_reply: Bot's response
            timestamp: Optional timestamp string (if None, uses current time)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check and rotate if needed
        headers = ["timestamp", "user_text", "emotion", "bot_reply"]
        self._check_and_rotate(self.chats_csv, headers)
        
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

