# audio/speaker.py
"""
Speaker Module for Ambient Music Playback
Uses pygame mixer for non-blocking background playback.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import config
except ImportError:
    try:
        from therapy_robot import config
    except ImportError:
        config = None

import pygame
import threading
import time

try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    HAVE_PYGAME = True
except Exception as e:
    print(f"[Speaker] pygame mixer initialization failed: {e}")
    HAVE_PYGAME = False


class Speaker:
    """
    Speaker controller for playing ambient calming music.
    Uses pygame mixer for non-blocking playback.
    """

    def __init__(self, music_dir=None):
        """
        Initialize speaker.
        
        Args:
            music_dir: Directory containing music files (uses config.MUSIC_DIR if None)
        """
        # Use config if available, otherwise default
        if music_dir is None:
            if config and hasattr(config, 'MUSIC_DIR'):
                music_dir = config.MUSIC_DIR
                # Resolve path relative to project root if config provides a function
                if config and hasattr(config, 'get_project_root'):
                    project_root = config.get_project_root()
                    music_dir = str(project_root / music_dir)
            else:
                music_dir = "assets/music"
        
        # Store as resolved absolute path for reliability
        if not os.path.isabs(music_dir):
            # If relative, try to resolve from project root or current directory
            if config and hasattr(config, 'get_project_root'):
                project_root = config.get_project_root()
                music_dir = str(project_root / music_dir)
            else:
                # Fallback: resolve from current working directory
                music_dir = os.path.abspath(music_dir)
        
        self.music_dir = music_dir
        self.current_file = None
        self.volume = 0.7  # Default volume (0.0 to 1.0)
        self.is_playing = False
        self.loop = True  # Loop music by default
        
        if not HAVE_PYGAME:
            print("[Speaker] pygame not available, using software simulation")
        
        # Ensure music directory exists
        if not os.path.exists(music_dir):
            print(f"[Speaker] Music directory '{music_dir}' does not exist, creating...")
            os.makedirs(music_dir, exist_ok=True)
        
        # List available files on startup
        available = self.list_available_files()
        if available:
            print(f"[Speaker] Found {len(available)} music file(s): {', '.join(available)}")
        else:
            print(f"[Speaker] Warning: No music files found in '{music_dir}'. Supported formats: .wav, .mp3, .ogg, .flac")

    def set_volume(self, value: float):
        """
        Set playback volume.
        
        Args:
            value: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, value))
        
        if HAVE_PYGAME:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception as e:
                print(f"[Speaker] Error setting volume: {e}")
        
        print(f"[Speaker] Volume set to {self.volume:.2f}")

    def get_volume(self):
        """Get current volume level."""
        return self.volume

    def play_file(self, filename: str, loop: bool = None):
        """
        Play a music file.
        
        Args:
            filename: Name of music file (e.g., "calm1.wav")
            loop: Whether to loop playback (None = use default loop setting)
        """
        if loop is None:
            loop = self.loop
        
        filepath = os.path.join(self.music_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"[Speaker] Music file not found: {filepath}")
            return False
        
        if not HAVE_PYGAME:
            print(f"[Speaker] [SIMULATION] Would play: {filename} (loop={loop})")
            self.current_file = filename
            self.is_playing = True
            return True
        
        try:
            # Stop any currently playing music
            if self.is_playing:
                pygame.mixer.music.stop()
            
            # Load and play the file
            # For WAV files, pygame.mixer.music should work, but if it fails,
            # we can try loading it as a sound object (though that's less ideal for music)
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.volume)
            
            # Play with or without looping
            if loop:
                pygame.mixer.music.play(-1)  # -1 = infinite loop
            else:
                pygame.mixer.music.play(1)   # Play once
            
            self.current_file = filename
            self.is_playing = True
            
            # Get file info for logging
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # Size in MB
            print(f"[Speaker] Playing: {filename} (loop={loop}, size={file_size:.2f} MB)")
            return True
        except pygame.error as e:
            print(f"[Speaker] Pygame error playing file '{filename}': {e}")
            print(f"[Speaker] This might be a file format issue. Try converting the file or check if it's a valid audio file.")
            self.is_playing = False
            return False
        except Exception as e:
            print(f"[Speaker] Error playing file '{filename}': {e}")
            import traceback
            traceback.print_exc()
            self.is_playing = False
            return False

    def stop(self):
        """Stop playback."""
        if HAVE_PYGAME:
            try:
                pygame.mixer.music.stop()
            except Exception as e:
                print(f"[Speaker] Error stopping playback: {e}")
        
        self.is_playing = False
        self.current_file = None
        print("[Speaker] Playback stopped")

    def pause(self):
        """Pause playback."""
        if HAVE_PYGAME:
            try:
                pygame.mixer.music.pause()
                print("[Speaker] Playback paused")
            except Exception as e:
                print(f"[Speaker] Error pausing playback: {e}")

    def unpause(self):
        """Resume playback."""
        if HAVE_PYGAME:
            try:
                pygame.mixer.music.unpause()
                print("[Speaker] Playback resumed")
            except Exception as e:
                print(f"[Speaker] Error resuming playback: {e}")

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if not self.is_playing:
            return
        
        if HAVE_PYGAME:
            if pygame.mixer.music.get_busy():
                self.pause()
            else:
                self.unpause()
        else:
            print("[Speaker] [SIMULATION] Toggling play/pause")

    def get_current_file(self):
        """Get currently playing file name."""
        return self.current_file

    def list_available_files(self):
        """
        List available music files in music directory.
        
        Returns:
            List of music file names
        """
        if not os.path.exists(self.music_dir):
            return []
        
        music_extensions = ['.wav', '.mp3', '.ogg', '.flac']
        files = []
        
        for filename in os.listdir(self.music_dir):
            if any(filename.lower().endswith(ext) for ext in music_extensions):
                files.append(filename)
        
        return sorted(files)

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if HAVE_PYGAME:
            try:
                pygame.mixer.quit()
            except:
                pass

