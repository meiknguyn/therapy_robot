# Therapy Robot - Quick Start Guide

Complete guide to set up and run the Therapy Robot project.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Fix Permissions](#fix-permissions)
3. [Run Main Project](#run-main-project)
4. [Run Dashboard](#run-dashboard)
5. [Run Both Together](#run-both-together)
6. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Step 1: Install Python Development Headers

```bash
sudo apt install python3.13-dev
```

**Note:** Adjust the version number (3.13) to match your Python version.

### Step 2: Set Up Virtual Environment

```bash
cd /home/mike/therapy_robot

# Option A: Use setup script (Recommended)
./setup.sh

# Option B: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for use in the next step

---

## Fix Permissions

### Fix SPI Permissions (Required for Photoresistor, Accelerometer, Joystick)

**Option 1: Quick Fix (Temporary)**
```bash
sudo chmod 666 /dev/spidev0.0
```

**Option 2: Create SPI Group (Persistent)**
```bash
# Create spi group
sudo groupadd spi

# Add your user to spi group
sudo usermod -a -G spi $USER

# Change SPI device permissions
sudo chgrp spi /dev/spidev0.0
sudo chmod 664 /dev/spidev0.0

# Activate new group (or logout/login)
newgrp spi
```

**Option 3: Udev Rule (Most Permanent - Survives Reboots)**
```bash
# Create udev rule
sudo bash -c 'echo "KERNEL==\"spidev0.0\", MODE=\"0666\"" > /etc/udev/rules.d/99-spi-permissions.rules'

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Fix GPIO Permissions (Usually Already Done)

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Activate group (or logout/login)
newgrp gpio
```

### Verify Permissions

```bash
# Check your groups
groups

# Check SPI device permissions
ls -l /dev/spidev0.0

# Check GPIO device permissions
ls -l /dev/gpiochip2
```

---

## Run Main Project

### Method 1: Run from Parent Directory (Recommended)

```bash
# Navigate to parent directory
cd /home/mike

# Activate virtual environment
source therapy_robot/venv/bin/activate

# Set Gemini API key
export GEMINI_API_KEY="YOUR_KEY_HERE"

# Run the main project
python -m therapy_robot.main
```

### Method 2: Run from Project Directory

```bash
# Navigate to project directory
cd /home/mike/therapy_robot

# Activate virtual environment
source venv/bin/activate

# Set Gemini API key
export GEMINI_API_KEY="YOUR_KEY_HERE"

# Set PYTHONPATH
export PYTHONPATH=/home/mike:$PYTHONPATH

# Run the main project
python main.py
```

### Using .env File (Alternative to export)

Create a `.env` file in the project root:

```bash
cd /home/mike/therapy_robot
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env
```

Then run:
```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python -m therapy_robot.main
```

### Interacting with the Robot

- Type your message and press **Enter**
- Type **"quit"**, **"exit"**, or **"bye"** to end the session
- Press **Ctrl+C** to interrupt

### Special Commands

- **"play my favorite song"** - Plays favorite song
- **"stop the music"** - Stops any playing music
- **"i need to focus"** - Starts Pomodoro study session
- **"breathing exercise"** - Starts breathing exercise
- **"set alarm at 14:30"** - Sets an alarm
- **"wake me up in 30 minutes"** - Sets alarm in X minutes

---

## Run Dashboard

### Method 1: Run in Foreground

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

### Method 2: Run in Background

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > dashboard.log 2>&1 &
```

### Method 3: Run as Service (Persistent)

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > /tmp/dashboard.log 2>&1 &
echo "Dashboard PID: $!"
```

### Access Dashboard

- **Local:** `http://localhost:5000`
- **Network:** `http://<beagle-ip>:5000` (replace with your BeagleY-AI IP)

Find your IP:
```bash
hostname -I
# or
ip addr show | grep "inet "
```

### Stop Dashboard

**If running in foreground:**
- Press **Ctrl+C**

**If running in background:**
```bash
# Find the process
ps aux | grep web_app.py

# Kill it
kill <PID>

# Or kill all web_app processes
pkill -f web_app.py
```

---

## Run Both Together

### Terminal 1: Main Project

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main
```

### Terminal 2: Dashboard (Foreground)

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

### Terminal 2: Dashboard (Background)

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > dashboard.log 2>&1 &
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'therapy_robot'"

**Solution:** Run from parent directory (`/home/mike`) not from inside the project folder.

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python -m therapy_robot.main
```

### Error: "Permission denied" for SPI devices

**Solution:** Fix SPI permissions (see [Fix Permissions](#fix-permissions) section above).

### Error: "Permission denied" for GPIO

**Solution:** Add user to gpio group:
```bash
sudo usermod -a -G gpio $USER
newgrp gpio
```

### Error: "Python.h: No such file or directory"

**Solution:** Install Python development headers:
```bash
sudo apt install python3.13-dev
```

### Error: "externally-managed-environment"

**Solution:** Always use the virtual environment. Never use `--break-system-packages`.

### Dashboard shows no data

**Solution:** Run the main project first to generate log data:
```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main
```

Have a few conversations, then refresh the dashboard.

### Port 5000 already in use

**Solution:** Find and kill the process using port 5000:
```bash
sudo lsof -i :5000
kill <PID>
```

---

## Quick Reference

### One-Line Commands

**Setup:**
```bash
cd /home/mike/therapy_robot && ./setup.sh
```

**Fix SPI Permissions:**
```bash
sudo chmod 666 /dev/spidev0.0
```

**Run Main Project:**
```bash
cd /home/mike && source therapy_robot/venv/bin/activate && export GEMINI_API_KEY="YOUR_KEY" && python -m therapy_robot.main
```

**Run Dashboard:**
```bash
cd /home/mike/therapy_robot && source venv/bin/activate && python dashboard/web_app.py
```

**Check Status:**
```bash
ps aux | grep -E "(main.py|web_app.py)"
```

---

## Next Steps

- See `PROJECT_SUMMARY.md` for detailed project documentation
- See `DASHBOARD_GUIDE.md` for dashboard features
- See `WEB_DASHBOARD_GUIDE.md` for web dashboard details

