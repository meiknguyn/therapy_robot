# utils/error_handler.py
"""
Centralized error handling utilities for robust error recovery.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

# Setup logging
logger = logging.getLogger(__name__)

# Global error log callback (set by main.py or dashboard)
_error_log_callback: Optional[Callable[[str, dict], None]] = None


def set_error_log_callback(callback: Callable[[str, dict], None]):
    """Set global callback for logging errors."""
    global _error_log_callback
    _error_log_callback = callback


def log_hardware_error(module_name: str, operation: str, error: Exception, context: dict = None):
    """
    Log hardware errors with context.
    
    Args:
        module_name: Name of the hardware module (e.g., "LED", "Joystick")
        operation: Operation that failed (e.g., "read_adc", "set_brightness")
        error: Exception that occurred
        context: Additional context dictionary
    """
    error_details = {
        "module": module_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        error_details.update(context)
    
    error_msg = f"[{module_name}] Hardware error during {operation}: {error}"
    logger.error(error_msg, exc_info=True)
    print(error_msg)
    
    # Log via callback if available
    if _error_log_callback:
        try:
            _error_log_callback("hardware_error", error_details)
        except Exception as e:
            logger.error(f"Failed to log error via callback: {e}")


def log_network_error(module_name: str, operation: str, error: Exception, context: dict = None):
    """
    Log network/API errors with context.
    
    Args:
        module_name: Name of the module (e.g., "Gemini", "Discord")
        operation: Operation that failed (e.g., "analyze_emotion", "send_alert")
        error: Exception that occurred
        context: Additional context dictionary
    """
    error_details = {
        "module": module_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        error_details.update(context)
    
    error_msg = f"[{module_name}] Network/API error during {operation}: {error}"
    logger.warning(error_msg)
    print(error_msg)
    
    # Log via callback if available
    if _error_log_callback:
        try:
            _error_log_callback("network_error", error_details)
        except Exception as e:
            logger.error(f"Failed to log error via callback: {e}")


def safe_hardware_operation(module_name: str, operation_name: str, default_value=None, 
                           log_callback=None, context: dict = None):
    """
    Decorator/context manager for safe hardware operations with error recovery.
    
    Usage:
        @safe_hardware_operation("LED", "set_brightness", default_value=None)
        def set_brightness(value):
            self.led.value = value
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_hardware_error(module_name, operation_name, e, context)
                return default_value
        return wrapper
    return decorator


def safe_network_operation(module_name: str, operation_name: str, default_value=None,
                          log_callback=None, context: dict = None):
    """
    Decorator/context manager for safe network/API operations with error recovery.
    
    Usage:
        @safe_network_operation("Gemini", "analyze_emotion", default_value="neutral")
        def analyze_emotion(text):
            # API call
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_network_error(module_name, operation_name, e, context)
                return default_value
        return wrapper
    return decorator


def thread_safe_loop(thread_name: str, loop_func: Callable, error_delay: float = 1.0,
                    log_callback=None):
    """
    Wrapper for background thread loops with top-level error handling.
    
    Args:
        thread_name: Name of the thread for logging
        loop_func: Function to call in the loop
        error_delay: Delay in seconds before retrying after error
        log_callback: Optional callback for logging
    """
    import time
    
    while True:
        try:
            loop_func()
        except Exception as e:
            error_msg = f"[{thread_name}] Thread error: {e}"
            logger.error(error_msg, exc_info=True)
            print(error_msg)
            
            if log_callback:
                try:
                    log_callback("thread_error", {
                        "thread_name": thread_name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    pass
            
            # Wait before continuing (prevents error loops)
            time.sleep(error_delay)

