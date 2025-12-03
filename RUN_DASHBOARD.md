# Running the Therapy Robot Dashboard

Complete guide to run the web dashboard for monitoring therapy sessions.

## Quick Start

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

Then open `http://localhost:5000` in your browser.

## Detailed Steps

### Step 1: Navigate to Project Directory

```bash
cd /home/mike/therapy_robot
```

### Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 3: Run Dashboard

```bash
python dashboard/web_app.py
```

## Expected Output

```
============================================================
Starting Therapy Robot Web Dashboard...
============================================================

🌐 Dashboard available at:
   Local:    http://localhost:5000
   Network:  http://0.0.0.0:5000

📊 API endpoint:
   http://localhost:5000/api/stats

⚠️  Press Ctrl+C to stop the server
============================================================

 * Serving Flask app 'web_app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.XXX:5000
Press CTRL+C to quit
```

## Accessing the Dashboard

### From BeagleY-AI Board (Local)

Open a web browser on the board:
```
http://localhost:5000
```

### From Another Computer on Network

1. **Find your BeagleY-AI's IP address:**
   ```bash
   hostname -I
   # or
   ip addr show | grep "inet "
   ```

2. **Open browser on your computer:**
   ```
   http://<beagle-ip>:5000
   ```
   
   Example: `http://192.168.1.100:5000`

## Running Modes

### Foreground (Interactive)

Best for testing and development:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

Press **Ctrl+C** to stop.

### Background (Detached)

Run in background and continue using terminal:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > dashboard.log 2>&1 &
```

View logs:
```bash
tail -f dashboard.log
```

### Service Mode (Persistent)

Run as a service that survives terminal closure:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > /tmp/dashboard.log 2>&1 &
echo "Dashboard PID: $!"
```

## Dashboard Features

### Main Dashboard Page (`/`)

- **Statistics Cards:**
  - Total Interactions
  - Average Mood Score
  - Mood Trend (Improving/Declining/Stable)
  - Total Events

- **Recent Chat Interactions:**
  - Last 10 conversations
  - Mood scores for each
  - Timestamps

- **Recent Events:**
  - Last 10 system events
  - Event types and details
  - Timestamps

- **Volume Control:**
  - Slider to adjust volume
  - Real-time volume display
  - Syncs with main program

- **Chat Interface:**
  - Chat directly with therapy robot
  - View conversation history
  - See mood scores in real-time

### Auto-Refresh

- Click **"🔄 Refresh Now"** to manually refresh
- Click **"▶️ Enable Auto-Refresh"** for automatic updates every 5 seconds

### API Endpoints

**Get Statistics (JSON):**
```bash
curl http://localhost:5000/api/stats
```

**Get Recent Chats (JSON):**
```bash
curl http://localhost:5000/api/chats
```

**Get Recent Events (JSON):**
```bash
curl http://localhost:5000/api/events
```

**Get Current Volume:**
```bash
curl http://localhost:5000/api/volume
```

**Set Volume:**
```bash
curl -X POST http://localhost:5000/api/volume \
  -H "Content-Type: application/json" \
  -d '{"volume": 0.8}'
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

## Stopping the Dashboard

### If Running in Foreground

Press **Ctrl+C**

### If Running in Background

**Find the process:**
```bash
ps aux | grep web_app.py
```

**Kill by PID:**
```bash
kill <PID>
```

**Kill all web_app processes:**
```bash
pkill -f web_app.py
```

**Kill by port:**
```bash
sudo lsof -i :5000
kill <PID>
```

## Troubleshooting

### Port 5000 Already in Use

**Find what's using the port:**
```bash
sudo lsof -i :5000
```

**Kill the process:**
```bash
kill <PID>
```

**Or use a different port:**

Edit `dashboard/web_app.py` and change:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```
to:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Can't Access from Another Computer

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 5000
```

**Verify server is bound to 0.0.0.0:**
The server should show:
```
Running on all addresses (0.0.0.0)
```

**Check IP address:**
```bash
hostname -I
```

### No Data Showing

**Generate data first:**
1. Run the main project to create log files
2. Have a few conversations
3. Refresh the dashboard

**Check log files exist:**
```bash
ls -la /home/mike/therapy_robot/logs/
```

Should see:
- `chats.csv`
- `events.csv`
- `volume.txt`

**Check file permissions:**
```bash
ls -l /home/mike/therapy_robot/logs/
```

### Import Errors

**Make sure you're in the correct directory:**
```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

**Check virtual environment is activated:**
You should see `(venv)` in your prompt.

### Dashboard Shows Old Data

**Clear browser cache** or do a hard refresh:
- **Chrome/Firefox:** Ctrl+Shift+R
- **Safari:** Cmd+Shift+R

**Or manually refresh:**
Click the "🔄 Refresh Now" button on the dashboard.

## Integration with Main Project

The dashboard reads data from CSV log files created by the main project:

- **Chats:** `/home/mike/therapy_robot/logs/chats.csv`
- **Events:** `/home/mike/therapy_robot/logs/events.csv`
- **Volume:** `/home/mike/therapy_robot/logs/volume.txt`

### Volume Sync

Volume changes sync bidirectionally:
- Changes in dashboard → saved to `volume.txt` → main program reads it
- Changes in main program → saved to `volume.txt` → dashboard reads it

### Real-Time Updates

- Dashboard polls for new data every 5 seconds (if auto-refresh enabled)
- Manual refresh updates immediately
- Chat interface sends messages in real-time

## Security Notes

⚠️ **Important:** The dashboard is currently set to `debug=True` and accessible from any network interface (`0.0.0.0`).

For production use:
1. Set `debug=False` in `dashboard/web_app.py`
2. Consider adding authentication
3. Use a reverse proxy (nginx) with SSL
4. Restrict access to local network only

## Viewing Logs

**Dashboard application logs:**
```bash
tail -f dashboard.log
```

**Chat logs:**
```bash
tail -20 /home/mike/therapy_robot/logs/chats.csv
```

**Event logs:**
```bash
tail -20 /home/mike/therapy_robot/logs/events.csv
```

## Next Steps

- See `RUN_MAIN_PROJECT.md` for running the main therapy robot
- See `QUICK_START.md` for complete setup guide
- See `WEB_DASHBOARD_GUIDE.md` for detailed dashboard documentation

