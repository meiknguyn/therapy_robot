# Therapy Robot Project

## Purpose

An AI-powered therapy robot designed for students, running on a BeagleY-AI board with real hardware. The robot provides emotional support through a Gemini-powered chatbot, ambient music, and visual feedback via LED.

## Hardware

- **BeagleY-AI Board**: Main computing platform
- **LED (GPIO12, Pin 32)**: PWM-controlled LED for mood visualization
- **MCP3208 ADC (SPI)**: 12-bit ADC on `/dev/spidev0.0` for sensor readings
  - Channel 5: Photoresistor (LDR) for ambient light detection
  - Channels 0-1, 2-3, 7: Reserved for joystick and accelerometer (future use)
- **USB Audio**: Audio output via Pygame for music playback

## Software Components

### AI Module (`ai/`)
- **Gemini Client**: Emotion analysis with caching and supportive reply generation
- Uses Google Gemini API for natural language understanding and response

### Hardware Module (`hardware/`)
- **LED Controller**: PWM brightness control with breathing effects
- **Photoresistor**: Ambient light reading via MCP3208 ADC
- **Joystick & Rotary Encoder**: Stubs for future implementation

### Audio Module (`audio/`)
- **Speaker**: Music playback using Pygame mixer
- Auto-plays calming music when ambient light is below threshold

### Dashboard Module (`dashboard/`)
- **CSV Logger**: Thread-safe logging of events and chat interactions
- **Mental Health Analyzer**: Stub for future analytics

## Features

1. **Terminal-based Therapy Chatbot**: Interactive conversation with Gemini-powered responses
2. **Emotion Analysis**: Keyword-based emotion scoring (1-10 scale) with caching
3. **Ambient Music**: Auto-plays music when room is dark
4. **LED Mood Feedback**: LED brightness reflects user's emotional state
5. **CSV Logging**: All events and conversations logged for analysis
6. **Safety Features**: Detects self-harm keywords and provides crisis resources

## How to Run

### Initial Setup

1. **Install system dependencies** (if needed for spidev compilation):
   ```bash
   sudo apt install python3-dev python3.13-dev
   ```
   Note: The exact package name may vary based on your Python version.

2. **Create and activate virtual environment** (required for Debian/Ubuntu systems):
   ```bash
   cd therapy_robot
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   Or use the setup script:
   ```bash
   cd therapy_robot
   ./setup.sh
   ```

3. **Install dependencies** (if not using setup script):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Gemini API key**:
   ```bash
   export GEMINI_API_KEY="YOUR_KEY_HERE"
   ```

4. **Add music file** (optional):
   - Place `calm.wav` in `assets/music/` directory

### Running the Robot

1. **Activate virtual environment** (if not already activated):
   ```bash
   cd therapy_robot
   source venv/bin/activate
   ```

2. **Set Gemini API key** (if not already set):
   ```bash
   export GEMINI_API_KEY="YOUR_KEY_HERE"
   ```

3. **Run the robot**:
   ```bash
   python -m therapy_robot.main
   ```
   
   Or from the project root:
   ```bash
   python -m therapy_robot.main
   ```

4. **Interact with the chatbot**:
   - Type your message and press Enter
   - Type "quit", "exit", or "bye" to end the session
   - Press Ctrl+C to interrupt

### Deactivating Virtual Environment

When done, deactivate the virtual environment:
```bash
deactivate
```

## Project Structure

```
therapy_robot/
├── ai/                    # Gemini API integration
├── hardware/              # LED, ADC, sensors
├── audio/                 # Music playback
├── dashboard/             # Logging and analytics
├── logs/                  # CSV log files
├── assets/music/          # Audio files
├── config.py              # Configuration constants
├── main.py                # Main entry point
└── requirements.txt       # Python dependencies
```

## Future Extensions

- Joystick control for navigation
- Rotary encoder for settings adjustment
- Accelerometer-based fall detection
- Advanced mental health analytics
- Web dashboard for data visualization

