"""Mental health analytics and statistics.

This module analyzes chat logs and provides insights about user's mental health trends.
"""

import pandas as pd
from pathlib import Path

from therapy_robot import config


def compute_basic_stats() -> dict:
    """
    Compute basic statistics from chat logs.
    
    Returns:
        Dictionary with basic statistics
    """
    stats = {
        "total_sessions": 0,
        "average_mood": 0.0,
        "trend": "stable"
    }
    
    if not config.CHAT_LOG_PATH.exists():
        return stats
    
    try:
        df = pd.read_csv(config.CHAT_LOG_PATH)
        
        if len(df) == 0:
            return stats
        
        stats["total_sessions"] = len(df)
        stats["average_mood"] = float(df['emotion_score'].mean())
        
        # Determine trend (compare first half vs second half)
        if len(df) >= 4:
            mid = len(df) // 2
            first_half_avg = df.iloc[:mid]['emotion_score'].mean()
            second_half_avg = df.iloc[mid:]['emotion_score'].mean()
            
            if second_half_avg > first_half_avg + 0.5:
                stats["trend"] = "improving"
            elif second_half_avg < first_half_avg - 0.5:
                stats["trend"] = "declining"
            else:
                stats["trend"] = "stable"
        else:
            stats["trend"] = "stable"
            
    except Exception as e:
        # Return default stats on error
        pass
    
    return stats

