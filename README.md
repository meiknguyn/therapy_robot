# Therapy Robot - Quick Start Guide

## Prerequisites

1. **Install Python development headers** (required for `spidev` package):
   ```bash
   sudo apt install python3.13-dev
   ```
   Note: Adjust the version number (3.13) to match your Python version.

2. **Ensure you have a Gemini API key** from Google AI Studio.

## Setup

### Option 1: Using the setup script (Recommended)

```bash
cd therapy_robot
./setup.sh
```

### Option 2: Manual setup

```bash
cd therapy_robot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Robot

1. **Activate the virtual environment** (if not already activated):
   ```bash
   cd therapy_robot
   source venv/bin/activate
   ```

2. **Set your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="YOUR_KEY_HERE"
   ```

3. **Run the robot**:
   ```bash
   python -m therapy_robot.main
   ```

4. **Interact with the chatbot**:
   - Type your message and press Enter
   - Type "quit", "exit", or "bye" to end the session
   - Press Ctrl+C to interrupt

## Troubleshooting

### Error: "externally-managed-environment"
- Solution: Use the virtual environment as shown above. Never use `--break-system-packages`.

### Error: "Python.h: No such file or directory" when installing spidev
- Solution: Install Python development headers:
  ```bash
  sudo apt install python3.13-dev
  ```
  (Adjust version number to match your Python version)

### Error: "Permission denied" when accessing /dev/spidev0.0
- Solution: Add your user to the `spi` group:
  ```bash
  sudo usermod -a -G spi $USER
  ```
  Then log out and log back in, or run `newgrp spi`.

### Error: "Permission denied" when accessing GPIO
- Solution: Add your user to the `gpio` group:
  ```bash
  sudo usermod -a -G gpio $USER
  ```
  Then log out and log back in, or run `newgrp gpio`.

## Deactivating Virtual Environment

When done, deactivate the virtual environment:
```bash
deactivate
```

## For More Information

See `PROJECT_SUMMARY.md` for detailed project documentation.


