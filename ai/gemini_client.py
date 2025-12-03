"""Gemini API client for emotion analysis and therapy support."""

import re
import threading
import time
from typing import Dict, Any

try:
    import google.genai as genai
except ImportError:
    try:
        import google_genai as genai
    except ImportError:
        genai = None

from therapy_robot import config

# Thread-safe client singleton
_client = None
_client_api_key = None  # Track which API key was used
_client_lock = threading.Lock()

# Emotion cache
_emotion_cache = {}
_emotion_cache_lock = threading.Lock()
_cache_timestamp = None


def _get_client():
    """Get or create the Gemini client instance."""
    global _client, _client_api_key
    
    # Check if we need to recreate the client (API key changed)
    current_key = config.GEMINI_API_KEY
    if _client is None or _client_api_key != current_key:
        with _client_lock:
            # Double-check after acquiring lock
            if _client is None or _client_api_key != current_key:
                if not current_key:
                    raise ValueError(
                        "GEMINI_API_KEY environment variable is not set. "
                        "Please set it with: export GEMINI_API_KEY='your_key_here'"
                    )
                if genai is None:
                    raise ImportError(
                        "google-genai package is not installed. "
                        "Install it with: pip install google-genai"
                    )
                # Close old client if it exists
                if _client is not None:
                    try:
                        _client.close()
                    except:
                        pass
                # Create new client with current API key
                _client = genai.Client(api_key=current_key)
                _client_api_key = current_key
    
    return _client


def reset_client():
    """Reset the cached client (useful when API key changes)."""
    global _client, _client_api_key
    with _client_lock:
        if _client is not None:
            try:
                _client.close()
            except:
                pass
        _client = None
        _client_api_key = None


def analyze_emotion_with_cache(user_text: str) -> Dict[str, Any]:
    """
    Analyze emotion from user text with caching.
    
    First tries Gemini API for intelligent analysis, falls back to comprehensive
    keyword-based scoring. Returns cached result if called within 
    GEMINI_EMOTION_CACHE_SECONDS.
    
    Args:
        user_text: User's input text
        
    Returns:
        Dict with "score" (int, 1-10) and "raw_text" (str)
    """
    global _emotion_cache, _cache_timestamp
    
    current_time = time.time()
    
    with _emotion_cache_lock:
        # Check cache
        if (_cache_timestamp is not None and 
            current_time - _cache_timestamp < config.GEMINI_EMOTION_CACHE_SECONDS):
            return _emotion_cache.copy()
        
        # Try Gemini API first for intelligent emotion analysis
        score = _analyze_emotion_with_gemini(user_text)
        
        # If Gemini failed, use comprehensive keyword-based fallback
        if score is None:
            score = _analyze_emotion_with_keywords(user_text)
        
        result = {
            "score": score,
            "raw_text": user_text
        }
        
        # Update cache
        _emotion_cache = result.copy()
        _cache_timestamp = current_time
        
        return result


def _analyze_emotion_with_gemini(user_text: str) -> int:
    """
    Use Gemini API to analyze emotion. Returns score (1-10) or None if fails.
    """
    if not config.GEMINI_API_KEY:
        return None
    
    try:
        client = _get_client()
        
        prompt = f"""Analyze the emotional state expressed in this text and provide a mood score from 1-10:
- 1-2: Extremely negative (suicidal, severe depression, panic)
- 3-4: Very negative (anxious, stressed, sad, overwhelmed)
- 5-6: Neutral to slightly negative (okay, fine, a bit worried, slightly down)
- 7-8: Positive (happy, content, grateful, excited)
- 9-10: Extremely positive (ecstatic, euphoric, very happy)

Text: "{user_text}"

Respond with ONLY a single number from 1-10, nothing else."""
        
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt
        )
        
        # Extract number from response
        response_text = response.text.strip()
        # Try to find a number in the response
        numbers = re.findall(r'\b([1-9]|10)\b', response_text)
        if numbers:
            score = int(numbers[0])
            # Clamp to valid range
            score = max(1, min(10, score))
            return score
    except Exception as e:
        # Silently fail and fall back to keyword analysis
        pass
    
    return None


def _analyze_emotion_with_keywords(user_text: str) -> int:
    """
    Comprehensive keyword-based emotion scoring with full 1-10 range.
    """
    text_lower = user_text.lower()
    
    # Intensity modifiers
    very_intense = any(word in text_lower for word in [
        "extremely", "incredibly", "absolutely", "completely", "totally",
        "really", "very", "so", "super", "ultra", "intensely"
    ])
    
    slightly_moderate = any(word in text_lower for word in [
        "slightly", "a bit", "a little", "somewhat", "kind of", "sort of",
        "pretty", "quite", "rather"
    ])
    
    # Extremely negative (1-2)
    extreme_negative = [
        "suicide", "kill myself", "end it all", "want to die", "no point",
        "hopeless", "worthless", "useless", "can't go on", "give up",
        "self harm", "hurt myself", "cut myself"
    ]
    
    # Very negative (3-4)
    very_negative = [
        "sad", "depressed", "anxious", "stressed", "overwhelmed", "worried",
        "fear", "scared", "afraid", "terrified", "panic", "nervous",
        "frustrated", "angry", "mad", "upset", "disappointed", "hurt",
        "lonely", "isolated", "exhausted", "tired", "burnout", "burned out",
        "exam", "test", "deadline", "assignment", "project due", "can't finish",
        "failing", "failed", "bad grade", "poor grade", "struggling",
        "difficult", "hard", "impossible", "can't do", "don't understand"
    ]
    
    # Moderately negative (4-5)
    moderate_negative = [
        "not great", "not good", "not okay", "not fine", "meh", "bleh",
        "tired", "sleepy", "bored", "unmotivated", "procrastinating",
        "confused", "uncertain", "unsure", "don't know", "lost"
    ]
    
    # Neutral (5-6)
    neutral = [
        "okay", "fine", "normal", "alright", "ok", "same", "usual",
        "nothing", "nothing much", "same as always", "nothing special"
    ]
    
    # Moderately positive (6-7)
    moderate_positive = [
        "good", "nice", "decent", "okay", "fine", "not bad", "pretty good",
        "better", "improving", "getting better", "feeling better"
    ]
    
    # Positive (7-8)
    positive = [
        "happy", "glad", "pleased", "content", "satisfied", "grateful",
        "thankful", "appreciate", "excited", "thrilled", "pumped",
        "motivated", "inspired", "energized", "confident", "proud",
        "accomplished", "successful", "did it", "finished", "completed"
    ]
    
    # Very positive (8-9)
    very_positive = [
        "great", "wonderful", "amazing", "fantastic", "awesome", "excellent",
        "brilliant", "outstanding", "incredible", "unbelievable", "perfect",
        "best", "love it", "so happy", "so excited", "ecstatic"
    ]
    
    # Extremely positive (9-10)
    extreme_positive = [
        "ecstatic", "euphoric", "overjoyed", "thrilled", "elated",
        "on cloud nine", "walking on air", "best day ever", "perfect day",
        "couldn't be happier", "so grateful", "blessed", "lucky"
    ]
    
    # Check for extreme negative first (highest priority)
    if any(word in text_lower for word in extreme_negative):
        return 1 if very_intense else 2
    
    # Check for very negative
    if any(word in text_lower for word in very_negative):
        if very_intense:
            return 2
        elif slightly_moderate:
            return 4
        else:
            return 3
    
    # Check for moderate negative
    if any(word in text_lower for word in moderate_negative):
        if very_intense:
            return 3
        elif slightly_moderate:
            return 5
        else:
            return 4
    
    # Check for neutral
    if any(word in text_lower for word in neutral):
        if "not" in text_lower or "bad" in text_lower:
            return 4
        elif "good" in text_lower or "great" in text_lower:
            return 6
        else:
            return 5
    
    # Check for moderate positive
    if any(word in text_lower for word in moderate_positive):
        if very_intense:
            return 7
        elif slightly_moderate:
            return 6
        else:
            return 6
    
    # Check for positive
    if any(word in text_lower for word in positive):
        if very_intense:
            return 8
        elif slightly_moderate:
            return 7
        else:
            return 7
    
    # Check for very positive
    if any(word in text_lower for word in very_positive):
        if very_intense:
            return 9
        else:
            return 8
    
    # Check for extreme positive
    if any(word in text_lower for word in extreme_positive):
        return 9 if very_intense else 10
    
    # Default: neutral
    return 5


def get_support_reply(mood_score: int, user_text: str) -> str:
    """
    Get a supportive reply from Gemini based on mood score and user text.
    
    Args:
        mood_score: Emotion score (1-10)
        user_text: User's input text
        
    Returns:
        Supportive reply string (80-100 words)
    """
    client = _get_client()
    
    # Safety check for self-harm or danger
    danger_keywords = ["self-harm", "suicide", "kill myself", "end it", "hurt myself"]
    if any(keyword in user_text.lower() for keyword in danger_keywords):
        return (
            "I'm concerned about what you've shared. Please reach out to a mental health "
            "professional or emergency services immediately. You can call 988 (Suicide & Crisis "
            "Lifeline) or 911. Your life matters, and there are people who can help you right now."
        )
    
    # System prompt
    SYSTEM_PROMPT = (
        "You are a gentle, supportive therapy companion for a stressed student. "
        "Your role is to:\n"
        "1. Reflect their feelings briefly\n"
        "2. Normalize their emotions\n"
        "3. Offer 1-2 small, realistic coping suggestions\n"
        "Keep your reply under 80-100 words. Be warm, empathetic, and non-judgmental."
    )
    
    # Build the prompt
    prompt = f"""User's mood score: {mood_score}/10
User said: "{user_text}"

Please provide a supportive response following the guidelines above."""

    try:
        # Use the working API pattern: Direct generate_content on client.models
        # This pattern works reliably with the google-genai library
        try:
            # Pattern 1: Direct generate_content with system_instruction in config
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config={"system_instruction": SYSTEM_PROMPT}
            )
            reply = response.text.strip()
        except (AttributeError, TypeError, KeyError) as e:
            # Pattern 2: Fallback - include system instruction in prompt
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=full_prompt
            )
            reply = response.text.strip()
        
        return reply
    
    except Exception as e:
        # Fallback response if API fails
        error_msg = str(e)
        # Check if it's an API key error specifically
        if "API key" in error_msg or "INVALID_ARGUMENT" in error_msg or "API_KEY" in str(type(e).__name__):
            print(f"Error: Gemini API key issue - {error_msg}")
            print("Please check:")
            print("  1. Your API key in .env file is correct")
            print("  2. Your API key is active at https://aistudio.google.com/app/apikey")
            print("  3. The API key has proper permissions")
        else:
            print(f"Warning: Gemini API error: {error_msg}")
        return (
            f"I hear that you're feeling this way (mood: {mood_score}/10). "
            "It's okay to have difficult emotions. Try taking a few deep breaths, "
            "or step outside for a moment if you can. Remember, you're not alone in this."
        )

