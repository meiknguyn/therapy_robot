#!/usr/bin/env python3
"""Flask web dashboard for Therapy Robot."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template_string, jsonify, request
import pandas as pd
from datetime import datetime
from therapy_robot import config
from therapy_robot.ai import gemini_client
from therapy_robot.audio import speaker
from therapy_robot.dashboard import csv_logger
from therapy_robot.dashboard.mental_health_analyzer import compute_basic_stats

app = Flask(__name__)

# HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Therapy Robot Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #333; 
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
            gap: 20px; 
            margin: 30px 0; 
        }
        .stat-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px; 
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            margin-bottom: 5px;
        }
        .stat-label { 
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .section {
            margin: 40px 0;
        }
        .section h2 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td { 
            padding: 15px; 
            text-align: left; 
            border-bottom: 1px solid #e0e0e0; 
        }
        th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }
        tr:hover { 
            background-color: #f5f5f5; 
        }
        .mood-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .mood-low { background: #ffcdd2; color: #c62828; }
        .mood-mid { background: #fff9c4; color: #f57f17; }
        .mood-high { background: #c8e6c9; color: #2e7d32; }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        .auto-refresh {
            display: inline-block;
            margin-left: 10px;
            font-size: 0.9em;
            color: #666;
        }
        .auto-refresh.active {
            color: #667eea;
        }
        .last-update {
            text-align: right;
            color: #999;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 30px 0;
            display: flex;
            flex-direction: column;
            height: 500px;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f9f9f9;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .chat-message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .chat-message.robot {
            background: #e0e0e0;
            color: #333;
            margin-right: auto;
        }
        .chat-message-header {
            font-size: 0.85em;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        .chat-input-container {
            display: flex;
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
            font-family: inherit;
        }
        .chat-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .chat-send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        .chat-send-btn:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a3d8f 100%);
        }
        .chat-send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .mood-indicator {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }
        .mood-low { background: #ffcdd2; color: #c62828; }
        .mood-mid { background: #fff9c4; color: #f57f17; }
        .mood-high { background: #c8e6c9; color: #2e7d32; }
    </style>
    <script>
        let autoRefreshInterval;
        let lastUpdateTime = new Date();
        
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    // Update stat cards
                    document.querySelector('.stat-card:nth-child(1) .stat-value').textContent = data.total_sessions;
                    document.querySelector('.stat-card:nth-child(2) .stat-value').textContent = data.avg_mood ? data.avg_mood.toFixed(2) + '/10' : '0.00/10';
                    
                    // Update trend
                    const trendEmoji = data.trend === 'improving' ? '📈' : data.trend === 'declining' ? '📉' : '➡️';
                    document.querySelector('.stat-card:nth-child(3) .stat-value').textContent = trendEmoji + ' ' + data.trend.charAt(0).toUpperCase() + data.trend.slice(1);
                    
                    // Update last update time
                    lastUpdateTime = new Date();
                    const updateEl = document.getElementById('last-update');
                    if (updateEl) {
                        updateEl.textContent = 'Last updated: ' + lastUpdateTime.toLocaleTimeString();
                    }
                })
                .catch(error => console.error('Error fetching stats:', error));
        }
        
        function reloadPage() {
            location.reload();
        }
        
        function toggleAutoRefresh() {
            const btn = document.getElementById('auto-refresh-btn');
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                btn.textContent = '▶️ Enable Auto-Refresh';
                btn.classList.remove('active');
            } else {
                autoRefreshInterval = setInterval(reloadPage, 5000); // Refresh every 5 seconds
                btn.textContent = '⏸️ Auto-Refresh ON (5s)';
                btn.classList.add('active');
            }
        }
        
        // Volume control functions
        function updateVolume(volume) {
            const volumePercent = Math.round(volume * 100);
            document.getElementById('volume-value').textContent = volumePercent + '%';
            document.getElementById('volume-bar-fill').style.width = volumePercent + '%';
            document.getElementById('volume-slider').value = volume;
        }
        
        function setVolume(volume) {
            console.log('Setting volume to:', volume);
            fetch('/api/volume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ volume: volume })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Volume response:', data);
                if (data.success) {
                    updateVolume(data.volume);
                } else {
                    console.error('Volume set failed:', data.error);
                    alert('Failed to set volume: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error setting volume:', error);
                alert('Error setting volume: ' + error.message);
            });
        }
        
        function onVolumeSliderChange() {
            const slider = document.getElementById('volume-slider');
            const volume = parseFloat(slider.value);
            setVolume(volume);
        }
        
        function loadCurrentVolume() {
            fetch('/api/volume')
                .then(response => response.json())
                .then(data => {
                    if (data.volume !== undefined) {
                        updateVolume(data.volume);
                    }
                })
                .catch(error => console.error('Error loading volume:', error));
        }
        
        // Load current volume on page load
        window.addEventListener('load', () => {
            loadCurrentVolume();
            loadChatHistory();
        });
        
        // Chat functions
        function addChatMessage(userText, botReply, moodScore) {
            const messagesDiv = document.getElementById('chat-messages');
            
            // User message
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-message user';
            userMsg.innerHTML = `
                <div class="chat-message-header">You</div>
                <div>${escapeHtml(userText)}</div>
            `;
            messagesDiv.appendChild(userMsg);
            
            // Robot message
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message robot';
            const moodClass = moodScore <= 3 ? 'mood-low' : moodScore <= 6 ? 'mood-mid' : 'mood-high';
            botMsg.innerHTML = `
                <div class="chat-message-header">
                    Robot 
                    <span class="mood-indicator ${moodClass}">Mood: ${moodScore}/10</span>
                </div>
                <div>${escapeHtml(botReply)}</div>
            `;
            messagesDiv.appendChild(botMsg);
            
            // Scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const sendBtn = document.getElementById('chat-send-btn');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Disable input while processing
            input.disabled = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            // Show user message immediately
            const messagesDiv = document.getElementById('chat-messages');
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-message user';
            userMsg.innerHTML = `
                <div class="chat-message-header">You</div>
                <div>${escapeHtml(message)}</div>
            `;
            messagesDiv.appendChild(userMsg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Clear input
            input.value = '';
            
            // Send to server
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addChatMessage(message, data.reply, data.mood_score);
                } else {
                    alert('Error: ' + (data.error || 'Failed to get response'));
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
                alert('Error sending message: ' + error.message);
            })
            .finally(() => {
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.focus();
            });
        }
        
        function loadChatHistory() {
            fetch('/api/chats')
                .then(response => response.json())
                .then(chats => {
                    const messagesDiv = document.getElementById('chat-messages');
                    messagesDiv.innerHTML = '';
                    
                    // Show last 10 chats
                    chats.slice(-10).forEach(chat => {
                        addChatMessage(chat.user_text, chat.bot_reply, chat.emotion_score);
                    });
                })
                .catch(error => console.error('Error loading chat history:', error));
        }
        
        // Allow Enter key to send message
        document.addEventListener('DOMContentLoaded', () => {
            const input = document.getElementById('chat-input');
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                    }
                });
            }
        });
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Therapy Robot Dashboard</h1>
        <div class="subtitle">Real-time monitoring of therapy sessions and mental health metrics</div>
        
        <div style="margin-bottom: 20px;">
            <button class="refresh-btn" onclick="reloadPage()">🔄 Refresh Now</button>
            <button class="refresh-btn" id="auto-refresh-btn" onclick="toggleAutoRefresh()" style="margin-left: 10px;">▶️ Enable Auto-Refresh</button>
            <span class="auto-refresh" id="last-update">Last updated: {{ current_time }}</span>
        </div>
        
        <div class="volume-control">
            <h3>🔊 Volume Control</h3>
            <div class="volume-slider-container">
                <span style="font-size: 1.2em;">🔇</span>
                <input type="range" id="volume-slider" class="volume-slider" 
                       min="0" max="1" step="0.01" value="0.6" 
                       oninput="onVolumeSliderChange()" onchange="onVolumeSliderChange()">
                <span style="font-size: 1.2em;">🔊</span>
                <span id="volume-value" class="volume-value">60%</span>
                <div class="volume-bar">
                    <div id="volume-bar-fill" class="volume-bar-fill" style="width: 60%;"></div>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ total_chats }}</div>
                <div class="stat-label">Total Interactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ avg_mood }}/10</div>
                <div class="stat-label">Average Mood</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ trend_emoji }} {{ trend }}</div>
                <div class="stat-label">Mood Trend</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ total_events }}</div>
                <div class="stat-label">Total Events</div>
            </div>
        </div>
        
        <div class="section">
            <h2>💬 Chat with Therapy Robot</h2>
            <div class="chat-container">
                <div id="chat-messages" class="chat-messages">
                    <!-- Chat messages will be loaded here -->
                </div>
                <div class="chat-input-container">
                    <input type="text" id="chat-input" class="chat-input" 
                           placeholder="Type your message here... (Press Enter to send)" 
                           autocomplete="off">
                    <button id="chat-send-btn" class="chat-send-btn" onclick="sendChatMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Chat Interactions</h2>
            {% if recent_chats %}
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>User Message</th>
                    <th>Mood</th>
                    <th>Bot Response</th>
                </tr>
                {% for chat in recent_chats %}
                <tr>
                    <td>{{ chat.timestamp[:19].replace('T', ' ') }}</td>
                    <td><strong>{{ chat.user_text }}</strong></td>
                    <td>
                        <span class="mood-badge {% if chat.emotion_score <= 3 %}mood-low{% elif chat.emotion_score <= 6 %}mood-mid{% else %}mood-high{% endif %}">
                            {{ chat.emotion_score }}/10
                        </span>
                    </td>
                    <td>{{ chat.bot_reply[:80] }}{% if chat.bot_reply|length > 80 %}...{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <div class="empty-state">No chat interactions logged yet. Start a therapy session to see data here.</div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>📋 Recent Events</h2>
            {% if recent_events %}
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Event Type</th>
                    <th>Details</th>
                </tr>
                {% for event in recent_events %}
                <tr>
                    <td>{{ event.timestamp[:19].replace('T', ' ') }}</td>
                    <td><strong>{{ event.event_type }}</strong></td>
                    <td>{{ event.details[:100] }}{% if event.details|length > 100 %}...{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <div class="empty-state">No events logged yet.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


def get_mood_emoji(trend):
    """Get emoji for mood trend."""
    if "improving" in trend.lower():
        return "📈"
    elif "declining" in trend.lower():
        return "📉"
    else:
        return "➡️"


@app.route('/')
def dashboard():
    """Main dashboard page."""
    stats = compute_basic_stats()
    
    # Load chat data
    recent_chats = []
    avg_mood = 0.0
    if config.CHAT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            if len(df) > 0:
                avg_mood = float(df['emotion_score'].mean())
                recent_chats = df.tail(10).to_dict('records')
        except Exception as e:
            print(f"Error loading chats: {e}")
    
    # Load event data
    recent_events = []
    total_events = 0
    if config.EVENT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.EVENT_LOG_PATH)
            total_events = len(df)
            recent_events = df.tail(10).to_dict('records')
        except Exception as e:
            print(f"Error loading events: {e}")
    
    trend_emoji = get_mood_emoji(stats['trend'])
    current_time = datetime.now().strftime('%H:%M:%S')
    
    return render_template_string(
        DASHBOARD_HTML,
        total_chats=stats['total_sessions'],
        avg_mood=f"{avg_mood:.2f}" if avg_mood > 0 else "0.00",
        trend=stats['trend'].title(),
        trend_emoji=trend_emoji,
        total_events=total_events,
        recent_chats=recent_chats,
        recent_events=recent_events,
        current_time=current_time
    )


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics (JSON)."""
    stats = compute_basic_stats()
    
    # Add additional stats from CSV
    if config.CHAT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            if len(df) > 0:
                stats['avg_mood'] = float(df['emotion_score'].mean())
                stats['min_mood'] = int(df['emotion_score'].min())
                stats['max_mood'] = int(df['emotion_score'].max())
        except:
            pass
    
    # Add timestamp
    stats['last_update'] = datetime.now().isoformat()
    
    return jsonify(stats)


@app.route('/api/chats')
def api_chats():
    """API endpoint for recent chats (JSON)."""
    recent_chats = []
    if config.CHAT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.CHAT_LOG_PATH)
            recent_chats = df.tail(10).to_dict('records')
        except:
            pass
    return jsonify(recent_chats)


@app.route('/api/events')
def api_events():
    """API endpoint for recent events (JSON)."""
    recent_events = []
    if config.EVENT_LOG_PATH.exists():
        try:
            df = pd.read_csv(config.EVENT_LOG_PATH)
            recent_events = df.tail(10).to_dict('records')
        except:
            pass
    return jsonify(recent_events)


@app.route('/api/volume', methods=['GET'])
def api_volume_get():
    """API endpoint to get current volume."""
    # Read current volume from file or use default
    volume_file = config.LOG_DIR / "volume.txt"
    current_volume = 0.6  # Default
    
    if volume_file.exists():
        try:
            with open(volume_file, 'r') as f:
                current_volume = float(f.read().strip())
        except:
            pass
    
    return jsonify({"volume": current_volume})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint to send a chat message and get a response."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_text = data.get('message', '').strip()
        if not user_text:
            return jsonify({"success": False, "error": "Message is empty"}), 400
        
        user_text_lower = user_text.lower()
        
        # Check for "stop the music" command
        stop_music_phrases = [
            "stop the music",
            "stop music",
            "turn off the music",
            "turn off music",
            "pause the music",
            "pause music",
            "stop playing music",
            "stop the song"
        ]
        
        if any(phrase in user_text_lower for phrase in stop_music_phrases):
            # Stop any currently playing music
            speaker.stop_music()
            csv_logger.log_event("music_stopped", {"source": "dashboard_command", "command": user_text})
            
            return jsonify({
                "success": True,
                "reply": "🔇 Music stopped. Is there anything else I can help you with?",
                "mood_score": 5  # Neutral mood for command
            })
        
        # Check for "play my favorite song" command
        favorite_song_phrases = [
            "play my favorite song",
            "let's play my favorite song",
            "lets play my favorite song",
            "play favorite song",
            "my favorite song"
        ]
        
        if any(phrase in user_text_lower for phrase in favorite_song_phrases):
            favorite_song = "myfavsong.wav"
            favorite_song_path = config.MUSIC_DIR / favorite_song
            
            if favorite_song_path.exists():
                # Stop any currently playing music first
                speaker.stop_music()
                
                # Play the favorite song
                speaker.play_music(favorite_song, loop=True, volume=0.6)
                csv_logger.log_event("favorite_song_played", {"song": favorite_song, "source": "dashboard"})
                
                return jsonify({
                    "success": True,
                    "reply": f"🎵 Playing your favorite song: {favorite_song}",
                    "mood_score": 7  # Happy mood for music
                })
            else:
                return jsonify({
                    "success": True,
                    "reply": f"⚠️ Sorry, I couldn't find '{favorite_song}' in the music directory.",
                    "mood_score": 5
                })
        
        # Check for Pomodoro study session commands
        pomodoro_start_phrases = [
            "i need to focus studying",
            "i need to focus",
            "lets focus",
            "let's focus",
            "start studying",
            "start study session",
            "start pomodoro",
            "begin studying",
            "begin study session"
        ]
        
        if any(phrase in user_text_lower for phrase in pomodoro_start_phrases):
            # Note: Pomodoro requires LED controller which is only available in main.py
            # For now, return a message directing user to terminal
            csv_logger.log_event("pomodoro_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "🍅 To start a Pomodoro study session, please use the terminal interface. The LED will breathe during study time and flash during rest breaks!",
                "mood_score": 6  # Slightly positive mood
            })
        
        # Check for Pomodoro stop commands
        pomodoro_stop_phrases = [
            "stop studying",
            "stop study session",
            "stop pomodoro",
            "end studying",
            "end study session",
            "finish studying"
        ]
        
        if any(phrase in user_text_lower for phrase in pomodoro_stop_phrases):
            csv_logger.log_event("pomodoro_stop_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "🍅 To stop a Pomodoro session, please use the terminal interface where it was started.",
                "mood_score": 5
            })
        
        # Check for Breathing Exercise commands
        breathing_start_phrases = [
            "lets do breathing exercise",
            "let's do breathing exercise",
            "breathing exercise",
            "start breathing exercise",
            "begin breathing exercise",
            "lets breathe",
            "let's breathe",
            "breathing session",
            "start breathing",
            "do breathing"
        ]
        
        if any(phrase in user_text_lower for phrase in breathing_start_phrases):
            csv_logger.log_event("breathing_exercise_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "🧘 To start a breathing exercise session, please use the terminal interface. The LED will guide you: bright for inhale, breathing for hold, rapid flash for exhale!",
                "mood_score": 6
            })
        
        # Check for Breathing Exercise stop commands
        breathing_stop_phrases = [
            "stop breathing exercise",
            "stop breathing",
            "end breathing exercise",
            "end breathing",
            "finish breathing exercise",
            "finish breathing"
        ]
        
        if any(phrase in user_text_lower for phrase in breathing_stop_phrases):
            csv_logger.log_event("breathing_exercise_stop_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "🧘 To stop a breathing exercise session, please use the terminal interface where it was started.",
                "mood_score": 5
            })
        
        # Check for Alarm commands
        alarm_phrases = [
            "set alarm",
            "wake me up",
            "alarm",
            "set alarm at",
            "wake me up in",
            "alarm in"
        ]
        
        if any(phrase in user_text_lower for phrase in alarm_phrases):
            csv_logger.log_event("alarm_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "⏰ To set an alarm, please use the terminal interface. Examples: 'set alarm at 14:30', 'wake me up in 30 minutes', 'alarm in 5 minutes'",
                "mood_score": 5
            })
        
        # Check for Alarm cancel commands
        alarm_cancel_phrases = [
            "cancel alarm",
            "stop alarm",
            "turn off alarm",
            "disable alarm"
        ]
        
        if any(phrase in user_text_lower for phrase in alarm_cancel_phrases):
            csv_logger.log_event("alarm_cancel_requested", {"source": "dashboard", "command": user_text})
            return jsonify({
                "success": True,
                "reply": "⏰ To cancel an alarm, please use the terminal interface where it was set.",
                "mood_score": 5
            })
        
        # Analyze emotion
        emo = gemini_client.analyze_emotion_with_cache(user_text)
        mood_score = emo["score"]
        
        # Get support reply from Gemini
        reply = gemini_client.get_support_reply(mood_score, user_text)
        
        # Log chat interaction
        csv_logger.log_chat(user_text, mood_score, reply)
        
        return jsonify({
            "success": True,
            "reply": reply,
            "mood_score": mood_score
        })
    except Exception as e:
        print(f"[Dashboard] Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/volume', methods=['POST'])
def api_volume_set():
    """API endpoint to set volume."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        volume = float(data.get('volume', 0.6))
        
        # Clamp volume to valid range
        volume = max(0.0, min(1.0, volume))
        
        # Set volume in pygame
        speaker.set_volume(volume)
        
        # Save volume to file for main program to read
        volume_file = config.LOG_DIR / "volume.txt"
        try:
            with open(volume_file, 'w') as f:
                f.write(str(volume))
            print(f"[Dashboard] Volume set to {volume:.2f} ({int(volume*100)}%)")
        except Exception as e:
            print(f"[Dashboard] Error writing volume file: {e}")
            return jsonify({"success": False, "error": f"Failed to save volume: {e}"}), 500
        
        # Log the event
        try:
            csv_logger.log_event(
                "volume_adjusted",
                {
                    "volume": round(volume, 2),
                    "source": "dashboard"
                }
            )
        except:
            pass  # Don't fail if logging fails
        
        return jsonify({"success": True, "volume": volume})
    except Exception as e:
        print(f"[Dashboard] Error setting volume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Therapy Robot Web Dashboard...")
    print("=" * 60)
    print("\n🌐 Dashboard available at:")
    print("   Local:    http://localhost:5000")
    print("   Network:  http://0.0.0.0:5000")
    print("\n📊 API endpoint:")
    print("   http://localhost:5000/api/stats")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

