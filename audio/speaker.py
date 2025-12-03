"""Audio playback using Pygame mixer."""

import os
import threading
from pathlib import Path

import pygame.mixer

from therapy_robot import config

# Thread-safe initialization
_mixer_initialized = False
_mixer_lock = threading.Lock()


def _ensure_init():
    """Ensure pygame.mixer is initialized (thread-safe)."""
    global _mixer_initialized
    
    if not _mixer_initialized:
        with _mixer_lock:
            if not _mixer_initialized:
                # Force pygame to use PulseAudio for proper audio routing
                # This ensures audio goes to the correct output device (e.g., USB headphones)
                os.environ.setdefault('SDL_AUDIODRIVER', 'pulse')
                
                # Unmute the default audio sink (headphones might be muted)
                try:
                    import subprocess
                    subprocess.run(
                        ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    # If pactl is not available, continue anyway
                    pass
                
                pygame.mixer.init()
                _mixer_initialized = True


def play_music(filename: str, loop: bool = True, volume: float = 0.6):
    """
    Play music file from assets/music directory.
    
    Args:
        filename: Name of the audio file (e.g., "calm.wav")
        loop: Whether to loop the music
        volume: Volume level (0.0 to 1.0)
    """
    _ensure_init()
    
    file_path = config.MUSIC_DIR / filename
    
    if not file_path.exists():
        print(f"Warning: Music file not found: {file_path}")
        return
    
    # Stop any currently playing music
    stop_music()
    
    # Load and play
    pygame.mixer.music.load(str(file_path))
    pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    if loop:
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    else:
        pygame.mixer.music.play()


def stop_music():
    """Stop currently playing music."""
    _ensure_init()
    pygame.mixer.music.stop()


def set_volume(volume: float):
    """
    Set music volume.
    
    Args:
        volume: Volume level (0.0 to 1.0, clamped automatically)
    """
    _ensure_init()
    clamped_volume = max(0.0, min(1.0, volume))
    pygame.mixer.music.set_volume(clamped_volume)

