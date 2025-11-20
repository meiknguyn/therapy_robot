# dashboard/dashboard_app.py
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

chat_log = []
event_log = []

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Therapy Assistant Dashboard</title>
  <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <span class="navbar-brand mb-0 h1">Therapy Assistant Dashboard</span>
  </div>
</nav>

<div class="container">

  <h3>Chat Log</h3>
  <table class="table table-striped table-sm">
    <thead>
      <tr>
        <th>Time</th>
        <th>User</th>
        <th>Emotion</th>
        <th>Bot Reply</th>
      </tr>
    </thead>
    <tbody>
      {% for c in chat_log %}
      <tr>
        <td>{{ c.timestamp }}</td>
        <td>{{ c.user_text }}</td>
        <td>{{ c.emotion }}</td>
        <td>{{ c.bot_reply }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <hr />

  <h3>Events (Pomodoro, Meditation, etc.)</h3>
  <table class="table table-bordered table-sm">
    <thead>
      <tr>
        <th>Time</th>
        <th>Event Type</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {% for e in event_log %}
      <tr>
        <td>{{ e.timestamp }}</td>
        <td>{{ e.event_type }}</td>
        <td>{{ e.details }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

</div>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, chat_log=chat_log, event_log=event_log)


@app.route("/api/log_chat", methods=["POST"])
def api_log_chat():
    data = request.get_json() or {}
    chat_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_text": data.get("user_text", ""),
        "emotion": data.get("emotion", ""),
        "bot_reply": data.get("bot_reply", "")
    })
    return jsonify({"status": "ok"})


@app.route("/api/log_event", methods=["POST"])
def api_log_event():
    data = request.get_json() or {}
    event_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": data.get("event_type", "unknown"),
        "details": data.get("details", {})
    })
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Access at http://127.0.0.1:5000/
    app.run(host="0.0.0.0", port=5000, debug=True)
