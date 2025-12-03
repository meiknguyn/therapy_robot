# Dashboard Real-Time Sync Guide

## How It Works

The dashboard automatically syncs with your therapy robot data! Here's how:

### Data Flow

1. **Therapy Robot** (`main.py`) logs all interactions to CSV files:
   - `logs/chats.csv` - Every conversation
   - `logs/events.csv` - All system events

2. **Dashboard** reads from the same CSV files in real-time
   - Every page load = fresh data
   - API endpoints update instantly

3. **Auto-Refresh** keeps the dashboard updated automatically

## Using the Dashboard

### Method 1: Manual Refresh (Default)

1. Open the dashboard: `http://localhost:5000`
2. Click **"🔄 Refresh Now"** button whenever you want to see latest data
3. The page reloads with fresh data from CSV files

### Method 2: Auto-Refresh (Recommended)

1. Open the dashboard: `http://localhost:5000`
2. Click **"▶️ Enable Auto-Refresh"** button
3. Dashboard automatically refreshes every 5 seconds
4. Button changes to **"⏸️ Auto-Refresh ON (5s)"**
5. Click again to disable

### Method 3: Browser Auto-Refresh

Some browsers have extensions that auto-refresh pages:
- Chrome: "Auto Refresh" extension
- Firefox: "ReloadEvery" extension

## Testing Real-Time Sync

### Step 1: Start the Dashboard

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

### Step 2: Open Dashboard in Browser

Go to: `http://localhost:5000` (or your BeagleY-AI IP)

### Step 3: Start a Therapy Session

In another terminal:
```bash
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key_here'
python -m therapy_robot.main
```

### Step 4: Watch the Dashboard Update

- **With Auto-Refresh ON**: New conversations appear automatically every 5 seconds
- **With Manual Refresh**: Click "Refresh Now" after each conversation

## API Endpoints for Real-Time Data

You can also fetch data programmatically:

```bash
# Get statistics
curl http://localhost:5000/api/stats

# Get recent chats
curl http://localhost:5000/api/chats

# Get recent events
curl http://localhost:5000/api/events
```

## How Data Appears

### When you chat with the robot:

1. You type a message → Robot responds
2. `csv_logger.log_chat()` writes to `logs/chats.csv`
3. Dashboard reads from `logs/chats.csv` on next refresh
4. New conversation appears in the dashboard!

### Timeline:

- **0s**: You chat with robot → Data logged to CSV
- **0-5s**: Dashboard auto-refreshes (if enabled)
- **5s**: New data appears in dashboard

## Troubleshooting

### Dashboard not updating?

1. **Check if CSV files are being written:**
   ```bash
   tail -f /home/mike/therapy_robot/logs/chats.csv
   ```
   Run the therapy robot and you should see new lines appear.

2. **Check dashboard is reading files:**
   ```bash
   curl http://localhost:5000/api/stats
   ```
   Should return current statistics.

3. **Force refresh:**
   - Click "Refresh Now" button
   - Or press F5 in browser
   - Or enable auto-refresh

### Data appears delayed?

- CSV files are written immediately when you chat
- Dashboard reads files on each page load
- Auto-refresh updates every 5 seconds
- For instant updates, click "Refresh Now"

### No data showing?

1. **Make sure you've had conversations:**
   ```bash
   # Check if chats.csv has data
   wc -l /home/mike/therapy_robot/logs/chats.csv
   ```

2. **Check file permissions:**
   ```bash
   ls -la /home/mike/therapy_robot/logs/
   ```

## Best Practices

1. **Keep dashboard open** while using therapy robot
2. **Enable auto-refresh** for real-time monitoring
3. **Use two terminals**: One for robot, one for dashboard
4. **Or use two browser tabs**: One for robot (if web-based), one for dashboard

## Example Workflow

```bash
# Terminal 1: Start Dashboard
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py

# Terminal 2: Start Therapy Robot
cd /home/mike/therapy_robot
source venv/bin/activate
export GEMINI_API_KEY='your_key'
python -m therapy_robot.main

# Browser: Open http://localhost:5000
# Enable auto-refresh
# Watch data update in real-time!
```

## Summary

✅ **Dashboard syncs automatically** - Reads from CSV files on each refresh  
✅ **Auto-refresh available** - Updates every 5 seconds  
✅ **Manual refresh** - Click button anytime  
✅ **API endpoints** - Programmatic access to data  
✅ **Real-time data** - See conversations as they happen  

The dashboard is always in sync with your therapy robot data!

