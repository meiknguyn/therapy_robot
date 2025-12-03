# Goodnight Feature Guide

## Overview

The **Goodnight Feature** automatically plays ambient music when the photoresistor detects low light levels. This creates a calming bedtime atmosphere.

## How It Works

1. **Light Detection**: The photoresistor continuously monitors ambient light
2. **Dark Detection**: When light drops below the threshold (`AMBIENT_DARK_THRESHOLD`), it's considered "dark"
3. **Music Starts**: Ambient music automatically starts playing from `assets/music/`
4. **Light Returns**: When light increases above the threshold, music stops

## Features

✅ **Automatic**: No manual intervention needed  
✅ **State Management**: Only starts/stops music when state changes (not repeatedly)  
✅ **Multiple Formats**: Supports `.wav`, `.mp3`, `.ogg`, `.flac` files  
✅ **Configurable**: Volume and check interval can be adjusted  
✅ **Logging**: All goodnight events are logged to `logs/events.csv`  

## Music Files

Place your ambient music files in:
```
/home/mike/therapy_robot/assets/music/
```

**Supported formats:**
- `.wav` (recommended for best compatibility)
- `.mp3`
- `.ogg`
- `.flac`

**Example files:**
- `calm.wav`
- `ambient.mp3`
- `sleep.ogg`

The feature will automatically find and play the first available music file.

## Configuration

Edit `config.py` to adjust settings:

```python
# Goodnight feature configuration
GOODNIGHT_MUSIC_VOLUME = 0.4  # Volume (0.0 to 1.0)
GOODNIGHT_CHECK_INTERVAL = 2.0  # Check interval (seconds)
AMBIENT_DARK_THRESHOLD = 0.58  # Light threshold for "dark"
```

### Volume

- `0.0` = Silent
- `0.4` = Quiet/background (default)
- `0.6` = Moderate
- `1.0` = Full volume

### Check Interval

- `1.0` = Check every second (more responsive)
- `2.0` = Check every 2 seconds (default, balanced)
- `5.0` = Check every 5 seconds (less CPU usage)

### Threshold

- Lower = More sensitive (triggers in dimmer light)
- Higher = Less sensitive (needs darker to trigger)
- Default: `0.58` (calibrated for your photoresistor)

## Testing

### Quick Test

Test the goodnight feature:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_goodnight.py
```

**What to do:**
1. Cover the photoresistor (make it dark)
2. Music should start playing
3. Uncover the photoresistor (make it bright)
4. Music should stop

### Test with Main Program

Run the main program and watch for goodnight messages:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python -m therapy_robot.main
```

When it gets dark, you'll see:
```
🌙 Goodnight mode: Playing calm.wav (volume: 0.4)
```

When light returns:
```
☀️ Goodnight mode: Music stopped (light detected)
```

## Usage in Main Program

The goodnight feature is **automatically enabled** when you run `main.py` if:
- Photoresistor is available
- Music files exist in `assets/music/`

It runs in the background and doesn't interfere with chat interactions.

## Troubleshooting

### Music doesn't play

1. **Check music files exist:**
   ```bash
   ls -la /home/mike/therapy_robot/assets/music/
   ```

2. **Check file format:**
   - Must be `.wav`, `.mp3`, `.ogg`, or `.flac`
   - Try `.wav` format first (best compatibility)

3. **Check photoresistor:**
   ```bash
   python therapy_robot/calibrate_photoresistor.py
   ```

4. **Check threshold:**
   - If threshold is too high, music won't start
   - If threshold is too low, music won't stop
   - Adjust `AMBIENT_DARK_THRESHOLD` in `config.py`

### Music plays but doesn't stop

- Threshold might be too low
- Increase `AMBIENT_DARK_THRESHOLD` in `config.py`
- Or check if photoresistor is working: `python therapy_robot/calibrate_photoresistor.py`

### Music starts/stops repeatedly

- This is normal if light is right at the threshold
- Increase `GOODNIGHT_CHECK_INTERVAL` to reduce sensitivity
- Or adjust `AMBIENT_DARK_THRESHOLD` to be more stable

### No music files found

```
⚠ Goodnight: No music files found in assets/music/
```

**Solution:**
1. Create the directory (if needed):
   ```bash
   mkdir -p /home/mike/therapy_robot/assets/music
   ```

2. Add music files:
   ```bash
   # Copy your music file
   cp your_music.wav /home/mike/therapy_robot/assets/music/calm.wav
   ```

## Logging

Goodnight events are logged to `logs/events.csv`:

- `goodnight_started`: When music starts
  - Fields: `music_file`, `volume`, `threshold`
- `goodnight_stopped`: When music stops
  - Fields: `reason` (usually "light_detected")

View logs:
```bash
cat /home/mike/therapy_robot/logs/events.csv | grep goodnight
```

## Advanced Usage

### Programmatic Control

```python
from therapy_robot.features.goodnight import GoodnightFeature
from therapy_robot.hardware.photoresistor import Photoresistor

# Initialize
ldr = Photoresistor()
goodnight = GoodnightFeature(music_volume=0.5)

# Update based on light
light = ldr.read_normalized()
goodnight.update(light)

# Get status
status = goodnight.get_status()
print(f"Music playing: {status['is_active']}")
print(f"Current file: {status['current_music']}")

# Stop manually
goodnight.stop()
```

### Custom Configuration

```python
goodnight = GoodnightFeature(
    music_volume=0.6,        # Louder music
    check_interval=1.0,      # Check every second
    dark_threshold=0.55      # Custom threshold
)
```

## Summary

✅ **Automatic**: Plays music when dark, stops when light  
✅ **Smart**: Only changes state when needed  
✅ **Configurable**: Adjust volume, interval, threshold  
✅ **Logged**: All events saved to CSV  
✅ **Multiple Formats**: Supports common audio formats  

The goodnight feature is now ready to create a calming bedtime atmosphere! 🌙

