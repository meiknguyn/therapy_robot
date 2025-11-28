# Therapy Robot – Milestone 2

An AI-powered student wellness assistant running on the BeagleY-AI board. The system provides emotional support, focus tools (Pomodoro), meditation assistance through LED breathing animation, and a web dashboard that logs all user interactions.

## Features Implemented (Milestone 2)

### 1. AI Text Chat Interaction
- User types messages into the terminal.
- AI detects emotional tone (stressed, sad, happy, neutral).
- AI generates supportive, context-aware replies.
- Emotion + response are logged to a dashboard.

### 2. Web Dashboard (Flask)
- Runs on `http://<beagle-ip>:5000`
- Displays chat messages, detected emotions, Pomodoro events, and meditation events.
- Uses Flask backend + HTML/CSS frontend.

### 3. Meditation LED Breathing Routine
- Triggered by user command: `start meditation`
- LED fades in/out smoothly using PWM.

### 4. Pomodoro Focus Mode
- `start focus` triggers a focus session.
- Logged to dashboard for study session tracking.

## Project Structure
```
therapy_robot/
├── ai/
│   ├── gemini_client.py
│   └── prompts.py
├── dashboard/
│   └── dashboard_app.py
├── io/
│   ├── led_driver.py
│   └── audio_io.py
├── modules/
│   ├── chat_session.py
│   ├── meditation.py
│   └── pomodoro.py
├── safety/
│   └── fall_detector.py
├── config/
│   └── secrets.env
├── main.py
├── list_models.py
└── requirements.txt
```

## How to Run

### 1. Activate Environment
```bash
cd ~/therapy_robot
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Gemini API Key
Create `config/secrets.env`:
```
GEMINI_API_KEY=YOUR_KEY_HERE
```

## Run Dashboard
In Terminal #1:
```bash
python -m dashboard.dashboard_app
```
Visit: `http://<beagle-ip>:5000`

## Run AI Assistant
In Terminal #2:
```bash
python main.py
```
Try:
```
I'm stressed about my exam
start focus
start meditation
```

## Milestone 2 Proofs
- AI chat + emotion detection output.
- Dashboard logs of events.
- LED meditation breathing animation.

## Future Work
- Fall detector using accelerometer.
- More hardware outputs (sound/vibration).
- Advanced dialogue and emotion personalization.

## Author
**Tan Minh Nguyen (meiknguyn)**

