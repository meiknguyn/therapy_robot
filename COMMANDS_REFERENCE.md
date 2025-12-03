# Therapy Robot - Commands Reference

Quick reference for all commands needed to run the project.

## Setup Commands

### Initial Setup

```bash
# Install Python dev headers
sudo apt install python3.13-dev

# Navigate to project
cd /home/mike/therapy_robot

# Run setup script
./setup.sh
```

### Manual Setup

```bash
cd /home/mike/therapy_robot
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Permission Fixes

### Quick Fix (Temporary)

```bash
sudo chmod 666 /dev/spidev0.0
```

### Complete Fix (Persistent)

```bash
# Create groups
sudo groupadd spi
sudo groupadd gpio

# Add user to groups
sudo usermod -a -G spi $USER
sudo usermod -a -G gpio $USER

# Fix SPI permissions
sudo chgrp spi /dev/spidev0.0
sudo chmod 664 /dev/spidev0.0

# Create udev rule (persistent)
sudo bash -c 'echo "KERNEL==\"spidev0.0\", GROUP=\"spi\", MODE=\"0664\"" > /etc/udev/rules.d/99-spi-permissions.rules'
sudo udevadm control --reload-rules
sudo udevadm trigger

# Activate groups
newgrp spi
newgrp gpio
```

## Running Main Project

### Standard Run

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main
```

### With .env File

```bash
# Create .env file
cd /home/mike/therapy_robot
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env

# Run
cd /home/mike
source therapy_robot/venv/bin/activate
python -m therapy_robot.main
```

### Background Run

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
nohup python -m therapy_robot.main > therapy_robot.log 2>&1 &
```

## Running Dashboard

### Foreground

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

### Background

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > dashboard.log 2>&1 &
```

### Service Mode

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
nohup python dashboard/web_app.py > /tmp/dashboard.log 2>&1 &
```

## Running Both Together

### Terminal 1: Main Project

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main
```

### Terminal 2: Dashboard

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

## Verification Commands

### Check Groups

```bash
groups
```

### Check Device Permissions

```bash
ls -l /dev/spidev0.0
ls -l /dev/gpiochip2
```

### Test SPI Access

```bash
python3 -c "import spidev; spi = spidev.SpiDev(); spi.open(0, 0); print('✓ SPI OK'); spi.close()"
```

### Test GPIO Access

```bash
python3 -c "import gpiod; chip = gpiod.Chip('/dev/gpiochip2'); print('✓ GPIO OK'); chip.close()"
```

### Check Running Processes

```bash
ps aux | grep -E "(main.py|web_app.py)"
```

### Check Port Usage

```bash
sudo lsof -i :5000
```

## Stopping Services

### Stop Main Project

```bash
pkill -f "therapy_robot.main"
# or
pkill -f "main.py"
```

### Stop Dashboard

```bash
pkill -f web_app.py
```

### Stop Both

```bash
pkill -f "therapy_robot.main"
pkill -f web_app.py
```

## Log Viewing

### View Main Project Logs

```bash
tail -f therapy_robot.log
```

### View Dashboard Logs

```bash
tail -f dashboard.log
```

### View Chat Logs

```bash
tail -20 /home/mike/therapy_robot/logs/chats.csv
```

### View Event Logs

```bash
tail -20 /home/mike/therapy_robot/logs/events.csv
```

## Testing Commands

### Run Full Test Suite

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_project.py
```

### Test Dashboard

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_dashboard.py
```

### Test Hardware

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_accelerometer.py
python therapy_robot/test_photoresistor.py
python therapy_robot/test_led_diagnostic.py
```

## API Testing

### Get Dashboard Stats

```bash
curl http://localhost:5000/api/stats
```

### Get Recent Chats

```bash
curl http://localhost:5000/api/chats
```

### Get Recent Events

```bash
curl http://localhost:5000/api/events
```

### Get Volume

```bash
curl http://localhost:5000/api/volume
```

### Set Volume

```bash
curl -X POST http://localhost:5000/api/volume \
  -H "Content-Type: application/json" \
  -d '{"volume": 0.8}'
```

### Send Chat Message

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Network Commands

### Find IP Address

```bash
hostname -I
# or
ip addr show | grep "inet "
```

### Check Firewall

```bash
sudo ufw status
sudo ufw allow 5000
```

## One-Line Quick Commands

### Complete Setup

```bash
cd /home/mike/therapy_robot && ./setup.sh && sudo chmod 666 /dev/spidev0.0
```

### Run Main Project

```bash
cd /home/mike && source therapy_robot/venv/bin/activate && export GEMINI_API_KEY="YOUR_KEY" && python -m therapy_robot.main
```

### Run Dashboard

```bash
cd /home/mike/therapy_robot && source venv/bin/activate && python dashboard/web_app.py
```

### Fix Permissions and Run

```bash
sudo chmod 666 /dev/spidev0.0 && cd /home/mike && source therapy_robot/venv/bin/activate && export GEMINI_API_KEY="YOUR_KEY" && python -m therapy_robot.main
```

## Environment Variables

### Set API Key (Temporary)

```bash
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

### Set API Key (Persistent)

```bash
echo 'export GEMINI_API_KEY="YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### Check API Key

```bash
echo $GEMINI_API_KEY
```

## File Locations

### Project Root
```
/home/mike/therapy_robot/
```

### Log Files
```
/home/mike/therapy_robot/logs/chats.csv
/home/mike/therapy_robot/logs/events.csv
/home/mike/therapy_robot/logs/volume.txt
```

### Configuration
```
/home/mike/therapy_robot/config.py
/home/mike/therapy_robot/.env (if using)
```

### Hardware Devices
```
/dev/spidev0.0 (SPI)
/dev/gpiochip2 (GPIO)
```

## Common Issues & Fixes

### Module Not Found

```bash
cd /home/mike
python -m therapy_robot.main
```

### Permission Denied

```bash
sudo chmod 666 /dev/spidev0.0
```

### Port Already in Use

```bash
sudo lsof -i :5000
kill <PID>
```

### Groups Not Active

```bash
newgrp spi
newgrp gpio
```

## Next Steps

- See `QUICK_START.md` for detailed setup guide
- See `RUN_MAIN_PROJECT.md` for main project details
- See `RUN_DASHBOARD.md` for dashboard details
- See `FIX_PERMISSIONS.md` for permission troubleshooting

