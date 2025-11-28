# utils/system_status.py
"""
System Status Tracker
Tracks hardware, AI, and network status for the dashboard.
"""
import time
from datetime import datetime
from typing import Optional, Dict
import threading

# Module-level status tracking
_app_start_time: Optional[float] = None
_hardware_status: Dict[str, Dict] = {}
_ai_status: Dict[str, any] = {}
_last_status_update: Optional[float] = None
_status_lock = threading.Lock()

# Initialize app start time on module import
_app_start_time = time.time()


def set_app_start_time(timestamp: Optional[float] = None):
    """Set application start time (called from main.py)."""
    global _app_start_time
    with _status_lock:
        _app_start_time = timestamp if timestamp is not None else time.time()


def update_hardware_status(component: str, status: str, last_success: Optional[float] = None, error: Optional[str] = None):
    """
    Update status for a hardware component.
    
    Args:
        component: Component name (e.g., "LED", "Joystick", "Photoresistor", "FallDetector")
        status: Status string ("ok", "error", "unknown")
        last_success: Timestamp of last successful operation (optional)
        error: Error message if status is "error" (optional)
    """
    global _hardware_status
    with _status_lock:
        _hardware_status[component] = {
            "status": status,
            "last_success": last_success or time.time(),
            "error": error,
            "updated_at": time.time()
        }


def update_ai_status(last_success: Optional[float] = None, last_error: Optional[str] = None):
    """
    Update AI/Gemini API status.
    
    Args:
        last_success: Timestamp of last successful API call
        last_error: Error message from last failed call
    """
    global _ai_status
    with _status_lock:
        if last_success is not None:
            _ai_status["last_success"] = last_success
            _ai_status["status"] = "ok"
        if last_error is not None:
            _ai_status["last_error"] = last_error
            _ai_status["last_error_time"] = time.time()
            _ai_status["status"] = "error"
        _ai_status["updated_at"] = time.time()


def get_system_status() -> Dict:
    """
    Get current system status for dashboard.
    
    Returns:
        Dictionary with system status information
    """
    global _app_start_time, _hardware_status, _ai_status, _last_status_update
    import config
    
    with _status_lock:
        uptime_seconds = time.time() - _app_start_time if _app_start_time else 0
        
        # Format uptime
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        # Determine AI status
        ai_status_str = _ai_status.get("status", "unknown")
        if ai_status_str == "ok":
            # Check if last success was recent (within last hour)
            last_success = _ai_status.get("last_success", 0)
            if time.time() - last_success > 3600:
                ai_status_str = "unknown"
        
        # Determine Discord status
        discord_configured = bool(config.DISCORD_WEBHOOK_URL)
        discord_status = "configured" if discord_configured else "not_configured"
        
        # Build hardware status summary
        hardware_summary = {}
        for component, status_info in _hardware_status.items():
            status_str = status_info.get("status", "unknown")
            last_success = status_info.get("last_success", 0)
            # If last success was more than 5 minutes ago, mark as stale
            if status_str == "ok" and (time.time() - last_success) > 300:
                status_str = "stale"
            hardware_summary[component] = {
                "status": status_str,
                "last_success": datetime.fromtimestamp(last_success).isoformat() if last_success else None,
                "error": status_info.get("error")
            }
        
        # Default hardware components if not tracked
        default_components = ["LED", "Joystick", "Photoresistor", "FallDetector", "RotaryEncoder"]
        for comp in default_components:
            if comp not in hardware_summary:
                hardware_summary[comp] = {"status": "unknown", "last_success": None, "error": None}
        
        _last_status_update = time.time()
        
        return {
            "simulation_mode": config.USE_SIMULATION,
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": uptime_str,
            "app_start_time": datetime.fromtimestamp(_app_start_time).isoformat() if _app_start_time else None,
            "hardware": hardware_summary,
            "ai": {
                "status": ai_status_str,
                "last_success": datetime.fromtimestamp(_ai_status["last_success"]).isoformat() if _ai_status.get("last_success") else None,
                "last_error": _ai_status.get("last_error"),
                "last_error_time": datetime.fromtimestamp(_ai_status["last_error_time"]).isoformat() if _ai_status.get("last_error_time") else None
            },
            "discord": {
                "configured": discord_configured,
                "status": discord_status
            },
            "last_update": datetime.fromtimestamp(_last_status_update).isoformat()
        }

