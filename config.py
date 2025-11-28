# config.py
"""
Central configuration module for therapy_robot project.
Single source of truth for pins, thresholds, paths, and settings.
"""
import os
from pathlib import Path

# ============================================================
# Simulation Mode
# ============================================================
USE_SIMULATION = bool(int(os.getenv("THERAPY_ROBOT_SIMULATION", "0")))

# ============================================================
# SPI / ADC Configuration
# ============================================================
SPI_DEVICE = "/dev/spidev0.0"
SPI_MODE = 0
SPI_MAX_SPEED_HZ = 1_000_000

# ADC Channel Assignments
ADC_CHANNEL_JOYSTICK_X = 0
ADC_CHANNEL_JOYSTICK_Y = 1
ADC_CHANNEL_ACCEL_X = 2
ADC_CHANNEL_ACCEL_Y = 3
ADC_CHANNEL_LDR = 4
ADC_CHANNEL_ACCEL_Z = 7

# ADC Constants
ADC_MAX_VALUE = 4095  # 12-bit ADC
ADC_CENTER = ADC_MAX_VALUE / 2.0

# ============================================================
# GPIO Configuration
# ============================================================
LED_PIN = 26  # PWM-capable GPIO pin

ROTARY_GPIOCHIP = "/dev/gpiochip2"
ROTARY_CLK_LINE = 15  # GPIO5 on pin 29
ROTARY_DT_LINE = 17   # GPIO6 on pin 31
ROTARY_BUTTON_LINE = 18  # GPIO13 on pin 33 (not currently used)

# ============================================================
# Thresholds and Timings
# ============================================================
# Fall Detection
FALL_IMPACT_THRESHOLD = 2000  # Threshold for detecting sudden acceleration change
FALL_DURATION_MS = 100        # Minimum duration of impact (ms)
FALL_NO_MOVEMENT_MS = 500     # Time after fall to confirm it's not just a shake
FALL_SAMPLING_INTERVAL_MS = 10  # Sampling interval

# Ambient Light
AMBIENT_DARK_THRESHOLD = 0.3  # Below this is considered dark (0.0-1.0)
AMBIENT_LIGHT_CHECK_INTERVAL = 5.0  # Check every 5 seconds

# LED Breathing Animation
LED_BREATH_MIN_BRIGHTNESS = 0.1
LED_BREATH_MAX_BRIGHTNESS = 0.8
LED_BREATH_PERIOD_SEC = 4.0  # Duration of one complete cycle (in/out)

# Joystick
JOY_DEADZONE = 900      # Deadzone to prevent jitter
JOY_COOLDOWN_MS = 120   # Minimum time between actions

# Rotary Encoder
ROTARY_VOLUME_STEP = 0.02  # Volume change per encoder step
JOYSTICK_VOLUME_STEP = 0.05  # Volume change per joystick movement

# Health Alert
HEALTH_CHECK_TIMEOUT_SECONDS = 30  # Time to wait for user response after fall

# ============================================================
# Paths
# ============================================================
# Base paths (relative to project root)
MUSIC_DIR = "assets/music"
LOG_DIR = "logs"
PROOFS_DIR = "proofs"

# CSV Log Files
EVENTS_CSV = os.path.join(LOG_DIR, "events.csv")
CHATS_CSV = os.path.join(LOG_DIR, "chats.csv")

# ============================================================
# AI / Web Configuration
# ============================================================
DASHBOARD_REFRESH_SECONDS = 30  # Dashboard auto-refresh interval
GEMINI_EMOTION_CACHE_SECONDS = 15  # Rate limiting for emotion analysis (15-60 seconds)

# ============================================================
# Environment Variables
# ============================================================
# Google Gemini API Key
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Discord Webhook URL for safety alerts
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# ============================================================
# Dashboard Configuration
# ============================================================
DASHBOARD_BASE = "http://127.0.0.1:5000"
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000

# ============================================================
# Mental Health Tracking
# ============================================================
# Trend analysis windows (days)
TREND_SHORT_WINDOW_DAYS = 7   # Recent period
TREND_COMPARISON_DAYS = 7     # Previous period for comparison
TREND_THRESHOLD = 0.5         # Minimum score difference to detect trend

# Daily summary aggregation
DAILY_SUMMARY_MIN_SESSIONS = 1  # Minimum sessions needed for summary

# ============================================================
# Utility Functions
# ============================================================
def get_project_root():
    """
    Get the project root directory.
    
    Returns:
        Path object pointing to therapy_robot directory
    """
    return Path(__file__).parent

def ensure_directories():
    """Ensure all required directories exist."""
    base = get_project_root()
    dirs = [MUSIC_DIR, LOG_DIR, PROOFS_DIR]
    for dir_path in dirs:
        full_path = base / dir_path
        full_path.mkdir(parents=True, exist_ok=True)

