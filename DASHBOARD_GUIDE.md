# Therapy Robot Dashboard - Testing Guide

## Overview

The dashboard system logs all therapy robot interactions and events to CSV files, and provides tools to view and analyze this data.

## Dashboard Components

1. **CSV Logger** (`dashboard/csv_logger.py`)
   - Logs events (LED changes, ambient light readings, etc.)
   - Logs chat interactions (user messages, mood scores, bot replies)
   - Thread-safe logging

2. **Mental Health Analyzer** (`dashboard/mental_health_analyzer.py`)
   - Computes statistics from chat logs
   - Analyzes mood trends
   - Provides basic analytics

## Log Files

- **Events**: `/home/mike/therapy_robot/logs/events.csv`
  - Columns: `timestamp`, `event_type`, `details`
  
- **Chats**: `/home/mike/therapy_robot/logs/chats.csv`
  - Columns: `timestamp`, `user_text`, `emotion_score`, `bot_reply`

## Testing the Dashboard

### 1. Run the Dashboard Test Suite

Comprehensive test that verifies all dashboard functionality:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_dashboard.py
```

**What it does:**
- Tests CSV logging (events and chats)
- Displays logged events with statistics
- Displays chat interactions with mood analysis
- Computes dashboard statistics
- Shows summary view

### 2. View Dashboard (Interactive Viewer)

View your logs anytime with the interactive dashboard viewer:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/view_dashboard.py
```

**Options:**
```bash
# View everything (default)
python therapy_robot/view_dashboard.py

# View only statistics
python therapy_robot/view_dashboard.py --stats

# View only recent chats
python therapy_robot/view_dashboard.py --chats

# View only events
python therapy_robot/view_dashboard.py --events

# Limit number of items shown
python therapy_robot/view_dashboard.py --limit 5
```

### 3. Generate Test Data

Run the main program to generate real log data:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key_here'
python -m therapy_robot.main
```

Then interact with the chatbot - all conversations will be logged automatically.

### 4. Direct CSV Access

You can also view the CSV files directly:

```bash
# View events
cat /home/mike/therapy_robot/logs/events.csv

# View chats
cat /home/mike/therapy_robot/logs/chats.csv

# Or use pandas in Python
python -c "
import pandas as pd
from therapy_robot import config
df = pd.read_csv(config.CHAT_LOG_PATH)
print(df)
"
```

## Dashboard Features

### Statistics Provided

- **Total Interactions**: Number of chat sessions
- **Average Mood**: Mean emotion score (1-10 scale)
- **Mood Range**: Min and max mood scores
- **Mood Distribution**: Histogram of mood scores
- **Trend Analysis**: Whether mood is improving, declining, or stable
- **Event Summary**: Breakdown of event types

### Example Output

```
📊 Chat Statistics:
  • Total interactions: 9
  • Average mood: 4.89/10
  • Mood range: 3/10 - 8/10
  • Mood std dev: 1.45
  • Trend: ➡️ Stable

📈 Mood Distribution:
   3/10: ██                     2 ( 22.2%)
   5/10: ██████                 6 ( 66.7%)
   8/10: █                      1 ( 11.1%)
```

## Programmatic Access

You can also use the dashboard modules in your own scripts:

```python
from therapy_robot.dashboard import csv_logger
from therapy_robot.dashboard.mental_health_analyzer import compute_basic_stats

# Log an event
csv_logger.log_event("custom_event", {"key": "value"})

# Log a chat
csv_logger.log_chat("User message", 7, "Bot response")

# Get statistics
stats = compute_basic_stats()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Average mood: {stats['average_mood']}")
print(f"Trend: {stats['trend']}")
```

## Troubleshooting

### No data in logs?

1. Make sure you've run the main program at least once
2. Check that log files exist:
   ```bash
   ls -la /home/mike/therapy_robot/logs/
   ```

### Import errors?

1. Make sure you're in the parent directory:
   ```bash
   cd /home/mike
   ```
2. Activate the virtual environment:
   ```bash
   source therapy_robot/venv/bin/activate
   ```

### Permission errors?

The dashboard only reads CSV files, so no special permissions are needed. If you can't read the files, check:
```bash
ls -la /home/mike/therapy_robot/logs/
```

## Quick Test Commands

```bash
# Full dashboard test
cd /home/mike && source therapy_robot/venv/bin/activate && python therapy_robot/test_dashboard.py

# Quick dashboard view
cd /home/mike && source therapy_robot/venv/bin/activate && python therapy_robot/view_dashboard.py --stats

# View last 5 chats
cd /home/mike && source therapy_robot/venv/bin/activate && python therapy_robot/view_dashboard.py --chats --limit 5
```

## Next Steps

- Run the main program to generate real therapy session data
- Use the dashboard viewer to track mood trends over time
- Analyze the CSV files for deeper insights
- Extend the mental health analyzer with more advanced analytics

