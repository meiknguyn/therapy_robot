# dashboard/dashboard_app.py
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json

from dashboard.csv_logger import CSVLogger
from dashboard.mental_health_analyzer import MentalHealthAnalyzer

app = Flask(__name__)

chat_log = []
event_log = []

# Initialize CSV logger
csv_logger = CSVLogger(logs_dir="logs")

# Initialize mental health analyzer
health_analyzer = MentalHealthAnalyzer(chats_csv_path="logs/chats.csv")

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Therapy Assistant Dashboard</title>
  <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <meta http-equiv="refresh" content="30">
  <style>
    .badge { font-size: 0.85em; }
    pre { background-color: #f8f9fa; padding: 8px; border-radius: 4px; }
    .table-responsive { max-height: 600px; overflow-y: auto; }
    .chart-container { position: relative; height: 400px; margin-bottom: 20px; }
    .nav-tabs .nav-link.active { background-color: #0d6efd; color: white; }
    .health-stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
  </style>
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <span class="navbar-brand mb-0 h1">Therapy Assistant Dashboard</span>
  </div>
</nav>

<div class="container">

  <h3>Chat Log</h3>
  <div class="table-responsive">
    <table class="table table-striped table-hover table-sm">
      <thead class="table-dark">
        <tr>
          <th>Time</th>
          <th>User Message</th>
          <th>Emotion</th>
          <th>Bot Reply</th>
        </tr>
      </thead>
      <tbody>
        {% for c in chat_log|reverse %}
        <tr>
          <td><small>{{ c.timestamp }}</small></td>
          <td>{{ c.user_text }}</td>
          <td><span class="badge bg-info">{{ c.emotion }}</span></td>
          <td>{{ c.bot_reply }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <hr />

  <h2>📊 Mental Health Tracking</h2>
  
  <div class="row mb-4">
    <div class="col-md-3">
      <div class="health-stat-card">
        <h5>Overall Score</h5>
        <h2 id="overall-score">--</h2>
        <small>/10</small>
      </div>
    </div>
    <div class="col-md-3">
      <div class="health-stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h5>Total Sessions</h5>
        <h2 id="total-sessions">--</h2>
      </div>
    </div>
    <div class="col-md-3">
      <div class="health-stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h5>Current Trend</h5>
        <h4 id="current-trend">--</h4>
      </div>
    </div>
    <div class="col-md-3">
      <div class="health-stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <h5>Recent Average</h5>
        <h2 id="recent-average">--</h2>
        <small>/10</small>
      </div>
    </div>
  </div>

  <div class="row mb-4">
    <div class="col-12">
      <div class="card shadow-sm">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">📝 Today's Therapy Summary</h4>
        </div>
        <div class="card-body">
          <div id="daily-summary-content">
            <p class="text-muted">Loading summary...</p>
          </div>
          <div class="mt-2">
            <small class="text-muted">Last updated: <span id="daily-summary-date">--</span></small>
          </div>
        </div>
      </div>
    </div>
  </div>

  <ul class="nav nav-tabs mb-3" id="timePeriodTabs" role="tablist">
    <li class="nav-item" role="presentation">
      <button class="nav-link active" id="daily-tab" data-bs-toggle="tab" data-bs-target="#daily" type="button" role="tab">Daily (30 days)</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="weekly-tab" data-bs-toggle="tab" data-bs-target="#weekly" type="button" role="tab">Weekly (12 weeks)</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="monthly-tab" data-bs-toggle="tab" data-bs-target="#monthly" type="button" role="tab">Monthly (12 months)</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="yearly-tab" data-bs-toggle="tab" data-bs-target="#yearly" type="button" role="tab">Yearly</button>
    </li>
  </ul>

  <div class="tab-content" id="timePeriodContent">
    <div class="tab-pane fade show active" id="daily" role="tabpanel">
      <div class="chart-container">
        <canvas id="dailyChart"></canvas>
      </div>
    </div>
    <div class="tab-pane fade" id="weekly" role="tabpanel">
      <div class="chart-container">
        <canvas id="weeklyChart"></canvas>
      </div>
    </div>
    <div class="tab-pane fade" id="monthly" role="tabpanel">
      <div class="chart-container">
        <canvas id="monthlyChart"></canvas>
      </div>
    </div>
    <div class="tab-pane fade" id="yearly" role="tabpanel">
      <div class="chart-container">
        <canvas id="yearlyChart"></canvas>
      </div>
    </div>
  </div>

  <hr />

  <h3>Events Log</h3>
  <div class="alert alert-info d-flex justify-content-between align-items-center">
    <div>
      <strong>Total Events:</strong> {{ event_log|length }} | 
      <strong>Total Chats:</strong> {{ chat_log|length }}
      <br>
      <small>All events are automatically logged to CSV files in the logs/ directory. Page auto-refreshes every 5 seconds.</small>
    </div>
    <div>
      <a href="/api/download/events.csv" class="btn btn-sm btn-primary">Download Events CSV</a>
      <a href="/api/download/chats.csv" class="btn btn-sm btn-primary">Download Chats CSV</a>
    </div>
  </div>
  <div class="table-responsive">
    <table class="table table-striped table-hover table-sm">
      <thead class="table-dark">
        <tr>
          <th>Time</th>
          <th>Event Type</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        {% for e in event_log|reverse %}
        <tr>
          <td><small>{{ e.timestamp }}</small></td>
          <td>
            <span class="badge bg-primary">{{ e.event_type }}</span>
          </td>
          <td>
            <pre class="mb-0" style="font-size: 0.85em; max-width: 600px; white-space: pre-wrap;">{{ e.details_formatted }}</pre>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
let dailyChart, weeklyChart, monthlyChart, yearlyChart;

// Load overall stats
async function loadStats() {
  try {
    const response = await fetch('/api/mental-health/stats');
    const stats = await response.json();
    
    document.getElementById('overall-score').textContent = stats.average_score.toFixed(1);
    document.getElementById('total-sessions').textContent = stats.total_chats;
    document.getElementById('current-trend').textContent = stats.current_trend.charAt(0).toUpperCase() + stats.current_trend.slice(1);
    document.getElementById('recent-average').textContent = stats.recent_average.toFixed(1);
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load and render daily chart
async function loadDailyChart() {
  try {
    const response = await fetch('/api/mental-health/daily');
    const data = await response.json();
    
    const labels = Object.keys(data);
    const averages = labels.map(date => data[date].average);
    
    const ctx = document.getElementById('dailyChart').getContext('2d');
    
    if (dailyChart) dailyChart.destroy();
    
    dailyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Mental Health Score',
          data: averages,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 10,
            title: {
              display: true,
              text: 'Mental Health Score (1-10)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Daily Mental Health Trends (Last 30 Days)'
          },
          legend: {
            display: true
          }
        }
      }
    });
  } catch (error) {
    console.error('Error loading daily chart:', error);
  }
}

// Load and render weekly chart
async function loadWeeklyChart() {
  try {
    const response = await fetch('/api/mental-health/weekly');
    const data = await response.json();
    
    const labels = Object.keys(data);
    const averages = labels.map(week => data[week].average);
    
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    
    if (weeklyChart) weeklyChart.destroy();
    
    weeklyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Mental Health Score',
          data: averages,
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 10,
            title: {
              display: true,
              text: 'Mental Health Score (1-10)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Week'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Weekly Mental Health Trends (Last 12 Weeks)'
          }
        }
      }
    });
  } catch (error) {
    console.error('Error loading weekly chart:', error);
  }
}

// Load and render monthly chart
async function loadMonthlyChart() {
  try {
    const response = await fetch('/api/mental-health/monthly');
    const data = await response.json();
    
    const labels = Object.keys(data);
    const averages = labels.map(month => data[month].average);
    
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) monthlyChart.destroy();
    
    monthlyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Mental Health Score',
          data: averages,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgb(255, 99, 132)',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 10,
            title: {
              display: true,
              text: 'Mental Health Score (1-10)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Month'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Monthly Mental Health Trends (Last 12 Months)'
          }
        }
      }
    });
  } catch (error) {
    console.error('Error loading monthly chart:', error);
  }
}

// Load and render yearly chart
async function loadYearlyChart() {
  try {
    const response = await fetch('/api/mental-health/yearly');
    const data = await response.json();
    
    const labels = Object.keys(data);
    const averages = labels.map(year => data[year].average);
    
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    
    if (yearlyChart) yearlyChart.destroy();
    
    yearlyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Mental Health Score',
          data: averages,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgb(54, 162, 235)',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 10,
            title: {
              display: true,
              text: 'Mental Health Score (1-10)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Year'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Yearly Mental Health Trends'
          }
        }
      }
    });
  } catch (error) {
    console.error('Error loading yearly chart:', error);
  }
}

// Load daily summary
async function loadDailySummary() {
  try {
    const response = await fetch('/api/mental-health/daily-summary');
    const data = await response.json();
    
    const summaryDiv = document.getElementById('daily-summary-content');
    const dateSpan = document.getElementById('daily-summary-date');
    
    if (data.summary) {
      summaryDiv.innerHTML = `<p style="font-size: 1.1em; line-height: 1.6;">${data.summary.replace(/\n/g, '<br>')}</p>`;
      dateSpan.textContent = data.date || new Date().toISOString().split('T')[0];
    } else {
      summaryDiv.innerHTML = '<p class="text-muted">No summary available yet.</p>';
    }
  } catch (error) {
    console.error('Error loading daily summary:', error);
    document.getElementById('daily-summary-content').innerHTML = 
      '<p class="text-muted">Unable to load summary. Please try again later.</p>';
  }
}

// Load all data on page load
window.addEventListener('DOMContentLoaded', function() {
  loadStats();
  loadDailyChart();
  loadDailySummary();
  
  // Load other charts when tabs are clicked
  document.getElementById('weekly-tab').addEventListener('shown.bs.tab', loadWeeklyChart);
  document.getElementById('monthly-tab').addEventListener('shown.bs.tab', loadMonthlyChart);
  document.getElementById('yearly-tab').addEventListener('shown.bs.tab', loadYearlyChart);
  
  // Refresh stats and summary every 30 seconds
  setInterval(loadStats, 30000);
  setInterval(loadDailySummary, 30000);
});
</script>

</body>
</html>
"""


@app.route("/")
def index():
    # Format event details for display
    formatted_event_log = []
    for e in event_log:
        formatted_event = dict(e)
        # Format details as readable JSON
        try:
            if isinstance(e.get("details"), dict):
                formatted_event["details_formatted"] = json.dumps(e["details"], indent=2, ensure_ascii=False)
            else:
                formatted_event["details_formatted"] = str(e.get("details", ""))
        except:
            formatted_event["details_formatted"] = str(e.get("details", ""))
        formatted_event_log.append(formatted_event)
    
    return render_template_string(PAGE, chat_log=chat_log, event_log=formatted_event_log)


@app.route("/api/log_chat", methods=["POST"])
def api_log_chat():
    data = request.get_json() or {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    chat_entry = {
        "timestamp": timestamp,
        "user_text": data.get("user_text", ""),
        "emotion": data.get("emotion", ""),
        "bot_reply": data.get("bot_reply", "")
    }
    
    chat_log.append(chat_entry)
    
    # Log to CSV
    csv_logger.log_chat(
        user_text=chat_entry["user_text"],
        emotion=chat_entry["emotion"],
        bot_reply=chat_entry["bot_reply"],
        timestamp=timestamp
    )
    
    return jsonify({"status": "ok"})


@app.route("/api/log_event", methods=["POST"])
def api_log_event():
    data = request.get_json() or {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_type = data.get("event_type", "unknown")
    details = data.get("details", {})
    
    event_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "details": details
    }
    
    event_log.append(event_entry)
    
    # Log to CSV
    csv_logger.log_event(
        event_type=event_type,
        details=details,
        timestamp=timestamp
    )
    
    # Keep only last 1000 events in memory (to prevent memory issues)
    if len(event_log) > 1000:
        event_log.pop(0)
    
    return jsonify({"status": "ok"})


@app.route("/api/download/<filename>")
def download_csv(filename):
    """Download CSV log files."""
    from flask import send_file, abort
    import os
    
    csv_path = os.path.join(csv_logger.logs_dir, filename)
    
    if os.path.exists(csv_path) and filename in ["events.csv", "chats.csv"]:
        return send_file(csv_path, as_attachment=True, download_name=filename)
    else:
        abort(404)


@app.route("/api/stats")
def api_stats():
    """Get statistics about logged events and chats."""
    return jsonify({
        "total_events": len(event_log),
        "total_chats": len(chat_log),
        "csv_events_count": csv_logger.get_events_count(),
        "csv_chats_count": csv_logger.get_chats_count()
    })


@app.route("/api/mental-health/stats")
def api_mental_health_stats():
    """Get overall mental health statistics."""
    stats = health_analyzer.get_overall_stats()
    return jsonify(stats)


@app.route("/api/mental-health/daily")
def api_mental_health_daily():
    """Get daily mental health trends."""
    trends = health_analyzer.get_daily_trends(days=30)
    return jsonify(trends)


@app.route("/api/mental-health/weekly")
def api_mental_health_weekly():
    """Get weekly mental health trends."""
    trends = health_analyzer.get_weekly_trends(weeks=12)
    return jsonify(trends)


@app.route("/api/mental-health/monthly")
def api_mental_health_monthly():
    """Get monthly mental health trends."""
    trends = health_analyzer.get_monthly_trends(months=12)
    return jsonify(trends)


@app.route("/api/mental-health/yearly")
def api_mental_health_yearly():
    """Get yearly mental health trends."""
    trends = health_analyzer.get_yearly_trends()
    return jsonify(trends)


@app.route("/api/mental-health/daily-summary")
def api_mental_health_daily_summary():
    """Get AI-generated daily therapy summary."""
    try:
        # Get today's context
        context = health_analyzer.get_daily_summary_context()
        
        # Generate summary using AI
        try:
            from ai.gemini_client import generate_daily_summary
            summary_text = generate_daily_summary(context)
        except Exception as e:
            print(f"[Dashboard] Error generating AI summary: {e}")
            # Fallback summary
            if context.get("has_data"):
                summary_text = (
                    f"Today you had {context.get('session_count', 0)} therapy session(s). "
                    "Your emotional well-being matters, and checking in with yourself is a positive step. "
                    "Remember to be gentle with yourself."
                )
            else:
                summary_text = "No sessions logged today. Remember, I'm here whenever you need to chat."
        
        # Get trend
        trend = health_analyzer.compute_trend_for_period(days=7)
        
        return jsonify({
            "summary": summary_text,
            "date": context.get("date", datetime.now().date().isoformat()),
            "trend": trend,
            "session_count": context.get("session_count", 0),
            "average_score": context.get("average_score", 5.0),
            "has_data": context.get("has_data", False)
        })
    except Exception as e:
        print(f"[Dashboard] Error in daily summary endpoint: {e}")
        # Return safe fallback
        return jsonify({
            "summary": "Unable to generate summary at this time. Please try again later.",
            "date": datetime.now().date().isoformat(),
            "trend": "stable",
            "session_count": 0,
            "average_score": 5.0,
            "has_data": False,
            "error": str(e)
        }), 200  # Return 200 so UI can still render


if __name__ == "__main__":
    # Access at http://127.0.0.1:5000/
    print("[Dashboard] CSV logging enabled. Logs will be saved to:", csv_logger.logs_dir)
    print("[Dashboard] Starting dashboard server at http://127.0.0.1:5000/")
    app.run(host="0.0.0.0", port=5000, debug=True)
