# Therapy Robot Web Dashboard - Quick Start Guide

## Overview

The web dashboard provides a beautiful, real-time view of your therapy robot's data through a web browser.

## Starting the Web Dashboard

### Method 1: Run directly

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

### Method 2: Run in background

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py &
```

### Method 3: Run as a service (persistent)

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > dashboard.log 2>&1 &
```

## Accessing the Dashboard

### From the BeagleY-AI board (local)

Open a web browser on the board and go to:
```
http://localhost:5000
```

### From another computer on the network

1. **Find your BeagleY-AI's IP address:**
   ```bash
   hostname -I
   # or
   ip addr show | grep "inet "
   ```

2. **Open browser on your computer and go to:**
   ```
   http://<beagle-ip>:5000
   ```
   Replace `<beagle-ip>` with the IP address from step 1.

   Example: `http://192.168.1.100:5000`

## Dashboard Features

### Main Dashboard (`/`)
- **Statistics Cards**: Total interactions, average mood, trend, total events
- **Recent Chat Interactions**: Last 10 conversations with mood scores
- **Recent Events**: Last 10 system events
- **Auto-refresh**: Click the refresh button to update data

### API Endpoint (`/api/stats`)
Returns JSON data for programmatic access:
```bash
curl http://localhost:5000/api/stats
```

## Testing the Dashboard

### 1. Check if server is running

```bash
# Check if port 5000 is listening
netstat -tlnp | grep 5000

# Or test with curl
curl http://localhost:5000
```

### 2. Test from command line

```bash
# Test the main page
curl http://localhost:5000 | head -20

# Test the API endpoint
curl http://localhost:5000/api/stats
```

### 3. Test from browser

1. Start the server (see above)
2. Open browser to `http://localhost:5000` (or your BeagleY-AI IP)
3. You should see the dashboard with statistics and data

## Stopping the Server

### If running in foreground:
Press `Ctrl+C`

### If running in background:
```bash
# Find the process
ps aux | grep web_app.py

# Kill it
kill <PID>

# Or kill all Python web_app processes
pkill -f web_app.py
```

## Troubleshooting

### Port already in use

If you see "Address already in use":
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill it
kill <PID>
```

### Can't access from another computer

1. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 5000
   ```

2. **Check if server is bound to 0.0.0.0:**
   The server should be running with `host='0.0.0.0'` (which it is)

3. **Verify IP address:**
   ```bash
   hostname -I
   ```

### No data showing

1. **Generate some data first:**
   ```bash
   cd /home/mike/therapy_robot
   source venv/bin/activate
   export GEMINI_API_KEY='your_key_here'
   python -m therapy_robot.main
   ```
   Have a few conversations, then refresh the dashboard.

2. **Check log files exist:**
   ```bash
   ls -la /home/mike/therapy_robot/logs/
   ```

### Import errors

Make sure you're running from the correct directory:
```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

## Example Usage

### Start dashboard and leave it running:
```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > /tmp/dashboard.log 2>&1 &
echo "Dashboard running at http://$(hostname -I | awk '{print $1}'):5000"
```

### View dashboard logs:
```bash
tail -f /tmp/dashboard.log
```

### Quick test:
```bash
# Start server
cd /home/mike/therapy_robot && source venv/bin/activate && python dashboard/web_app.py &

# Wait a moment, then test
sleep 2
curl http://localhost:5000/api/stats
```

## Security Note

⚠️ **Important**: The dashboard is currently set to `debug=True` and accessible from any network interface (`0.0.0.0`). For production use:

1. Set `debug=False`
2. Consider adding authentication
3. Use a reverse proxy (nginx) with SSL
4. Restrict access to local network only

## Next Steps

- Run therapy sessions to generate data
- View the dashboard to see real-time statistics
- Use the API endpoint for custom integrations
- Customize the dashboard HTML/CSS as needed

