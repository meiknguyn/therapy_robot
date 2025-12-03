# Joystick Y-Axis Volume Control

## Overview

The Therapy Robot uses the joystick Y-axis to control music volume in real-time. Move the joystick up to increase volume, down to decrease it.

## How It Works

The volume control uses a **step-based system** with hold-time requirements:

- **Push joystick UP (Y < 0.3)** and **hold for 0.5 seconds** → Volume increases by 5%
- **Push joystick DOWN (Y > 0.7)** and **hold for 0.5 seconds** → Volume decreases by 5%
- **Release joystick** → Volume stays at current level (doesn't revert)

**Key Features:**
- Volume changes in **5% steps** (gradual adjustment)
- Must **hold joystick** for 0.5 seconds to trigger change
- **0.3 second cooldown** after each change prevents rapid adjustments
- Volume **persists** when joystick returns to center
- You must push **repeatedly** to make larger volume changes

The volume control runs continuously in the background, so you can adjust volume at any time, even while chatting or while music is playing.

## Features

✅ **Step-based Control**: Volume changes in 5% increments (gradual adjustment)  
✅ **Hold-time Required**: Must hold joystick for 0.5s to trigger change (prevents accidental changes)  
✅ **Persistent Volume**: Volume stays at new level when joystick is released  
✅ **Cooldown Protection**: 0.3s cooldown prevents rapid volume changes  
✅ **Background Operation**: Works continuously without interrupting chat  
✅ **Visual Feedback**: Shows volume percentage when changed  
✅ **Event Logging**: Volume changes are logged to `logs/events.csv`  

## Usage

### During Normal Operation

When you run the main program, volume control is automatically active:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python -m therapy_robot.main
```

You'll see:
```
✓ Joystick initialized
✓ Volume control (joystick Y-axis) active
```

### Adjusting Volume

1. **Push joystick UP** (Y < 0.3) and **hold for 0.5 seconds** → Volume increases by 5%
2. **Push joystick DOWN** (Y > 0.7) and **hold for 0.5 seconds** → Volume decreases by 5%
3. **Release joystick** → Volume stays at current level
4. **Repeat** to make larger volume changes
5. **Volume display**: You'll see `🔊 Volume: XX%` when volume changes

### Example

```
You: Let's play my favorite song

🎵 Playing your favorite song: myfavsong.wav
   (You can continue chatting while it plays)

🔊 Volume: 75%    ← Joystick moved up

Robot (mood=7/10):
That's a great idea! Music can be so uplifting...

🔊 Volume: 50%    ← Joystick moved to center
🔊 Volume: 25%    ← Joystick moved down
```

## Testing

### Test Joystick Volume Control

Run the test script to see volume mapping:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_joystick_volume.py
```

**What you'll see:**
- Real-time Y-axis position
- Mapped volume percentage
- Visual volume bar
- Volume actually changes (if music is playing)

### Test with Music

1. Start the main program
2. Play music (goodnight feature or favorite song)
3. Move joystick up/down
4. Listen to volume change in real-time

## Technical Details

### Step-Based Control Logic

```python
# Joystick zones
if y_position < 0.3:  # Up zone
    # Must hold for 0.5 seconds
    # Then increase volume by 5%
elif y_position > 0.7:  # Down zone
    # Must hold for 0.5 seconds
    # Then decrease volume by 5%
else:
    # Center zone - volume stays the same
```

### Configuration

- **Step Size**: 5% per change
- **Hold Time**: 0.5 seconds required to trigger change
- **Cooldown**: 0.3 seconds between changes
- **Up Threshold**: Y < 0.3
- **Down Threshold**: Y > 0.7

### Update Frequency

Joystick is read every **0.05 seconds** (20 times per second) for responsive control.

## Logging

Volume adjustments are logged to `logs/events.csv`:

```csv
timestamp,event_type,data
2024-12-02 10:30:15,volume_adjusted,"{""volume"": 0.75, ""joystick_y"": 0.25}"
2024-12-02 10:30:20,volume_adjusted,"{""volume"": 0.50, ""joystick_y"": 0.50}"
```

View recent volume changes:
```bash
grep volume_adjusted /home/mike/therapy_robot/logs/events.csv
```

## Troubleshooting

### Volume doesn't change

1. **Check joystick initialization:**
   - Look for `✓ Joystick initialized` at startup
   - If you see `⚠ Joystick unavailable`, check SPI permissions

2. **Check joystick reading:**
   ```bash
   python therapy_robot/test_joystick_volume.py
   ```
   - If this fails, check ADC channel 1 connection

3. **Check music is playing:**
   - Volume control works even without music, but you won't hear changes
   - Start music first (goodnight feature or favorite song)

### Volume changes too quickly/slowly

**Too quickly:**
- The update threshold is 2% - this is intentional to reduce noise
- Volume updates every 0.1 seconds

**Too slowly:**
- Check if joystick is reading correctly
- Verify ADC channel 1 is connected properly

### Joystick not detected

1. **Check SPI permissions:**
   ```bash
   ls -la /dev/spidev0.0
   ```
   - Should be readable by your user

2. **Check ADC channel:**
   - Joystick Y is on ADC channel 1
   - Verify hardware connection

3. **Check initialization:**
   - Look for error messages at startup
   - Program continues without joystick if unavailable

## Configuration

### Adjust Update Frequency

Edit `main.py` and change:
```python
time.sleep(0.1)  # Check every 0.1 seconds
```

To:
```python
time.sleep(0.05)  # Check every 0.05 seconds (faster)
# or
time.sleep(0.2)  # Check every 0.2 seconds (slower)
```

### Adjust Update Threshold

Edit `main.py` and change:
```python
if abs(new_volume - current_volume) > 0.02:  # 2% threshold
```

To:
```python
if abs(new_volume - current_volume) > 0.05:  # 5% threshold (less sensitive)
# or
if abs(new_volume - current_volume) > 0.01:  # 1% threshold (more sensitive)
```

### Invert Volume Mapping

If you want down = louder, up = quieter, edit `main.py`:
```python
# Change from:
new_volume = 1.0 - y_position

# To:
new_volume = y_position  # Direct mapping (down = louder)
```

## Hardware

- **ADC Channel**: Channel 1 (Y-axis)
- **SPI Device**: `/dev/spidev0.0`
- **Range**: 0-4095 (12-bit ADC)
- **Normalized**: 0.0 to 1.0

## Summary

✅ **Easy to use**: Just move joystick up/down  
✅ **Real-time**: Instant volume adjustment  
✅ **Background**: Works while chatting  
✅ **Logged**: All changes recorded  
✅ **Responsive**: Updates 10 times per second  

Enjoy controlling your music volume with the joystick! 🎮🔊

