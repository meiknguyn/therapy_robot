"""Main entry point for the Therapy Robot."""

import threading
import time

from therapy_robot import config
from therapy_robot.ai import gemini_client
from therapy_robot.audio import speaker
from therapy_robot.dashboard import csv_logger
from therapy_robot.features.alarm import AlarmFeature, parse_alarm_time
from therapy_robot.features.breathing import BreathingExercise
from therapy_robot.features.goodnight import GoodnightFeature
from therapy_robot.features.pomodoro import PomodoroFeature
from therapy_robot.features.safety import SafetyFeature
from therapy_robot.hardware.accelerometer import Accelerometer
from therapy_robot.hardware.joystick import Joystick
from therapy_robot.hardware.led_ctrl import LEDController
from therapy_robot.hardware.photoresistor import Photoresistor
from therapy_robot.hardware.rotary_button import RotaryButton


def main():
    """Main therapy robot loop."""
    print("Starting Therapy Robot")
    print("=" * 50)
    
    # Initialize hardware (with error handling)
    led = None
    ldr = None
    accelerometer = None
    joystick = None
    rotary_button = None
    goodnight = None
    pomodoro = None
    breathing = None
    alarm = None
    safety = None
    
    try:
        led = LEDController()
        led.breathing_start()
        print("✓ LED controller initialized")
    except Exception as e:
        print(f"⚠ LED controller unavailable: {e}")
        print("  Continuing without LED feedback...")
    
    try:
        ldr = Photoresistor()
        print("✓ Photoresistor initialized")
    except Exception as e:
        print(f"⚠ Photoresistor unavailable: {e}")
        print("  Continuing without ambient light detection...")
    
    try:
        accelerometer = Accelerometer(smoothing_samples=5, auto_calibrate=False)
        print("✓ Accelerometer initialized")
    except Exception as e:
        print(f"⚠ Accelerometer unavailable: {e}")
        print("  Continuing without motion detection...")
    
    try:
        joystick = Joystick()
        print("✓ Joystick initialized")
    except Exception as e:
        print(f"⚠ Joystick unavailable: {e}")
        print("  Continuing without joystick control...")
    
    try:
        from therapy_robot.hardware.rotary_button import RotaryButton
        rotary_button = RotaryButton()
        print("✓ Rotary button initialized")
    except Exception as e:
        print(f"⚠ Rotary button unavailable: {e}")
        print("  Continuing without rotary button control...")
        rotary_button = None
    
    # Initialize volume control via joystick Y-axis (step-based with hold time)
    volume_thread = None
    stop_volume_thread = threading.Event()
    volume_file = config.LOG_DIR / "volume.txt"
    
    # Load volume from file if exists, otherwise use default
    current_volume = 0.6  # Default volume
    if volume_file.exists():
        try:
            with open(volume_file, 'r') as f:
                current_volume = float(f.read().strip())
                current_volume = max(0.0, min(1.0, current_volume))  # Clamp to valid range
        except:
            pass
    else:
        # Create initial volume file
        try:
            with open(volume_file, 'w') as f:
                f.write(str(current_volume))
        except:
            pass
    
    speaker.set_volume(current_volume)  # Set initial volume
    
    if joystick is not None:
        try:
            def volume_control_monitor():
                """Background thread to read joystick Y and adjust volume with step-based control."""
                nonlocal current_volume
                
                # State tracking for hold-time mechanism
                hold_start_time = None
                hold_direction = None  # 'up' or 'down'
                last_change_time = 0.0
                
                while not stop_volume_thread.is_set():
                    try:
                        # Read joystick Y axis (0.0 = up, 1.0 = down)
                        y_position = joystick.read_y()
                        current_time = time.time()
                        
                        # Check if joystick is in volume-up zone (pushed up)
                        # Since center is ~0.62, UP should decrease Y below threshold
                        # But if joystick is inverted, UP might increase Y instead
                        # Try both: Y < threshold (normal) OR check if Y is significantly different from center
                        center_position = 0.622  # Calibrated center position
                        y_diff_from_center = y_position - center_position
                        
                        # UP zone: either Y < threshold OR Y is significantly below center
                        # UP zone range: 0.500-0.593, threshold: 0.59 (below UP max 0.593)
                        # Use relative detection as primary method since joystick may not reach absolute threshold
                        is_up_zone = (y_position < config.VOLUME_UP_THRESHOLD or 
                                      y_diff_from_center < -0.005)  # At least 0.005 below center (Y < 0.617, very sensitive)
                        
                        if is_up_zone:
                            # Joystick is pushed up - increase volume
                            if hold_direction != 'up':
                                # Just entered up zone - start timing
                                # Reset cooldown when switching directions to allow immediate change
                                if hold_direction == 'down':
                                    last_change_time = 0.0  # Reset cooldown when switching from down to up
                                hold_direction = 'up'
                                hold_start_time = current_time
                            else:
                                # Still in up zone - check if held long enough
                                hold_duration = current_time - hold_start_time
                                time_since_last_change = current_time - last_change_time
                                
                                # Check if held long enough AND cooldown has passed
                                if (hold_duration >= config.VOLUME_HOLD_TIME and 
                                    time_since_last_change >= config.VOLUME_COOLDOWN):
                                    # Increase volume by step
                                    new_volume = min(1.0, current_volume + config.VOLUME_STEP_SIZE)
                                    if new_volume != current_volume:
                                        current_volume = new_volume
                                        speaker.set_volume(current_volume)
                                        # Save volume to file for dashboard sync
                                        try:
                                            with open(volume_file, 'w') as f:
                                                f.write(str(current_volume))
                                        except:
                                            pass
                                        last_change_time = current_time
                                        
                                        # Log and display
                                        csv_logger.log_event(
                                            "volume_adjusted",
                                            {
                                                "volume": round(current_volume, 2),
                                                "joystick_y": round(y_position, 3),
                                                "direction": "up"
                                            }
                                        )
                                        # Display volume with visual bar
                                        volume_percent = int(current_volume * 100)
                                        bar_length = 20
                                        filled = int(current_volume * bar_length)
                                        bar = "█" * filled + "░" * (bar_length - filled)
                                        print(f"🔊 Volume: {volume_percent:3d}% [{bar}]")
                                        # Reset hold timer to prevent rapid changes
                                        hold_start_time = current_time
                        
                        # Check if joystick is in volume-down zone (pushed down)
                        # Since center is ~0.622, DOWN should increase Y above threshold
                        # DOWN zone range: 0.674-1.000, threshold: 0.65
                        is_down_zone = (y_position > config.VOLUME_DOWN_THRESHOLD or 
                                       y_diff_from_center > 0.05)  # At least 0.05 above center (more sensitive)
                        
                        if is_down_zone:
                            # Joystick is pushed down - decrease volume
                            if hold_direction != 'down':
                                # Just entered down zone - start timing
                                # Reset cooldown when switching directions to allow immediate change
                                if hold_direction == 'up':
                                    last_change_time = 0.0  # Reset cooldown when switching from up to down
                                hold_direction = 'down'
                                hold_start_time = current_time
                            else:
                                # Still in down zone - check if held long enough
                                hold_duration = current_time - hold_start_time
                                time_since_last_change = current_time - last_change_time
                                
                                # Check if held long enough AND cooldown has passed
                                if (hold_duration >= config.VOLUME_HOLD_TIME and 
                                    time_since_last_change >= config.VOLUME_COOLDOWN):
                                    # Decrease volume by step
                                    new_volume = max(0.0, current_volume - config.VOLUME_STEP_SIZE)
                                    if new_volume != current_volume:
                                        current_volume = new_volume
                                        speaker.set_volume(current_volume)
                                        # Save volume to file for dashboard sync
                                        try:
                                            with open(volume_file, 'w') as f:
                                                f.write(str(current_volume))
                                        except:
                                            pass
                                        last_change_time = current_time
                                        
                                        # Log and display
                                        csv_logger.log_event(
                                            "volume_adjusted",
                                            {
                                                "volume": round(current_volume, 2),
                                                "joystick_y": round(y_position, 3),
                                                "direction": "down"
                                            }
                                        )
                                        # Display volume with visual bar
                                        volume_percent = int(current_volume * 100)
                                        bar_length = 20
                                        filled = int(current_volume * bar_length)
                                        bar = "█" * filled + "░" * (bar_length - filled)
                                        print(f"🔊 Volume: {volume_percent:3d}% [{bar}]")
                                        # Reset hold timer to prevent rapid changes
                                        hold_start_time = current_time
                        
                        else:
                            # Joystick is in neutral zone (center) - reset hold tracking
                            hold_direction = None
                            hold_start_time = None
                        
                    except Exception as e:
                        # Skip joystick reading if it fails
                        pass
                    
                    # Sleep for a short interval before next check
                    time.sleep(0.05)  # Check every 0.05 seconds for responsive control
            
            volume_thread = threading.Thread(target=volume_control_monitor, daemon=True)
            volume_thread.start()
            print("✓ Volume control (joystick Y-axis) active")
            print(f"   Step size: {int(config.VOLUME_STEP_SIZE * 100)}%, Hold time: {config.VOLUME_HOLD_TIME}s")
            
            # Display initial volume status
            volume_percent = int(current_volume * 100)
            bar_length = 20
            filled = int(current_volume * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"   🔊 Current Volume: {volume_percent:3d}% [{bar}]")
        except Exception as e:
            print(f"⚠ Volume control unavailable: {e}")
            print("  Continuing without volume control...")
    
    # Initialize goodnight feature (only if photoresistor is available)
    goodnight_thread = None
    stop_goodnight_thread = threading.Event()
    
    if ldr is not None:
        try:
            goodnight = GoodnightFeature(
                music_volume=config.GOODNIGHT_MUSIC_VOLUME,
                check_interval=config.GOODNIGHT_CHECK_INTERVAL
            )
            print("✓ Goodnight feature initialized")
            
            # Start background thread to monitor light continuously
            def goodnight_monitor():
                """Background thread to continuously monitor light and update goodnight feature."""
                while not stop_goodnight_thread.is_set():
                    try:
                        light = ldr.read_normalized()
                        csv_logger.log_event("ambient_light", {"value": light})
                        
                        # Update goodnight feature (will start/stop music as needed)
                        goodnight.update(light, force_check=False)
                    except Exception as e:
                        # Skip light reading if it fails
                        pass
                    
                    # Sleep for a short interval before next check
                    time.sleep(0.5)  # Check every 0.5 seconds
            
            goodnight_thread = threading.Thread(target=goodnight_monitor, daemon=True)
            goodnight_thread.start()
            print("✓ Goodnight monitor thread started")
        except Exception as e:
            print(f"⚠ Goodnight feature unavailable: {e}")
            print("  Continuing without goodnight feature...")
            goodnight = None
    
    # Initialize Pomodoro feature (if LED available)
    if led is not None:
        try:
            pomodoro = PomodoroFeature(led, study_duration=15.0, rest_duration=5.0)
            print("✓ Pomodoro feature initialized")
        except Exception as e:
            print(f"⚠ Pomodoro feature unavailable: {e}")
            pomodoro = None
    
    # Initialize Breathing Exercise feature (if LED available)
    if led is not None:
        try:
            breathing = BreathingExercise(led, inhale_duration=3.0, hold_duration=3.0, exhale_duration=3.0)
            print("✓ Breathing exercise feature initialized")
        except Exception as e:
            print(f"⚠ Breathing exercise feature unavailable: {e}")
            breathing = None
    
    # Initialize Alarm feature (if rotary button available)
    if rotary_button is not None:
        try:
            alarm = AlarmFeature(rotary_button)
            print("✓ Alarm feature initialized")
        except Exception as e:
            print(f"⚠ Alarm feature unavailable: {e}")
            alarm = None
    
    # Initialize Safety feature (if accelerometer and LED available)
    if accelerometer is not None and led is not None:
        try:
            safety = SafetyFeature(accelerometer, led)
            safety.start()  # Start monitoring immediately
            print("✓ Safety feature initialized and monitoring")
        except Exception as e:
            print(f"⚠ Safety feature unavailable: {e}")
            safety = None
        except Exception as e:
            print(f"⚠ Goodnight feature unavailable: {e}")
            print("  Continuing without goodnight feature...")
            goodnight = None
    
    # Start background thread to sync volume from dashboard
    volume_sync_thread = None
    stop_volume_sync_thread = threading.Event()
    last_volume_status_time = time.time()
    volume_status_interval = 30.0  # Show volume status every 30 seconds
    
    def volume_sync_monitor():
        """Background thread to sync volume from dashboard file."""
        nonlocal current_volume, last_volume_status_time
        
        while not stop_volume_sync_thread.is_set():
            try:
                if volume_file.exists():
                    with open(volume_file, 'r') as f:
                        dashboard_volume = float(f.read().strip())
                        dashboard_volume = max(0.0, min(1.0, dashboard_volume))
                        # Only update if different (avoid unnecessary updates)
                        if abs(dashboard_volume - current_volume) > 0.01:
                            current_volume = dashboard_volume
                            speaker.set_volume(current_volume)
                            volume_percent = int(current_volume * 100)
                            bar_length = 20
                            filled = int(current_volume * bar_length)
                            bar = "█" * filled + "░" * (bar_length - filled)
                            print(f"🔊 Volume: {volume_percent:3d}% [{bar}] (from dashboard)")
                
                # Periodically show volume status
                current_time = time.time()
                if current_time - last_volume_status_time >= volume_status_interval:
                    if joystick is not None:
                        volume_percent = int(current_volume * 100)
                        bar_length = 20
                        filled = int(current_volume * bar_length)
                        bar = "█" * filled + "░" * (bar_length - filled)
                        print(f"\n[Status] 🔊 Volume: {volume_percent:3d}% [{bar}]")
                    last_volume_status_time = current_time
            except Exception as e:
                # Silent fail - don't spam errors
                pass
            
            # Check every 0.5 seconds
            time.sleep(0.5)
    
    volume_sync_thread = threading.Thread(target=volume_sync_monitor, daemon=True)
    volume_sync_thread.start()
    print("✓ Volume sync thread started (dashboard ↔ main program)")
    
    try:
        while True:
            
            # Get user input
            user_text = input("\nYou: ").strip()
            
            # Skip empty input
            if not user_text:
                continue
            
            # Check for exit commands
            if user_text.lower() in {"quit", "exit", "bye"}:
                print("\nEnding session...")
                break
            
            # Check for "play my favorite song" command
            user_text_lower = user_text.lower()
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
                    # Stop any currently playing music (including goodnight feature)
                    if goodnight is not None:
                        goodnight.stop()
                    
                    # Play the favorite song
                    speaker.play_music(favorite_song, loop=True, volume=0.6)
                    csv_logger.log_event("favorite_song_played", {"song": favorite_song})
                    print(f"\n🎵 Playing your favorite song: {favorite_song}")
                    print("   (You can continue chatting while it plays)")
                    # Continue to normal chat flow (still analyze emotion and get reply)
                else:
                    print(f"\n⚠️ Sorry, I couldn't find '{favorite_song}' in {config.MUSIC_DIR}")
                    print("   Make sure the file exists and try again!")
                    # Continue to normal chat flow
            
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
                # Stop any currently playing music (including goodnight feature)
                if goodnight is not None:
                    goodnight.stop()
                
                speaker.stop_music()
                csv_logger.log_event("music_stopped", {"source": "user_command", "command": user_text})
                print("\n🔇 Music stopped")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
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
                if pomodoro is not None:
                    if pomodoro.is_active:
                        print("\n🍅 Pomodoro session is already running!")
                    else:
                        pomodoro.start()
                else:
                    print("\n⚠️ Pomodoro feature is not available (LED controller required)")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
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
                if pomodoro is not None and pomodoro.is_active:
                    pomodoro.stop()
                else:
                    print("\n⚠️ No active Pomodoro session to stop")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
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
                if breathing is not None:
                    if breathing.is_active:
                        print("\n🧘 Breathing exercise is already running!")
                    else:
                        breathing.start()
                else:
                    print("\n⚠️ Breathing exercise feature is not available (LED controller required)")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
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
                if breathing is not None and breathing.is_active:
                    breathing.stop()
                else:
                    print("\n⚠️ No active breathing exercise session to stop")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
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
                if alarm is not None:
                    # Parse alarm time from user text
                    alarm_time = parse_alarm_time(user_text)
                    if alarm_time:
                        # Cancel existing alarm if any
                        if alarm.is_set:
                            alarm.cancel_alarm()
                        # Set new alarm
                        alarm.set_alarm(alarm_time)
                    else:
                        print("\n⚠️ Could not parse alarm time. Try:")
                        print("   - 'set alarm at 14:30'")
                        print("   - 'wake me up in 30 minutes'")
                        print("   - 'alarm in 5 minutes'")
                        print("   - 'wake me up in 30 seconds'")
                else:
                    print("\n⚠️ Alarm feature is not available (rotary button required)")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
            # Check for Alarm cancel commands
            alarm_cancel_phrases = [
                "cancel alarm",
                "stop alarm",
                "turn off alarm",
                "disable alarm"
            ]
            
            if any(phrase in user_text_lower for phrase in alarm_cancel_phrases):
                if alarm is not None:
                    if alarm.is_set:
                        alarm.cancel_alarm()
                    elif alarm.is_ringing:
                        alarm._stop_alarm()
                    else:
                        print("\n⚠️ No alarm is currently set or ringing")
                else:
                    print("\n⚠️ Alarm feature is not available")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
            # Check for Safety feature response (fall detection)
            if safety is not None and safety.waiting_for_response:
                if safety.handle_user_response(user_text):
                    # User confirmed they're okay - skip normal chat flow
                    continue
            
            # Check for Safety feature stop/cancel commands
            safety_stop_phrases = [
                "stop fall detection",
                "cancel fall detection",
                "turn off fall detection",
                "disable fall detection",
                "stop safety",
                "cancel safety",
                "turn off safety",
                "disable safety"
            ]
            
            if any(phrase in user_text_lower for phrase in safety_stop_phrases):
                if safety is not None:
                    if safety.emergency_mode or safety.waiting_for_response:
                        # Cancel emergency mode or fall detection
                        safety.cancel_fall_detection()
                        print("\n🛡️ Fall detection cancelled. Safety feature resuming normal monitoring.")
                    else:
                        print("\n⚠️ No active fall detection or emergency to stop")
                else:
                    print("\n⚠️ Safety feature is not available")
                # Continue to normal chat flow (still analyze emotion and get reply)
            
            # Analyze emotion
            emo = gemini_client.analyze_emotion_with_cache(user_text)
            mood_score = emo["score"]
            
            # Get support reply from Gemini
            reply = gemini_client.get_support_reply(mood_score, user_text)
            
            # Log chat interaction
            csv_logger.log_chat(user_text, mood_score, reply)
            
            # Print response
            print(f"\nRobot (mood={mood_score}/10):\n{reply}\n")
            
            # Set LED brightness based on mood (if available)
            if led is not None:
                try:
                    led.set_brightness(mood_score / 10.0)
                except Exception:
                    # Skip LED update if it fails
                    pass
            
            # Small delay to avoid spamming logs
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        if led is not None:
            try:
                led.breathing_stop()
                led.close()
            except Exception:
                pass
        
        # Stop volume control thread
        if volume_thread is not None:
            try:
                stop_volume_thread.set()
                volume_thread.join(timeout=2.0)
            except Exception as e:
                # Thread might already be stopped or have issues
                pass
        
        # Stop volume sync thread
        if volume_sync_thread is not None:
            try:
                stop_volume_sync_thread.set()
                volume_sync_thread.join(timeout=2.0)
            except Exception as e:
                # Thread might already be stopped or have issues
                pass
        
        # Stop goodnight feature and thread
        if goodnight_thread is not None:
            try:
                stop_goodnight_thread.set()
                goodnight_thread.join(timeout=2.0)
            except Exception as e:
                # Thread might already be stopped or have issues
                pass
        
        if goodnight is not None:
            try:
                goodnight.stop()
            except Exception:
                pass
        
        # Stop Pomodoro session
        if pomodoro is not None:
            try:
                pomodoro.stop()
            except Exception:
                pass
        
        # Stop Breathing Exercise session
        if breathing is not None:
            try:
                breathing.stop()
            except Exception:
                pass
        
        # Cancel Alarm
        if alarm is not None:
            try:
                alarm.cancel_alarm()
            except Exception:
                pass
        
        # Stop Safety feature
        if safety is not None:
            try:
                safety.stop()
            except Exception:
                pass
        
        speaker.stop_music()
        
        # Close rotary button
        if rotary_button is not None:
            try:
                rotary_button.close()
            except Exception:
                pass
        
        if joystick is not None:
            try:
                joystick.close()
            except Exception:
                pass
        
        if ldr is not None:
            try:
                ldr.close()
            except Exception:
                pass
        
        print("Therapy Robot shutdown complete.")


if __name__ == "__main__":
    main()

