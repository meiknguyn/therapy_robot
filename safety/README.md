# Safety Features Documentation

## Overview

The therapy robot includes safety features to detect falls and alert trusted contacts via Discord when assistance may be needed.

## Components

### 1. Fall Detector (`fall_detector.py`)

Monitors the accelerometer (ADC channels 2, 3, 7) to detect when the robot falls or experiences sudden impacts.

**Features:**
- Continuous monitoring of acceleration magnitude
- Detects sudden changes in acceleration (impact detection)
- Confirms sustained impact to reduce false positives
- Runs in background thread with minimal overhead

**Hardware:**
- Uses accelerometer via MCP3208 ADC
- ADC Channel 2: X-axis
- ADC Channel 3: Y-axis  
- ADC Channel 7: Z-axis

### 2. Health Alert System (`health_alert.py`)

Handles user check-in after fall detection and sends Discord alerts.

**Features:**
- Asks user if they're okay after fall detection
- Waits 30 seconds for user response
- Sends Discord alert if:
  - No response received
  - User indicates they need help
- Sends detailed alert with timestamp and user response

## Discord Webhook Setup

### Step 1: Create a Discord Webhook

1. Open your Discord server
2. Go to **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Configure the webhook:
   - Name: "Therapy Robot Alert" (or your preference)
   - Channel: Select a channel for alerts
5. Click **Copy Webhook URL**

### Step 2: Configure the Webhook URL

**Option A: Environment Variable**

Add to your shell environment or `config/secrets.env`:

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

**Option B: System Environment**

On Linux/Mac:
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

On Windows (PowerShell):
```powershell
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

### Step 3: Test the Webhook

Run the therapy robot and say:
- **"test alert"** or **"test discord"**

You should receive a test message in your Discord channel.

## How It Works

1. **Fall Detection**
   - Fall detector continuously monitors accelerometer
   - When a sudden impact is detected, it triggers fall callback

2. **Health Check**
   - Robot asks: *"I detected a fall. Are you okay? Please respond with 'yes' or 'I'm okay' if you're fine."*
   - Waits up to 30 seconds for response

3. **Alert Scenarios**

   **No Response:**
   - Robot sends Discord alert: *"FALL DETECTED - NO RESPONSE"*
   - Includes timestamp and note that user didn't respond

   **User Needs Help:**
   - Robot sends Discord alert: *"FALL DETECTED - ASSISTANCE NEEDED"*
   - Includes timestamp and user's response

   **User is Okay:**
   - Robot acknowledges: *"I'm glad you're okay. Take care!"*
   - No alert sent

## Alert Message Format

Discord alerts include:
- 🚨 Alert title and color (red)
- Timestamp of the fall
- User response (if provided)
- Request to check on the user

## Troubleshooting

### Discord alerts not working?

1. **Check webhook URL:**
   - Verify `DISCORD_WEBHOOK_URL` environment variable is set
   - Test with "test alert" command

2. **Verify webhook is active:**
   - Check Discord webhook settings
   - Ensure webhook hasn't been deleted

3. **Check network connectivity:**
   - Robot must have internet connection
   - Firewall must allow outbound HTTPS to discord.com

### False positives?

Adjust fall detection sensitivity in `fall_detector.py`:
- `FALL_THRESHOLD`: Increase to reduce sensitivity
- `FALL_DURATION_MS`: Increase to require longer impact
- `STABLE_DURATION_MS`: Increase to wait longer before confirming fall

### No response from user?

- Check that `listen_callback` is working correctly
- Verify microphone/audio input is configured
- Increase `CHECK_IN_TIMEOUT_SECONDS` if needed

## Privacy & Security

- Discord webhook URLs are sensitive - keep them private
- Store webhook URL in `config/secrets.env` (not in git)
- Webhooks can be disabled/deleted from Discord if compromised

## Requirements

- `requests` library (already in requirements.txt)
- Internet connection for Discord webhook
- Discord webhook URL configured

