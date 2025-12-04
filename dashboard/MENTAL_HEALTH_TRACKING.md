# Mental Health Tracking System

## Overview

The dashboard includes comprehensive mental health tracking visualizations that analyze chat interactions to show trends over time. The system converts detected emotions into numeric scores and tracks improvements daily, weekly, monthly, and yearly.

## Features

### 1. Overall Statistics Dashboard

Four key metrics displayed at the top:
- **Overall Score**: Average mental health score across all sessions (1-10 scale)
- **Total Sessions**: Number of chat interactions logged
- **Current Trend**: Whether mental health is "improving", "declining", or "stable"
- **Recent Average**: Average score for the last 7 days

### 2. Interactive Charts

Four time-based views available via tabs:

#### Daily View (30 Days)
- Line chart showing daily average mental health scores
- Helps identify day-to-day patterns and fluctuations

#### Weekly View (12 Weeks)
- Line chart showing weekly averages
- Useful for spotting weekly trends and patterns

#### Monthly View (12 Months)
- Bar chart showing monthly averages
- Good for long-term progress tracking

#### Yearly View (All Years)
- Bar chart showing yearly averages
- Provides the highest-level overview of progress

## Emotion Scoring System

Emotions detected in chat interactions are converted to scores on a 1-10 scale:

### High Scores (7-9) - Positive Emotions
- joy, happy, excited, grateful, calm, peaceful, content, relaxed, satisfied, hopeful

### Neutral (5) - Neutral Emotions
- neutral, normal, okay, fine

### Low Scores (2-4) - Negative Emotions
- sad, depressed, anxious, worried, stressed, frustrated, angry, lonely, overwhelmed, tired, nervous, fearful, disappointed, guilty, ashamed

**Scoring Logic:**
- If emotion is not recognized, default score is 5 (neutral)
- Scores are averaged for each time period
- Higher scores indicate better mental health

## Data Processing

The system:
1. Reads chat data from `logs/chats.csv`
2. Extracts emotion from each chat entry
3. Converts emotion to numeric score (1-10)
4. Groups scores by time period (day/week/month/year)
5. Calculates averages, min, max for each period
6. Serves data via API endpoints for visualization

## API Endpoints

### `/api/mental-health/stats`
Returns overall statistics:
```json
{
  "total_chats": 150,
  "average_score": 6.5,
  "current_trend": "improving",
  "recent_average": 7.2,
  "previous_average": 6.8
}
```

### `/api/mental-health/daily`
Returns daily trends for last 30 days:
```json
{
  "2024-11-28": {
    "average": 7.5,
    "count": 5,
    "min": 6.0,
    "max": 9.0
  },
  ...
}
```

### `/api/mental-health/weekly`
Returns weekly trends for last 12 weeks (format: "YYYY-W##")

### `/api/mental-health/monthly`
Returns monthly trends for last 12 months (format: "YYYY-MM")

### `/api/mental-health/yearly`
Returns yearly trends (format: "YYYY")

## Chart Features

- **Interactive**: Hover to see exact values
- **Color-coded**: Different colors for different time periods
- **Responsive**: Adapts to screen size
- **Auto-refresh**: Updates every 30 seconds
- **Smooth animations**: Chart.js provides smooth transitions

## How It Works

1. **Data Collection**: Every chat interaction with detected emotion is logged to CSV
2. **Analysis**: Mental health analyzer reads CSV and processes data
3. **Visualization**: Chart.js renders interactive charts from processed data
4. **Updates**: Dashboard refreshes every 30 seconds with new data

## Interpretation Guide

### Score Ranges
- **8-10**: Excellent mental health
- **6-7.9**: Good mental health
- **4-5.9**: Moderate mental health
- **1-3.9**: Poor mental health (consider seeking help)

### Trend Analysis
- **Improving**: Recent average is >0.5 points higher than previous period
- **Stable**: Recent average is within ±0.5 points of previous period
- **Declining**: Recent average is >0.5 points lower than previous period

## Technical Details

### Technologies Used
- **Chart.js 4.4.0**: JavaScript charting library
- **Bootstrap 5.3.3**: UI framework
- **Python**: Backend data processing
- **CSV**: Data storage format

### Performance
- Efficient CSV reading with caching
- Charts load on-demand (when tab is clicked)
- Limits to prevent memory issues
- Handles large datasets gracefully

## Future Enhancements

Potential improvements:
- Export charts as images
- Custom date range selection
- Emotion breakdown pie charts
- Correlation with events (e.g., meditation sessions)
- Goal setting and progress tracking
- Trend prediction/forecasting
- Email/SMS alerts for concerning trends

## Troubleshooting

**No data showing?**
- Ensure chat CSV file exists in `logs/` directory
- Check that chats have emotion field populated
- Verify CSV format is correct

**Charts not loading?**
- Check browser console for JavaScript errors
- Ensure Chart.js CDN is accessible
- Verify API endpoints are responding (check Network tab)

**Incorrect scores?**
- Review emotion scoring system in `mental_health_analyzer.py`
- Check that emotions in CSV match expected format
- Verify emotion detection is working correctly

