"""Configuration constants for the Therapy Robot project."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Load environment variables from .env file
# Load from the project directory, not current working directory
# override=True ensures .env file values take precedence over existing env vars
# This will automatically load GEMINI_API_KEY from .env
load_dotenv(BASE_DIR / ".env", override=True)

# Directory paths (auto-created if missing)
LOG_DIR = BASE_DIR / "logs"
MUSIC_DIR = BASE_DIR / "assets" / "music"
PROOFS_DIR = BASE_DIR / "proofs"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
PROOFS_DIR.mkdir(parents=True, exist_ok=True)

# File paths
EVENT_LOG_PATH = LOG_DIR / "events.csv"
CHAT_LOG_PATH = LOG_DIR / "chats.csv"

# Hardware constants
LED_PIN = 16  # GPIO16 (named GPIO12 on BeagleY-AI), Pin 32 (PWM LED)

# SPI / MCP3208 ADC configuration
SPI_DEVICE = "/dev/spidev0.0"
SPI_MODE = 0
SPI_MAX_SPEED = 1_000_000  # 1 MHz

# ADC Channel assignments
ADC_CHANNEL_JOYSTICK_X = 0
ADC_CHANNEL_JOYSTICK_Y = 1
ADC_CHANNEL_ACCEL_X = 2
ADC_CHANNEL_ACCEL_Y = 3
ADC_CHANNEL_LDR = 5  # IMPORTANT: LDR on channel 5
ADC_CHANNEL_ACCEL_Z = 7

# GPIO chip for rotary encoder (future use)
GPIO_CHIP = "/dev/gpiochip2"
GPIO_ROTARY_CLK = 15  # GPIO5, Pin 29
GPIO_ROTARY_DT = 17   # GPIO6, Pin 31
GPIO_ROTARY_BTN = 18  # GPIO13, Pin 33

# AI / Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMOTION_CACHE_SECONDS = 15

# Other configuration
# Ambient light threshold for auto-playing music when dark
# Calibrated for your photoresistor range:
# - Darkest reading (lights off): ~0.545
# - Brightest reading (lights on): ~0.714
# Threshold set to 0.58 (between dark and bright, triggers reliably in dark)
# Run calibrate_photoresistor.py to fine-tune for your specific setup
AMBIENT_DARK_THRESHOLD = 0.58  # used to auto-start music when dark

# Goodnight feature configuration
GOODNIGHT_MUSIC_VOLUME = 0.4  # Volume for ambient music (0.0 to 1.0)
GOODNIGHT_CHECK_INTERVAL = 2.0  # How often to check light level (seconds)

# Volume control configuration (joystick Y-axis)
VOLUME_STEP_SIZE = 0.05  # Volume change per step (5%)
VOLUME_HOLD_TIME = 0.5  # Time (seconds) joystick must be held to trigger volume change
VOLUME_COOLDOWN = 0.3  # Cooldown (seconds) after volume change before next change allowed
VOLUME_UP_THRESHOLD = 0.59  # Joystick Y < this value triggers volume up (calibrated: center ~0.622, UP zone 0.500-0.593, center min 0.605)
VOLUME_DOWN_THRESHOLD = 0.65  # Joystick Y > this value triggers volume down (calibrated: center ~0.622, DOWN zone 0.674-1.000)

