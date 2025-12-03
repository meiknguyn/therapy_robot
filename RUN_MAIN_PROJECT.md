# Running the Main Therapy Robot Project

Complete guide to run the main therapy robot application.

## Prerequisites

1. Virtual environment set up (see `QUICK_START.md`)
2. Gemini API key obtained
3. Hardware permissions fixed (see `QUICK_START.md`)

## Quick Start

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main
```

## Detailed Steps

### Step 1: Navigate to Parent Directory

**Important:** The project must be run from `/home/mike`, not from inside `/home/mike/therapy_robot`.

```bash
cd /home/mike
```

### Step 2: Activate Virtual Environment

```bash
source therapy_robot/venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 3: Set Gemini API Key

**Option A: Export Environment Variable**
```bash
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

**Option B: Use .env File**

Create `.env` file in project root:
```bash
cd /home/mike/therapy_robot
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env
```

Then the key will be loaded automatically.

**Option C: Add to ~/.bashrc (Persistent)**

```bash
echo 'export GEMINI_API_KEY="YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Run the Main Project

```bash
python -m therapy_robot.main
```

Or if you're in the project directory with PYTHONPATH set:
```bash
cd /home/mike/therapy_robot
export PYTHONPATH=/home/mike:$PYTHONPATH
python main.py
```

## Expected Output

When starting, you should see:

```
Starting Therapy Robot
==================================================
✓ LED controller initialized
✓ Photoresistor initialized
✓ Accelerometer initialized
✓ Joystick initialized
✓ Rotary button initialized
✓ Volume control (joystick Y-axis) active
   Step size: 5%, Hold time: 0.5s
   🔊 Current Volume: 60% [████████████░░░░░░░░]
✓ Goodnight feature initialized
✓ Goodnight monitor thread started
✓ Pomodoro feature initialized
✓ Breathing exercise feature initialized
✓ Alarm feature initialized
✓ Safety feature initialized and monitoring
✓ Volume sync thread started (dashboard ↔ main program)
```

If you see warnings (⚠), those features will be disabled but the robot will still work.

## Interacting with the Robot

### Basic Chat

1. Type your message and press **Enter**
2. The robot will analyze your mood and respond
3. Continue the conversation naturally

### Ending the Session

- Type **"quit"**, **"exit"**, or **"bye"**
- Press **Ctrl+C** to interrupt

### Special Voice Commands

#### Music Commands

- **"play my favorite song"** - Plays your favorite song on loop
- **"stop the music"** - Stops any currently playing music

#### Study Commands

- **"i need to focus"** or **"start studying"** - Starts Pomodoro study session
  - LED will breathe during study time
  - LED will flash during rest breaks
- **"stop studying"** - Stops Pomodoro session

#### Breathing Exercise

- **"breathing exercise"** or **"let's breathe"** - Starts guided breathing
  - LED brightens for inhale
  - LED breathes for hold
  - LED flashes rapidly for exhale
- **"stop breathing"** - Stops breathing exercise

#### Alarm Commands

- **"set alarm at 14:30"** - Sets alarm for specific time
- **"wake me up in 30 minutes"** - Sets alarm in X minutes
- **"wake me up in 5 minutes"** - Sets alarm in X minutes
- **"cancel alarm"** - Cancels set alarm

#### Safety Commands

- **"stop fall detection"** - Disables fall detection temporarily

## Hardware Features

### Volume Control (Joystick)

- **Push joystick UP** - Increase volume (hold for 0.5s)
- **Push joystick DOWN** - Decrease volume (hold for 0.5s)
- Volume changes are shown with a visual bar
- Volume syncs with dashboard

### Goodnight Feature (Automatic)

- Automatically plays calming music when room gets dark
- Monitors ambient light via photoresistor
- Stops when light returns

### Safety Feature (Automatic)

- Monitors for falls via accelerometer
- Triggers LED alerts if fall detected
- Asks for confirmation you're okay

## Running in Background

To run the main project in the background:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
nohup python -m therapy_robot.main > therapy_robot.log 2>&1 &
```

View logs:
```bash
tail -f therapy_robot.log
```

Stop background process:
```bash
pkill -f "therapy_robot.main"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'therapy_robot'"

**Cause:** Running from wrong directory.

**Solution:** Run from `/home/mike`, not from inside the project folder.

```bash
cd /home/mike
python -m therapy_robot.main
```

### Hardware Not Initializing

**Cause:** Permission denied errors.

**Solution:** Fix permissions (see `QUICK_START.md` section on permissions).

### No Response from Robot

**Cause:** Gemini API key not set or invalid.

**Solution:** 
1. Check API key is set: `echo $GEMINI_API_KEY`
2. Verify key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Check for API errors in output

### Volume Control Not Working

**Cause:** Joystick not initialized or permissions issue.

**Solution:**
1. Check joystick initialized message on startup
2. Fix SPI permissions if needed
3. Try moving joystick more slowly

## Logs

All interactions are logged to:
- **Chats:** `/home/mike/therapy_robot/logs/chats.csv`
- **Events:** `/home/mike/therapy_robot/logs/events.csv`
- **Volume:** `/home/mike/therapy_robot/logs/volume.txt`

View recent chats:
```bash
tail -20 /home/mike/therapy_robot/logs/chats.csv
```

## Integration with Dashboard

The main project automatically syncs with the dashboard:
- Volume changes sync bidirectionally
- All chats are logged for dashboard viewing
- Events are logged for dashboard display

Run the dashboard in a separate terminal to view real-time data.

## Next Steps

- See `RUN_DASHBOARD.md` for running the web dashboard
- See `QUICK_START.md` for complete setup guide
- See `PROJECT_SUMMARY.md` for feature documentation

