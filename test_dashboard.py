#!/usr/bin/env python3
"""Test script for the Therapy Robot dashboard components."""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot import config
from therapy_robot.dashboard import csv_logger
from therapy_robot.dashboard.mental_health_analyzer import compute_basic_stats


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_csv_logging():
    """Test CSV logging functionality."""
    print_section("Testing CSV Logger")
    
    # Test event logging
    print("\n1. Testing event logging...")
    csv_logger.log_event("test_event", {"test": "value", "number": 42})
    csv_logger.log_event("led_change", {"brightness": 0.7})
    csv_logger.log_event("ambient_light", {"value": 0.45})
    print("   ✓ Logged 3 test events")
    
    # Test chat logging
    print("\n2. Testing chat logging...")
    csv_logger.log_chat("I feel happy today!", 8, "That's wonderful to hear!")
    csv_logger.log_chat("I'm stressed about exams", 3, "That's understandable. Let's work through this together.")
    csv_logger.log_chat("I'm okay", 5, "Thanks for checking in.")
    print("   ✓ Logged 3 test chat interactions")
    
    print("\n✓ CSV logging tests passed!")


def display_events():
    """Display logged events."""
    print_section("Event Log Analysis")
    
    if not config.EVENT_LOG_PATH.exists():
        print("   No events logged yet.")
        return
    
    try:
        df = pd.read_csv(config.EVENT_LOG_PATH)
        print(f"\n   Total events: {len(df)}")
        print(f"   Log file: {config.EVENT_LOG_PATH}")
        print(f"   File size: {config.EVENT_LOG_PATH.stat().st_size} bytes")
        
        print("\n   Event types:")
        event_counts = df['event_type'].value_counts()
        for event_type, count in event_counts.items():
            print(f"     - {event_type}: {count}")
        
        print("\n   Recent events (last 5):")
        print("   " + "-" * 56)
        for idx, row in df.tail(5).iterrows():
            timestamp = row['timestamp'][:19]  # Remove microseconds
            print(f"   {timestamp} | {row['event_type']:20s} | {row['details'][:30]}")
        
    except Exception as e:
        print(f"   Error reading events: {e}")


def display_chats():
    """Display logged chat interactions."""
    print_section("Chat Log Analysis")
    
    if not config.CHAT_LOG_PATH.exists():
        print("   No chats logged yet.")
        return
    
    try:
        df = pd.read_csv(config.CHAT_LOG_PATH)
        print(f"\n   Total chat interactions: {len(df)}")
        print(f"   Log file: {config.CHAT_LOG_PATH}")
        print(f"   File size: {config.CHAT_LOG_PATH.stat().st_size} bytes")
        
        if len(df) > 0:
            print("\n   Mood Statistics:")
            avg_mood = df['emotion_score'].mean()
            min_mood = df['emotion_score'].min()
            max_mood = df['emotion_score'].max()
            print(f"     - Average mood: {avg_mood:.2f}/10")
            print(f"     - Lowest mood: {min_mood}/10")
            print(f"     - Highest mood: {max_mood}/10")
            
            print("\n   Mood Distribution:")
            mood_counts = df['emotion_score'].value_counts().sort_index()
            for mood, count in mood_counts.items():
                bar = "█" * count
                print(f"     {mood}/10: {bar} ({count})")
            
            print("\n   Recent conversations (last 3):")
            print("   " + "-" * 56)
            for idx, row in df.tail(3).iterrows():
                timestamp = row['timestamp'][:19]
                print(f"\n   [{timestamp}]")
                print(f"   User (mood={row['emotion_score']}/10): {row['user_text']}")
                print(f"   Robot: {row['bot_reply'][:80]}...")
        
    except Exception as e:
        print(f"   Error reading chats: {e}")


def compute_dashboard_stats():
    """Compute and display dashboard statistics."""
    print_section("Dashboard Statistics")
    
    stats = compute_basic_stats()
    print("\n   Basic Stats (from analyzer):")
    print(f"     - Total sessions: {stats['total_sessions']}")
    print(f"     - Average mood: {stats['average_mood']:.2f}/10")
    print(f"     - Trend: {stats['trend']}")
    
    # Compute actual stats from CSV files
    print("\n   Actual Stats (from CSV files):")
    
    if config.CHAT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            if len(df) > 0:
                actual_avg = df['emotion_score'].mean()
                print(f"     - Total interactions: {len(df)}")
                print(f"     - Average mood: {actual_avg:.2f}/10")
                
                # Determine trend (simple: compare first half vs second half)
                if len(df) >= 4:
                    mid = len(df) // 2
                    first_half_avg = df.iloc[:mid]['emotion_score'].mean()
                    second_half_avg = df.iloc[mid:]['emotion_score'].mean()
                    
                    if second_half_avg > first_half_avg + 0.5:
                        trend = "improving"
                    elif second_half_avg < first_half_avg - 0.5:
                        trend = "declining"
                    else:
                        trend = "stable"
                    print(f"     - Mood trend: {trend}")
            else:
                print("     - No chat data available")
        except Exception as e:
            print(f"     - Error computing stats: {e}")
    else:
        print("     - No chat log file found")
    
    if config.EVENT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.EVENT_LOG_PATH)
            print(f"     - Total events: {len(df)}")
        except Exception as e:
            print(f"     - Error reading events: {e}")


def display_dashboard_summary():
    """Display a summary dashboard view."""
    print_section("Dashboard Summary")
    
    print("\n   📊 Therapy Robot Dashboard")
    print("   " + "-" * 56)
    
    # Check file status
    events_exist = config.EVENT_LOG_PATH.exists()
    chats_exist = config.CHAT_LOG_PATH.exists()
    
    print(f"\n   Log Files Status:")
    print(f"     Events: {'✓' if events_exist else '✗'} {config.EVENT_LOG_PATH}")
    print(f"     Chats:  {'✓' if chats_exist else '✗'} {config.CHAT_LOG_PATH}")
    
    if chats_exist:
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            if len(df) > 0:
                print(f"\n   📈 Quick Stats:")
                print(f"     Total conversations: {len(df)}")
                print(f"     Average mood: {df['emotion_score'].mean():.2f}/10")
                print(f"     Date range: {df['timestamp'].iloc[0][:10]} to {df['timestamp'].iloc[-1][:10]}")
        except Exception as e:
            print(f"     Error: {e}")


def main():
    """Run dashboard tests."""
    print("\n" + "=" * 60)
    print("  Therapy Robot - Dashboard Test Suite")
    print("=" * 60)
    
    # Test CSV logging
    test_csv_logging()
    
    # Display logged data
    display_events()
    display_chats()
    
    # Compute statistics
    compute_dashboard_stats()
    
    # Display summary
    display_dashboard_summary()
    
    print("\n" + "=" * 60)
    print("  Dashboard Test Complete!")
    print("=" * 60)
    print("\n💡 Tip: Run the main program to generate more log data:")
    print("   python -m therapy_robot.main")
    print()


if __name__ == "__main__":
    main()

