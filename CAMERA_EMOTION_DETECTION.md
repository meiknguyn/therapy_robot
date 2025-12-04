# Camera-Based Emotion Detection

## Overview

The therapy robot now supports **camera-based emotion detection** using Google Gemini's vision capabilities. This allows the robot to analyze facial expressions and detect emotions from camera images.

## How It Works

1. **Camera Capture**: Opens the camera and captures a single frame
2. **Image Processing**: Converts the frame to a PIL Image format
3. **AI Analysis**: Sends the image to Gemini API with emotion detection prompt
4. **Emotion Classification**: Returns one of the allowed emotions:
   - calm
   - happy
   - neutral
   - sad
   - stressed
   - anxious
   - angry

## Usage

### Voice Commands

Say any of these phrases to trigger camera emotion detection:
- **"detect emotion"**
- **"emotion from camera"**
- **"check my emotion"**
- **"analyze my face"**

### Example Flow

```
User: "detect emotion"
Robot: "Looking at you now to detect your emotion. Please look at the camera."
[Camera captures image]
Robot: "You look happy today. Would you like to talk about it?"
```

## Implementation Details

### Files Modified

1. **`ai/gemini_client.py`**
   - Added `analyze_emotion_from_image()` function
   - Uses Gemini vision API to analyze facial expressions
   - Returns emotion matching the system's allowed emotions

2. **`modules/camera_capture.py`**
   - Added `capture_frame_for_analysis()` - captures frame as PIL Image
   - Added `capture_and_analyze_emotion()` - convenience method combining capture + analysis
   - Saves emotion detection images to `proofs/` directory

3. **`main.py`**
   - Added voice command handling for emotion detection
   - Integrates camera emotion detection into chat flow
   - Logs emotion detection events

### Technical Details

- **Camera Index**: Defaults to camera device 0, configurable
- **Image Format**: Captured as BGR (OpenCV), converted to RGB for PIL, then sent to Gemini
- **Error Handling**: Graceful fallback to text-based emotion detection if camera fails
- **Logging**: All emotion detections are logged to CSV and dashboard
- **Image Storage**: Emotion detection images saved with format: `emotion_{emotion}_{timestamp}.jpg`

## Integration with Existing System

- Camera emotion detection **complements** text-based emotion detection
- Both methods use the same emotion classification system
- Camera emotion can trigger a chat session naturally
- All detected emotions are logged and tracked in mental health analytics

## Requirements

- **OpenCV**: Already in requirements.txt
- **Pillow**: Added to requirements.txt for PIL Image support
- **Google Gemini API**: Already configured for text-based emotion detection
- **Camera**: USB webcam or built-in camera

## Example Use Cases

1. **Initial Session Start**: Robot can detect emotion at start of session
2. **Periodic Check-ins**: Check emotional state throughout the day
3. **Visual Confirmation**: Verify text-based emotion detection with visual analysis
4. **Non-verbal Communication**: Detect emotions when user is quiet

## Privacy & Security

- Images are saved locally in `proofs/` directory
- Images are not sent to any external service except Gemini API (for analysis)
- Emotion detection images are timestamped for privacy tracking
- Users can delete saved images at any time

---

**Note**: This feature requires a camera and Gemini API key with vision capabilities enabled.

