import os
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------------------------------------------------
# Load API key from config/secrets.env
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
ENV_PATH = os.path.join(BASE_DIR, "config", "secrets.env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")
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


def analyze_emotion(text: str) -> str:
    """
    Classify the emotion of the student's message into one of ALLOWED_EMOTIONS.
    Returns a single lowercase word, defaulting to 'neutral' on error.
    """
    if not text or not text.strip():
        return "neutral"

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
    for emo in ALLOWED_EMOTIONS:
        if emo in raw:
            return emo

    return "neutral"


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


if __name__ == "__main__":
    # Quick manual test when you run: python -m ai.gemini_client
    test_msg = "I'm really stressed about my midterm and I feel like I'm going to fail."
    emo = analyze_emotion(test_msg)
    print("Detected emotion:", emo)
    reply = chat_with_gemini(test_msg, emo)
    print("AI reply:", reply)
