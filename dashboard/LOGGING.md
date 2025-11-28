# Event Logging System

## Overview

The therapy robot automatically logs all events and chat interactions to both the web dashboard and CSV files for long-term storage and analysis.

## CSV Log Files

All logs are saved in the `logs/` directory:

### `logs/events.csv`
Contains all system events with the following columns:
- `timestamp`: Date and time of the event (YYYY-MM-DD HH:MM:SS)
- `event_type`: Type of event (e.g., "fall_detected", "ambient_music_start", "camera_capture")
- `details_json`: JSON string containing event-specific details

### `logs/chats.csv`
Contains all chat interactions with the following columns:
- `timestamp`: Date and time of the chat (YYYY-MM-DD HH:MM:SS)
- `user_text`: User's message
- `emotion`: Detected emotion from user's message
- `bot_reply`: Bot's response

## Event Types

The system logs various event types:

### Safety Events
- `fall_detected`: Fall detected by accelerometer
- `health_check_initiated`: Health check started after fall
- `health_check_passed`: User confirmed they're okay
- `health_check_failed`: User needs assistance
- `discord_alert_sent`: Discord alert was sent

### Hardware Events
- `ambient_light`: Photoresistor reading
- `rotary_encoder_rotate`: Rotary encoder rotation
- `ambient_music_change`: Track switched

### Module Events
- `ambient_music_start`: Ambient music started
- `ambient_music_stop`: Ambient music stopped
- `ambient_music_volume_change`: Volume adjusted
- `camera_capture`: Photo taken

### Session Events
- `pomodoro_requested`: Focus session requested
- `pomodoro_start`: Focus session started
- `pomodoro_end`: Focus session ended
- `meditation_requested`: Meditation requested
- `session_end`: Session ended

## Web Dashboard

Access the dashboard at: `http://127.0.0.1:5000/`

Features:
- Real-time display of all events and chats
- Auto-refreshes every 5 seconds
- Formatted event details for easy reading
- Download CSV files directly from the dashboard
- Statistics on total events and chats

## CSV File Format

CSV files use:
- UTF-8 encoding
- Standard CSV format (comma-separated)
- JSON strings for complex details
- Headers in the first row

### Example Event Entry

```csv
timestamp,event_type,details_json
2024-11-28 10:30:15,fall_detected,"{""magnitude"": 0.85, ""delta"": 0.42, ""x"": 1800, ""y"": 2200, ""z"": 2500}"
```

### Example Chat Entry

```csv
timestamp,user_text,emotion,bot_reply
2024-11-28 10:25:30,"I feel stressed today","anxiety","I understand you're feeling stressed. Let's try some breathing exercises together."
```

## Accessing Logs

### From Web Dashboard
1. Open `http://127.0.0.1:5000/`
2. Click "Download Events CSV" or "Download Chats CSV" buttons

### Direct File Access
CSV files are stored in: `therapy_robot/logs/`

You can open them with:
- Excel
- Google Sheets
- Any text editor
- Python pandas
- Any CSV viewer

### Programmatic Access

```python
import pandas as pd

# Read events
events_df = pd.read_csv('logs/events.csv')
print(events_df.head())

# Read chats
chats_df = pd.read_csv('logs/chats.csv')
print(chats_df.head())
```

## Log Management

- CSV files are automatically created when first event/chat is logged
- Files append new entries (they don't overwrite)
- Files persist across sessions
- No automatic rotation (you can archive old files manually)

## Thread Safety

The CSV logger is thread-safe, so multiple events can be logged simultaneously without corruption.

## Troubleshooting

**CSV files not created?**
- Check that the `logs/` directory exists (it's created automatically)
- Verify write permissions for the directory
- Check console output for CSV logging errors

**Missing events?**
- Ensure dashboard is running
- Check that `log_event()` is being called
- Verify network connection if dashboard is on a different machine

**Large CSV files?**
- Archive old logs periodically
- Consider splitting by date if needed
- Use database instead for very high volume

