import os
import threading
import time
from typing import List, Optional

from dotenv import load_dotenv
import google.generativeai as genai

# Import config for rate limiting settings
try:
    from therapy_robot import config
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import config

# ---------------------------------------------------------------------
# Load API key from config/secrets.env
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
ENV_PATH = os.path.join(BASE_DIR, "config", "secrets.env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

API_KEY = config.GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. "
        "Set it in config/secrets.env or environment variables."
    )

# ---------------------------------------------------------------------
# Gemini setup
# ---------------------------------------------------------------------
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

# Emotions your system understands
ALLOWED_EMOTIONS: List[str] = [
    "calm",
    "happy",
    "neutral",
    "sad",
    "stressed",
    "anxious",
    "angry",
]

# ============================================================
# Rate Limiting Cache for Emotion Analysis
# ============================================================
_emotion_cache_lock = threading.Lock()
_last_emotion_request_time: Optional[float] = None
_last_emotion_result: Optional[str] = None


def analyze_emotion(text: str) -> str:
    """
    Classify the emotion of the student's message into one of ALLOWED_EMOTIONS.
    Returns a single lowercase word, defaulting to 'neutral' on error.
    
    Includes rate limiting to avoid excessive API calls.
    Caches results for config.GEMINI_EMOTION_CACHE_SECONDS.
    """
    if not text or not text.strip():
        return "neutral"

    # Check rate limiting cache
    current_time = time.time()
    cache_duration = config.GEMINI_EMOTION_CACHE_SECONDS
    
    with _emotion_cache_lock:
        if (_last_emotion_request_time is not None and 
            _last_emotion_result is not None and
            current_time - _last_emotion_request_time < cache_duration):
            # Return cached result
            print(f"[Gemini][analyze_emotion] Using cached result (age: {current_time - _last_emotion_request_time:.1f}s)")
            return _last_emotion_result

    # Cache expired or doesn't exist - call API
    prompt = f"""
You are part of an AI therapy assistant for university students.

Classify the dominant emotional tone of this message into exactly ONE of:
{", ".join(ALLOWED_EMOTIONS)}

Rules:
- Respond with ONLY the emotion word, lowercase.
- No punctuation, no explanation.

Message:
\"\"\"{text}\"\"\"
"""

    try:
        response = model.generate_content(prompt)
        raw = (response.text or "").strip().lower()
    except Exception as e:
        print("[Gemini][analyze_emotion] Error:", e)
        return "neutral"

    # Try to map the output to one of our known labels
    emotion_result = "neutral"
    for emo in ALLOWED_EMOTIONS:
        if emo in raw:
            emotion_result = emo
            break

    # Update cache
    with _emotion_cache_lock:
        _last_emotion_request_time = current_time
        _last_emotion_result = emotion_result

    return emotion_result


def chat_with_gemini(user_text: str, emotion: str) -> str:
    """
    Generate a short, supportive reply for the user.
    `emotion` should come from analyze_emotion().
    """
    if not user_text or not user_text.strip():
        user_text = "..."

    if emotion not in ALLOWED_EMOTIONS:
        emotion = "neutral"

    system_instructions = f"""
You are a supportive, non-clinical student therapy assistant.
The student's detected emotion is: {emotion}.

Guidelines:
- Use simple, conversational English.
- 2–4 sentences max.
- Validate their feelings (e.g. "It's understandable that...").
- Offer ONE small, concrete suggestion (e.g. tiny next step, short break, breathing).
- Do NOT say you 'detected' their emotion; respond naturally.
- Do NOT give medical or diagnostic advice.
- You may gently suggest reaching out to a friend, family member,
  or professional if things feel overwhelming.
"""

    full_prompt = f"""{system_instructions}

Student:
\"\"\"{user_text}\"\"\"

Reply:"""

    try:
        response = model.generate_content(full_prompt)
        reply = (response.text or "").strip()
        return reply
    except Exception as e:
        print("[Gemini][chat_with_gemini] Error:", e)
        return (
            "I'm having a bit of trouble thinking right now, but your feelings still matter. "
            "Try taking a few slow breaths, and maybe write down one small thing you can do next."
        )


def generate_daily_summary(context: dict) -> str:
    """
    Generate a friendly, caring daily therapy summary based on today's emotional data.
    
    Args:
        context: Dictionary containing daily summary context from mental_health_analyzer
    
    Returns:
        A 2-4 sentence friendly summary with gentle suggestions
    """
    if not context.get("has_data", False):
        return (
            "Today was quiet - no therapy sessions logged. "
            "Remember, it's okay to take things slow. "
            "If you'd like to chat, I'm here whenever you need."
        )
    
    # Build context string for prompt
    date = context.get("date", "today")
    sessions = context.get("session_count", 0)
    avg_score = context.get("average_score", 5.0)
    dominant_emotions = context.get("dominant_emotions", [])
    high_times = context.get("high_mood_times", [])
    low_times = context.get("low_mood_times", [])
    
    context_str = f"""
Date: {date}
Sessions: {sessions}
Average mental health score: {avg_score:.1f}/10
Dominant emotions: {', '.join(dominant_emotions) if dominant_emotions else 'neutral'}
"""
    
    if high_times:
        context_str += f"Higher mood periods: {', '.join(high_times)}\n"
    if low_times:
        context_str += f"Lower mood periods: {', '.join(low_times)}\n"
    
    prompt = f"""
You are a caring, supportive therapy assistant providing a daily emotional summary.

Based on today's session data:
{context_str}

Write a brief, friendly daily summary (2-4 sentences) that:
- Acknowledges their emotional journey today
- Validates their feelings naturally
- Provides 1-2 gentle, concrete suggestions for tomorrow
- Sounds warm and supportive, not clinical or robotic
- Does NOT mention specific scores or numbers directly

Write as if you're a caring friend checking in, not a medical professional.

Daily Summary:
"""
    
    try:
        response = model.generate_content(prompt)
        summary = (response.text or "").strip()
        
        # If summary is too short or seems like an error, provide fallback
        if len(summary) < 20:
            raise ValueError("Summary too short")
        
        return summary
    except Exception as e:
        print(f"[Gemini][generate_daily_summary] Error: {e}")
        
        # Fallback summary
        if avg_score >= 7:
            return (
                f"Today you had {sessions} session(s) and seemed to be doing well. "
                "Keep up the good work! Consider continuing activities that bring you peace. "
                "Remember to celebrate small wins - you're doing great."
            )
        elif avg_score <= 4:
            return (
                f"Today was challenging - you had {sessions} session(s). "
                "Your feelings are valid and it's okay to have tough days. "
                "Tomorrow, try starting with one small, manageable task. "
                "Be gentle with yourself - healing takes time."
            )
        else:
            return (
                f"You checked in {sessions} time(s) today. "
                "Every day is a step forward, even if it doesn't always feel like it. "
                "Tomorrow, try to notice one moment of peace or gratitude. "
                "You're making progress just by being here."
            )


if __name__ == "__main__":
    # Quick manual test when you run: python -m ai.gemini_client
    test_msg = "I'm really stressed about my midterm and I feel like I'm going to fail."
    emo = analyze_emotion(test_msg)
    print("Detected emotion:", emo)
    reply = chat_with_gemini(test_msg, emo)
    print("AI reply:", reply)
