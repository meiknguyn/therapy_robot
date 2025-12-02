# Therapy Robot Project - Complete Summary

## 🎯 Project Overview

A comprehensive therapy robot system with hardware integration, safety features, logging, and mental health tracking dashboard.

---

## 📁 Project Structure

```
therapy_robot/
├── hardware/              # Hardware control modules
│   ├── led_ctrl.py       # LED brightness & breathing control
│   ├── photoresistor.py  # Ambient light sensor (LDR)
│   ├── joystick.py       # Joystick controls
│   └── rotary.py         # Rotary encoder control
│
├── audio/                # Audio system
│   └── speaker.py        # Ambient music playback
│
├── modules/              # Feature modules
│   ├── ambient_music.py  # Music management
│   ├── camera_capture.py # Photo capture
│   ├── meditation_led.py # Meditation breathing
│   └── pomodoro.py       # Focus timer
│
├── safety/               # Safety features
│   ├── fall_detector.py  # Accelerometer fall detection
│   ├── health_alert.py   # Health check & Discord alerts
│   └── README.md         # Safety documentation
│
├── dashboard/            # Web dashboard
│   ├── dashboard_app.py  # Main Flask app with charts & summaries
│   ├── csv_logger.py     # CSV logging system
│   ├── mental_health_analyzer.py  # Mental health analysis & trends
│   ├── LOGGING.md        # Logging documentation
│   └── MENTAL_HEALTH_TRACKING.md  # Tracking docs
│
├── logs/                 # Log files (CSV)
│   ├── events.csv        # All system events
│   └── chats.csv         # All chat interactions
│
├── assets/               # Media assets
│   └── music/            # Ambient music files
│
├── config.py             # Central configuration (NEW!)
├── simulation.py         # Hardware simulation mode (NEW!)
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
├── HARDWARE_PINS.md      # Pin assignment reference
├── REFACTORING_STATUS.md # Refactoring status documentation
└── PROJECT_SUMMARY.md    # This file
```

---

## 🆕 Latest Refactoring Features (2024)

### Central Configuration System (`config.py`)
- **Single source of truth** for all pins, thresholds, paths, and settings
- **Environment variable support** for API keys and Discord webhook
- **Hardware pin assignments** centralized from Assignment 3
- **Thresholds and timings** configurable in one place
- **Path configuration** for logs, music, proofs directories

### Hardware Simulation Mode (`simulation.py`)
- **Run without physical hardware** for development/testing
- **Simulated implementations** of all hardware components:
  - SimulatedLED - logs brightness changes
  - SimulatedPhotoresistor - returns varying light readings
  - SimulatedJoystick - no input (simulation only)
  - SimulatedRotaryEncoder - no input (simulation only)
  - SimulatedFallDetector - never detects falls (for safety)
- **Controlled by environment variable**: `THERAPY_ROBOT_SIMULATION=1`
- **Full feature compatibility** - all modules work in simulation mode

### AI Rate Limiting
- **Thread-safe caching** for emotion analysis
- **Configurable cache duration** (default: 15 seconds)
- **Prevents excessive API calls** to Gemini
- **Seamless integration** - no changes to calling code

### Enhanced Mental Health Tracking
- **Daily Summary Generation**: AI-powered end-of-day summaries
- **Trend Forecasting**: Classifies trends as improving/stable/declining
- **Enhanced Analytics**: More detailed statistics and insights
- **Dashboard Integration**: Daily summary card with AI-generated insights

---

## 🔧 Hardware Modules Implemented

### 1. LED Controller (`hardware/led_ctrl.py`)
- **GPIO Pin**: 26 (from `config.LED_PIN`, configurable, PWM-capable)
- **Features**:
  - Brightness control (0.0-1.0)
  - Smooth breathing animation (configurable via config)
  - Thread-safe operation
  - Used during meditation sessions
  - **Supports simulation mode** - can run without hardware

### 2. Photoresistor/LDR (`hardware/photoresistor.py`)
- **ADC Channel**: 4 (from `config.ADC_CHANNEL_LDR`, MCP3208 via SPI)
- **Features**:
  - Normalized readings (0.0-1.0)
  - Automatic logging of ambient light
  - Auto-start music in dark environments (threshold from config)
  - Uses Assignment 3 SPI configuration
  - **Supports simulation mode** - returns simulated light readings

### 3. Joystick (`hardware/joystick.py`)
- **ADC Channels**: 0 (X-axis), 1 (Y-axis)
- **Features**:
  - Up/Down: Volume control
  - Left/Right: Track switching
  - Press: Play/Pause toggle
  - Background polling thread

### 4. Rotary Encoder (`hardware/rotary.py`)
- **GPIO Chip**: `/dev/gpiochip2`
- **Lines**: 15 (CLK), 17 (DT)
- **Features**:
  - Volume control via rotation
  - Step counting and direction detection
  - Thread-safe operation

---

## 🎵 Audio & Music System

### Speaker Module (`audio/speaker.py`)
- **Technology**: Pygame mixer
- **Features**:
  - Non-blocking background playback
  - Volume control (0.0-1.0)
  - Music looping support
  - Multiple format support (.wav, .mp3, .ogg, .flac)

### Ambient Music Module (`modules/ambient_music.py`)
- **Features**:
  - Random track selection
  - Track switching (next/previous)
  - Play/pause control
  - Event logging
  - Music stored in `assets/music/`

### Voice Commands for Music:
- "play music", "calm me", "start ambient", "relax" → Start music
- "stop music" → Stop playback

---

## 📷 Camera Module

### Camera Capture (`modules/camera_capture.py`)
- **Technology**: OpenCV
- **Features**:
  - Photo capture with auto-timestamping
  - Saves to `proofs/` directory
  - Event logging
  - Automatic filename generation

### Voice Commands:
- "capture", "take picture", "camera" → Take photo

---

## 🛡️ Safety Features

### 1. Fall Detector (`safety/fall_detector.py`)
- **Hardware**: Accelerometer (ADC channels 2, 3, 7)
- **Features**:
  - Continuous monitoring of acceleration
  - Sudden impact detection
  - False positive prevention
  - Automatic health check trigger

### 2. Health Alert System (`safety/health_alert.py`)
- **Features**:
  - User check-in after fall detection
  - 30-second response timeout
  - Discord webhook notifications
  - Multiple alert scenarios:
    - No response → "NO RESPONSE" alert
    - User needs help → "ASSISTANCE NEEDED" alert
    - User is okay → No alert

### Discord Integration:
- Sends formatted alerts to Discord channel
- Requires `DISCORD_WEBHOOK_URL` environment variable
- Configurable via `config/secrets.env`

---

## 📊 Logging System

### CSV Logger (`dashboard/csv_logger.py`)
- **Features**:
  - Thread-safe logging
  - Separate files for events and chats
  - Automatic timestamp generation
  - UTF-8 encoding support

### Files Generated:
1. **`logs/events.csv`**: All system events
   - Columns: timestamp, event_type, details_json

2. **`logs/chats.csv`**: All chat interactions
   - Columns: timestamp, user_text, emotion, bot_reply

### Event Types Logged:
- Safety events (fall_detected, health_check, etc.)
- Hardware events (ambient_light, rotary_encoder, etc.)
- Module events (music, camera, etc.)
- Session events (pomodoro, meditation, etc.)

---

## 🆕 AI Rate Limiting

### Implementation (`ai/gemini_client.py`)
- **Thread-safe cache** prevents excessive API calls
- **Configurable duration**: `config.GEMINI_EMOTION_CACHE_SECONDS` (default: 15 seconds)
- **Automatic caching**: Returns cached emotion result if within time window
- **Transparent operation**: No changes needed to calling code

### Daily Summary Generation
- **AI-powered summaries** using Gemini API
- **Context-aware prompts** based on daily statistics
- **Friendly, caring tone** - not clinical or robotic
- **Fallback summaries** if AI unavailable
- **2-4 sentences** with gentle suggestions

---

## 📈 Mental Health Tracking Dashboard

### Web Dashboard (`dashboard/dashboard_app.py`)
- **Technology**: Flask + Chart.js
- **Access**: http://127.0.0.1:5000/
- **Features**:
  - Real-time event display
  - Auto-refresh every 30 seconds
  - CSV file downloads
  - Interactive charts

### Mental Health Analyzer (`dashboard/mental_health_analyzer.py`)
- **Emotion Scoring**: 1-10 scale
  - Positive emotions: 7-9 (joy, happy, calm, etc.)
  - Neutral: 5 (normal, okay, fine)
  - Negative emotions: 2-4 (sad, anxious, stressed, etc.)

### Visualizations:

#### 1. Overall Statistics Cards
- Overall Score (average mental health)
- Total Sessions
- Current Trend (improving/stable/declining)
- Recent Average (last 7 days)

#### 2. Interactive Charts
- **Daily View**: Line chart (last 30 days)
- **Weekly View**: Line chart (last 12 weeks)
- **Monthly View**: Bar chart (last 12 months)
- **Yearly View**: Bar chart (all years)

#### 3. Daily Therapy Summary Card (NEW!)
- **AI-generated daily summary** with caring, supportive tone
- **Today's statistics**: session count, average score
- **Trend indicator**: showing improving/stable/declining
- **Auto-refreshes** every 30 seconds
- **Context-aware insights** based on daily emotional patterns

#### 4. API Endpoints
- `/api/mental-health/stats` - Overall statistics
- `/api/mental-health/daily` - Daily trends
- `/api/mental-health/weekly` - Weekly trends
- `/api/mental-health/monthly` - Monthly trends
- `/api/mental-health/yearly` - Yearly trends
- `/api/mental-health/daily-summary` - **AI-generated daily summary (NEW!)**

---

## 🎮 Voice Commands Supported

### Core Commands:
- "play music", "calm me", "start ambient", "relax" → Start ambient music
- "stop music" → Stop music
- "capture", "take picture", "camera" → Take photo
- "check light" → Read ambient light level
- "test alert" → Test Discord alert

### Existing Commands:
- "pomodoro", "focus", "study" → Start focus session
- "meditation", "meditate", "breathe" → Start breathing exercise
- "quit", "exit", "bye" → End session

---

## 🔌 Hardware Pin Assignments

### ADC (MCP3208 via SPI)
- **Device**: `/dev/spidev0.0`
- **Mode**: SPI_MODE_0, 1 MHz
- **Channels**:
  - 0: Joystick X-axis
  - 1: Joystick Y-axis
  - 2: Accelerometer X
  - 3: Accelerometer Y
  - 4: Photoresistor (LDR)
  - 7: Accelerometer Z

### GPIO
- **Rotary Encoder**: `/dev/gpiochip2`
  - Line 15 (GPIO5): CLK
  - Line 17 (GPIO6): DT
  - Line 18 (GPIO13): Button (not used)

- **LED**: GPIO pin 26 (PWM)

---

## 📦 Dependencies

See `requirements.txt` for complete list:
- **Core**: requests, python-dotenv, google-generativeai
- **Hardware**: gpiozero, spidev
- **Audio**: pygame
- **Camera**: opencv-python
- **Web**: flask
- **Optional**: gpiod (for rotary encoder)

---

## 🚀 Key Features Summary

### ✅ Completed Features:

1. **Hardware Integration**
   - LED control with breathing animation
   - Photoresistor for ambient light
   - Joystick for music control
   - Rotary encoder for volume control
   - All using Assignment 3 pin assignments

2. **Audio System**
   - Ambient music playback
   - Volume control
   - Track switching
   - Background playback

3. **Camera System**
   - Photo capture
   - Auto-timestamping
   - Event logging

4. **Safety System**
   - Fall detection via accelerometer
   - Health check after falls
   - Discord alert notifications
   - Automatic monitoring

5. **Logging System**
   - CSV file logging
   - Thread-safe operation
   - Separate event and chat logs
   - Automatic timestamping

6. **Mental Health Tracking**
   - Emotion scoring system
   - Trend analysis (daily/weekly/monthly/yearly)
   - Interactive charts
   - Overall statistics dashboard
   - Real-time updates

7. **Web Dashboard**
   - Real-time event display
   - Chat log viewer
   - Mental health visualizations
   - CSV downloads
   - Auto-refresh

---

## 📝 Documentation Files

1. **`HARDWARE_PINS.md`**: Pin assignment reference
2. **`safety/README.md`**: Safety features documentation
3. **`dashboard/LOGGING.md`**: Logging system documentation
4. **`dashboard/MENTAL_HEALTH_TRACKING.md`**: Mental health tracking guide
5. **`PROJECT_SUMMARY.md`**: This comprehensive summary

---

## 🔄 Main Application Flow

1. **Initialization**:
   - Hardware modules initialized with pin assignments
   - Safety systems started (fall detector monitoring)
   - Dashboard server started
   - CSV logger ready

2. **Main Loop**:
   - Listens for voice commands
   - Processes commands and triggers appropriate modules
   - Logs all events and chats to CSV
   - Sends data to dashboard

3. **Background Tasks**:
   - Fall detection monitoring
   - Ambient light monitoring
   - Joystick polling
   - Rotary encoder polling

4. **Safety Monitoring**:
   - Continuous accelerometer monitoring
   - Fall detection triggers health check
   - Discord alerts sent if needed

---

## 📊 Data Flow

```
User Input → Main.py → Module/Feature → Event Log
                                    ↓
                            CSV Logger → logs/*.csv
                                    ↓
                            Dashboard → Web Display
                                    ↓
                            Mental Health Analyzer → Charts
```

---

## 🎯 Project Goals Achieved

✅ Hardware + software modules using Assignment 3 GPIO pins  
✅ LED control with breathing animation  
✅ Photoresistor for ambient light detection  
✅ Joystick for music control  
✅ Rotary encoder for volume control  
✅ Speaker for ambient music playback  
✅ Camera support for photo capture  
✅ Fall detection with accelerometer  
✅ Health alert system with Discord notifications  
✅ CSV logging for all events  
✅ Mental health tracking with visualizations  
✅ Web dashboard with interactive charts  
✅ Comprehensive documentation  

---

## 🔧 Configuration & Simulation

### Central Configuration (`config.py`)
All settings centralized in one file:
- **SPI/ADC**: Device paths, channels, speeds
- **GPIO**: Pin assignments, chip paths
- **Thresholds**: Fall detection, ambient light, timing parameters
- **Paths**: Music directory, log directory, proofs directory
- **Environment Variables**: API keys, Discord webhook URL

### Simulation Mode
Run without hardware using `THERAPY_ROBOT_SIMULATION=1`:
```bash
export THERAPY_ROBOT_SIMULATION=1
python therapy_robot/main.py
```

**Benefits**:
- Test on any computer (laptop, desktop)
- Develop without physical hardware
- Demo the system easily
- Debug features without GPIO access

**What Works in Simulation**:
- ✅ All software features (music, dashboard, logging, AI)
- ✅ Ambient music playback
- ✅ Camera capture (if camera available)
- ✅ Dashboard and charts
- ✅ CSV logging
- ✅ AI chat and daily summaries
- ⚠️ Hardware controls log actions but don't control real hardware

---

## 🔗 Repository

**GitHub**: https://github.com/meiknguyn/therapy_robot

All code is version controlled and documented.

---

## 📞 Next Steps / Future Enhancements

Potential improvements:
- Complete hardware module refactoring (joystick, rotary, fall_detector)
- Machine learning for emotion detection accuracy
- More sophisticated fall detection algorithms
- Additional safety sensors
- Mobile app companion
- Cloud sync for logs
- Advanced analytics and insights
- Goal setting and achievement tracking
- Integration with health tracking devices
- Voice recognition integration

---

## Individual Contributions (Summary)

This project was completed by a 4-person group.  

**Mike served as the primary developer**, implementing the majority of the system including hardware modules, safety features, AI integration, dashboard, simulation mode, and refactoring.  

Group members contributed feedback, minor documentation, and testing.

For detailed contribution information, please refer to:
- `INDIVIDUAL_CONTRIBUTION_MIKE.md` - Detailed contribution statement
- `CONTRIBUTION_BREAKDOWN.md` - Subsystem-by-subsystem breakdown
- `PROJECT_REFLECTION_MIKE.md` - Development process and reflections

---

**Project Status**: ✅ **FEATURE COMPLETE** - All core features + refactoring improvements implemented and documented!

