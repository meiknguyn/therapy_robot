# dashboard/mental_health_analyzer.py
"""
Mental Health Analyzer Module
Processes CSV data to extract mental health metrics and trends.
"""
import csv
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Emotion scoring system (1-10 scale, 10 = best mental health)
EMOTION_SCORES = {
    # Positive emotions (high scores)
    "joy": 9,
    "happy": 9,
    "excited": 8,
    "grateful": 9,
    "calm": 8,
    "peaceful": 8,
    "content": 8,
    "relaxed": 7,
    "satisfied": 7,
    "hopeful": 7,
    
    # Neutral emotions
    "neutral": 5,
    "normal": 5,
    "okay": 5,
    "fine": 5,
    
    # Negative emotions (low scores)
    "sad": 3,
    "depressed": 2,
    "anxious": 3,
    "anxiety": 3,
    "worried": 4,
    "stressed": 3,
    "frustrated": 3,
    "angry": 2,
    "lonely": 3,
    "overwhelmed": 2,
    "tired": 4,
    "exhausted": 2,
    "nervous": 3,
    "fearful": 2,
    "disappointed": 3,
    "guilty": 2,
    "ashamed": 2,
}


def emotion_to_score(emotion: str) -> float:
    """
    Convert emotion string to numeric score (1-10).
    
    Args:
        emotion: Emotion string (case-insensitive)
    
    Returns:
        Score from 1-10 (5 if emotion not found)
    """
    if not emotion:
        return 5.0
    
    emotion_lower = emotion.lower().strip()
    
    # Check exact match first
    if emotion_lower in EMOTION_SCORES:
        return float(EMOTION_SCORES[emotion_lower])
    
    # Check if emotion contains any keyword
    for key, score in EMOTION_SCORES.items():
        if key in emotion_lower:
            return float(score)
    
    # Default neutral score
    return 5.0


class MentalHealthAnalyzer:
    """
    Analyzes mental health trends from CSV log files.
    """

    def __init__(self, chats_csv_path="logs/chats.csv"):
        """
        Initialize analyzer.
        
        Args:
            chats_csv_path: Path to chats CSV file
        """
        self.chats_csv_path = chats_csv_path

    def load_chats(self):
        """
        Load all chats from CSV file.
        
        Returns:
            List of dicts with chat data
        """
        if not os.path.exists(self.chats_csv_path):
            return []
        
        chats = []
        try:
            with open(self.chats_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chats.append({
                        "timestamp": row.get("timestamp", ""),
                        "user_text": row.get("user_text", ""),
                        "emotion": row.get("emotion", ""),
                        "bot_reply": row.get("bot_reply", ""),
                        "score": emotion_to_score(row.get("emotion", ""))
                    })
        except Exception as e:
            print(f"[MentalHealthAnalyzer] Error loading chats: {e}")
            return []
        
        return chats

    def parse_timestamp(self, timestamp_str: str):
        """Parse timestamp string to datetime object."""
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                return datetime.strptime(timestamp_str, "%Y-%m-%d")
            except:
                return None

    def get_daily_trends(self, days=30):
        """
        Get daily mental health trends.
        
        Args:
            days: Number of days to include
        
        Returns:
            Dict with dates as keys and average scores as values
        """
        chats = self.load_chats()
        if not chats:
            return {}
        
        daily_scores = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt and dt >= cutoff_date:
                date_key = dt.date().isoformat()
                daily_scores[date_key].append(chat["score"])
        
        # Calculate daily averages
        daily_trends = {}
        for date_str, scores in sorted(daily_scores.items()):
            if scores:
                daily_trends[date_str] = {
                    "average": sum(scores) / len(scores),
                    "count": len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
        
        return daily_trends

    def get_weekly_trends(self, weeks=12):
        """
        Get weekly mental health trends.
        
        Args:
            weeks: Number of weeks to include
        
        Returns:
            Dict with week identifiers as keys and average scores as values
        """
        chats = self.load_chats()
        if not chats:
            return {}
        
        weekly_scores = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt and dt >= cutoff_date:
                # Get year and week number
                year, week, _ = dt.isocalendar()
                week_key = f"{year}-W{week:02d}"
                weekly_scores[week_key].append(chat["score"])
        
        # Calculate weekly averages
        weekly_trends = {}
        for week_str, scores in sorted(weekly_scores.items()):
            if scores:
                weekly_trends[week_str] = {
                    "average": sum(scores) / len(scores),
                    "count": len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
        
        return weekly_trends

    def get_monthly_trends(self, months=12):
        """
        Get monthly mental health trends.
        
        Args:
            months: Number of months to include
        
        Returns:
            Dict with month identifiers as keys and average scores as values
        """
        chats = self.load_chats()
        if not chats:
            return {}
        
        monthly_scores = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt and dt >= cutoff_date:
                month_key = dt.strftime("%Y-%m")
                monthly_scores[month_key].append(chat["score"])
        
        # Calculate monthly averages
        monthly_trends = {}
        for month_str, scores in sorted(monthly_scores.items()):
            if scores:
                monthly_trends[month_str] = {
                    "average": sum(scores) / len(scores),
                    "count": len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
        
        return monthly_trends

    def get_yearly_trends(self):
        """
        Get yearly mental health trends.
        
        Returns:
            Dict with years as keys and average scores as values
        """
        chats = self.load_chats()
        if not chats:
            return {}
        
        yearly_scores = defaultdict(list)
        
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt:
                year_key = str(dt.year)
                yearly_scores[year_key].append(chat["score"])
        
        # Calculate yearly averages
        yearly_trends = {}
        for year_str, scores in sorted(yearly_scores.items()):
            if scores:
                yearly_trends[year_str] = {
                    "average": sum(scores) / len(scores),
                    "count": len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
        
        return yearly_trends

    def get_overall_stats(self):
        """
        Get overall mental health statistics.
        
        Returns:
            Dict with overall statistics
        """
        chats = self.load_chats()
        if not chats:
            return {
                "total_chats": 0,
                "average_score": 5.0,
                "current_trend": "stable"
            }
        
        scores = [chat["score"] for chat in chats]
        
        # Calculate trend (last 7 days vs previous 7 days)
        recent_cutoff = datetime.now() - timedelta(days=7)
        older_cutoff = datetime.now() - timedelta(days=14)
        
        recent_scores = []
        older_scores = []
        
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt:
                if dt >= recent_cutoff:
                    recent_scores.append(chat["score"])
                elif dt >= older_cutoff:
                    older_scores.append(chat["score"])
        
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 5.0
        older_avg = sum(older_scores) / len(older_scores) if older_scores else 5.0
        
        trend = "stable"
        if recent_avg > older_avg + 0.5:
            trend = "improving"
        elif recent_avg < older_avg - 0.5:
            trend = "declining"
        
        return {
            "total_chats": len(chats),
            "average_score": sum(scores) / len(scores) if scores else 5.0,
            "current_trend": trend,
            "recent_average": recent_avg,
            "previous_average": older_avg
        }

    def get_daily_summary_context(self, date: datetime = None):
        """
        Build daily summary context for a specific date (defaults to today).
        
        Args:
            date: Date to summarize (defaults to today)
        
        Returns:
            Dict with aggregated daily data for summary generation
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.date().isoformat()
        chats = self.load_chats()
        
        # Filter chats for today
        today_chats = []
        for chat in chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt and dt.date().isoformat() == date_str:
                today_chats.append(chat)
        
        if not today_chats:
            return {
                "date": date_str,
                "session_count": 0,
                "average_score": 5.0,
                "dominant_emotions": [],
                "high_mood_times": [],
                "low_mood_times": [],
                "has_data": False
            }
        
        # Calculate statistics
        scores = [chat["score"] for chat in today_chats]
        avg_score = sum(scores) / len(scores)
        
        # Find dominant emotions
        emotion_counts = defaultdict(int)
        for chat in today_chats:
            emotion = chat.get("emotion", "").lower()
            if emotion:
                emotion_counts[emotion] += 1
        
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        dominant_emotions = [emo for emo, count in dominant_emotions]
        
        # Find high/low mood time windows (simple: morning/afternoon/evening)
        time_windows = {"morning": [], "afternoon": [], "evening": []}
        for chat in today_chats:
            dt = self.parse_timestamp(chat["timestamp"])
            if dt:
                hour = dt.hour
                if 6 <= hour < 12:
                    time_windows["morning"].append(chat["score"])
                elif 12 <= hour < 18:
                    time_windows["afternoon"].append(chat["score"])
                else:
                    time_windows["evening"].append(chat["score"])
        
        high_mood_times = []
        low_mood_times = []
        
        for period, period_scores in time_windows.items():
            if period_scores:
                avg_period_score = sum(period_scores) / len(period_scores)
                if avg_period_score >= 7:
                    high_mood_times.append(period)
                elif avg_period_score <= 4:
                    low_mood_times.append(period)
        
        return {
            "date": date_str,
            "session_count": len(today_chats),
            "average_score": avg_score,
            "dominant_emotions": dominant_emotions,
            "high_mood_times": high_mood_times,
            "low_mood_times": low_mood_times,
            "score_range": {"min": min(scores), "max": max(scores)},
            "has_data": True
        }

    def compute_trend_for_period(self, days: int = 7):
        """
        Compute trend classification for the last N days.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            String: "improving", "stable", or "declining"
        """
        daily_trends = self.get_daily_trends(days=days * 2)  # Get more days for comparison
        
        if not daily_trends or len(daily_trends) < 3:
            return "stable"
        
        # Get dates and averages
        dates = sorted(daily_trends.keys())
        
        # Split into recent and previous periods
        split_point = len(dates) // 2
        recent_dates = dates[split_point:]
        previous_dates = dates[:split_point]
        
        if not recent_dates or not previous_dates:
            return "stable"
        
        recent_avg = sum(daily_trends[d]["average"] for d in recent_dates) / len(recent_dates)
        previous_avg = sum(daily_trends[d]["average"] for d in previous_dates) / len(previous_dates)
        
        # Import config for threshold
        try:
            from therapy_robot import config
            threshold = config.TREND_THRESHOLD
        except:
            threshold = 0.5
        
        diff = recent_avg - previous_avg
        
        if diff > threshold:
            return "improving"
        elif diff < -threshold:
            return "declining"
        else:
            return "stable"

