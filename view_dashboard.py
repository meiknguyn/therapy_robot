#!/usr/bin/env python3
"""Interactive dashboard viewer for Therapy Robot logs."""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from therapy_robot import config


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def view_events(limit=10):
    """View recent events."""
    print_header("Recent Events")
    
    if not config.EVENT_LOG_PATH.exists():
        print("\n   No events logged yet.")
        return
    
    try:
        df = pd.read_csv(config.EVENT_LOG_PATH)
        
        if len(df) == 0:
            print("\n   No events in log file.")
            return
        
        print(f"\n   Total events: {len(df)}")
        print(f"   Showing last {min(limit, len(df))} events:\n")
        
        print(f"   {'Timestamp':<20} {'Event Type':<20} {'Details':<30}")
        print("   " + "-" * 70)
        
        for idx, row in df.tail(limit).iterrows():
            timestamp = row['timestamp'][:19].replace('T', ' ')
            event_type = row['event_type'][:18]
            details = str(row['details'])[:28] if pd.notna(row['details']) else ""
            print(f"   {timestamp:<20} {event_type:<20} {details:<30}")
        
        # Event type summary
        print("\n   Event Type Summary:")
        event_counts = df['event_type'].value_counts()
        for event_type, count in event_counts.items():
            print(f"     • {event_type}: {count} occurrences")
            
    except Exception as e:
        print(f"\n   Error reading events: {e}")


def view_chats(limit=10):
    """View recent chat interactions."""
    print_header("Recent Chat Interactions")
    
    if not config.CHAT_LOG_PATH.exists():
        print("\n   No chats logged yet.")
        return
    
    try:
        df = pd.read_csv(config.CHAT_LOG_PATH)
        
        if len(df) == 0:
            print("\n   No chats in log file.")
            return
        
        print(f"\n   Total interactions: {len(df)}")
        print(f"   Showing last {min(limit, len(df))} interactions:\n")
        
        for idx, row in df.tail(limit).iterrows():
            timestamp = row['timestamp'][:19].replace('T', ' ')
            mood = row['emotion_score']
            user_text = row['user_text']
            bot_reply = row['bot_reply'][:100]  # Truncate long replies
            
            print(f"   [{timestamp}] Mood: {mood}/10")
            print(f"   👤 User: {user_text}")
            print(f"   🤖 Robot: {bot_reply}...")
            print()
        
    except Exception as e:
        print(f"\n   Error reading chats: {e}")


def view_statistics():
    """View statistics and analytics."""
    print_header("Statistics & Analytics")
    
    stats = {}
    
    # Chat statistics
    if config.CHAT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            if len(df) > 0:
                stats['total_chats'] = len(df)
                stats['avg_mood'] = df['emotion_score'].mean()
                stats['min_mood'] = df['emotion_score'].min()
                stats['max_mood'] = df['emotion_score'].max()
                stats['mood_std'] = df['emotion_score'].std()
                
                # Mood distribution
                mood_dist = df['emotion_score'].value_counts().sort_index()
                stats['mood_dist'] = mood_dist
                
                # Trend analysis
                if len(df) >= 4:
                    mid = len(df) // 2
                    first_half = df.iloc[:mid]['emotion_score'].mean()
                    second_half = df.iloc[mid:]['emotion_score'].mean()
                    diff = second_half - first_half
                    
                    if diff > 0.5:
                        stats['trend'] = "📈 Improving"
                    elif diff < -0.5:
                        stats['trend'] = "📉 Declining"
                    else:
                        stats['trend'] = "➡️ Stable"
                else:
                    stats['trend'] = "➡️ Stable (insufficient data)"
        except Exception as e:
            print(f"   Error computing chat stats: {e}")
            return
    
    # Event statistics
    if config.EVENT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.EVENT_LOG_PATH)
            stats['total_events'] = len(df)
            if len(df) > 0:
                stats['event_types'] = df['event_type'].value_counts()
        except Exception as e:
            print(f"   Error computing event stats: {e}")
    
    # Display statistics
    print("\n   📊 Chat Statistics:")
    if 'total_chats' in stats:
        print(f"     • Total interactions: {stats['total_chats']}")
        print(f"     • Average mood: {stats['avg_mood']:.2f}/10")
        print(f"     • Mood range: {stats['min_mood']}/10 - {stats['max_mood']}/10")
        print(f"     • Mood std dev: {stats['mood_std']:.2f}")
        print(f"     • Trend: {stats['trend']}")
        
        print("\n   📈 Mood Distribution:")
        for mood, count in stats['mood_dist'].items():
            bar = "█" * min(count, 20)  # Limit bar length
            percentage = (count / stats['total_chats']) * 100
            print(f"     {mood:2d}/10: {bar:20s} {count:3d} ({percentage:5.1f}%)")
    else:
        print("     No chat data available")
    
    print("\n   📋 Event Statistics:")
    if 'total_events' in stats:
        print(f"     • Total events: {stats['total_events']}")
        if 'event_types' in stats:
            print("     • Event breakdown:")
            for event_type, count in stats['event_types'].items():
                print(f"       - {event_type}: {count}")
    else:
        print("     No event data available")


def main():
    """Main dashboard viewer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='View Therapy Robot dashboard')
    parser.add_argument('--events', action='store_true', help='Show events only')
    parser.add_argument('--chats', action='store_true', help='Show chats only')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    parser.add_argument('--limit', type=int, default=10, help='Number of items to show (default: 10)')
    
    args = parser.parse_args()
    
    # If no specific view requested, show all
    if not (args.events or args.chats or args.stats):
        view_statistics()
        view_chats(args.limit)
        view_events(args.limit)
    else:
        if args.stats:
            view_statistics()
        if args.chats:
            view_chats(args.limit)
        if args.events:
            view_events(args.limit)
    
    print("\n" + "=" * 70)
    print("  Dashboard View Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

