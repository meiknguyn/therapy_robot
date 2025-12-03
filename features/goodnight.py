"""Goodnight feature: Auto-play ambient music when light is low."""

import time
from pathlib import Path
from typing import Optional

from therapy_robot import config
from therapy_robot.audio import speaker
from therapy_robot.dashboard import csv_logger


class GoodnightFeature:
    """Manages ambient music playback based on light levels."""
    
    def __init__(
        self,
        music_volume: float = 0.4,
        check_interval: float = 2.0,
        dark_threshold: Optional[float] = None
    ):
        """
        Initialize goodnight feature.
        
        Args:
            music_volume: Volume for ambient music (0.0 to 1.0)
            check_interval: How often to check light level (seconds)
            dark_threshold: Light threshold for "dark" (uses config if None)
        """
        self.music_volume = max(0.0, min(1.0, music_volume))
        self.check_interval = check_interval
        self.dark_threshold = dark_threshold or config.AMBIENT_DARK_THRESHOLD
        
        self.is_music_playing = False
        self.current_music_file: Optional[str] = None
        self.last_check_time = 0.0
        
        # Find available music files
        self.available_music = self._find_music_files()
        
        if not self.available_music:
            print("⚠ Goodnight: No music files found in assets/music/")
            print(f"   Place .wav, .mp3, or .ogg files in: {config.MUSIC_DIR}")
        else:
            print(f"✓ Goodnight: Found {len(self.available_music)} music file(s)")
            for music_file in self.available_music:
                print(f"   - {music_file}")
    
    def _find_music_files(self) -> list[str]:
        """Find all supported music files in the music directory."""
        if not config.MUSIC_DIR.exists():
            return []
        
        # Supported formats
        extensions = {'.wav', '.mp3', '.ogg', '.flac'}
        music_files = []
        
        for file_path in config.MUSIC_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                music_files.append(file_path.name)
        
        return sorted(music_files)
    
    def _select_music_file(self) -> Optional[str]:
        """Select a music file to play (cycles through available files)."""
        if not self.available_music:
            return None
        
        # If we have a current file, try to continue with it
        if self.current_music_file and self.current_music_file in self.available_music:
            return self.current_music_file
        
        # Otherwise, use the first available file
        return self.available_music[0]
    
    def update(self, light_level: float, force_check: bool = False) -> None:
        """
        Update goodnight feature based on current light level.
        
        Args:
            light_level: Normalized light reading (0.0 to 1.0)
            force_check: Force check even if interval hasn't passed
        """
        current_time = time.time()
        
        # Throttle checks to avoid excessive music start/stop
        if not force_check and (current_time - self.last_check_time) < self.check_interval:
            return
        
        self.last_check_time = current_time
        
        is_dark = light_level < self.dark_threshold
        
        if is_dark and not self.is_music_playing:
            # Light just got dark - start music
            self._start_music()
        elif not is_dark and self.is_music_playing:
            # Light just got bright - stop music
            self._stop_music()
    
    def _start_music(self) -> None:
        """Start playing ambient music."""
        music_file = self._select_music_file()
        
        if not music_file:
            return
        
        self.current_music_file = music_file
        speaker.play_music(music_file, loop=True, volume=self.music_volume)
        self.is_music_playing = True
        
        # Log the event
        csv_logger.log_event(
            "goodnight_started",
            {
                "music_file": music_file,
                "volume": self.music_volume,
                "threshold": self.dark_threshold
            }
        )
        
        print(f"🌙 Goodnight mode: Playing {music_file} (volume: {self.music_volume:.1f})")
    
    def _stop_music(self) -> None:
        """Stop playing ambient music."""
        if not self.is_music_playing:
            return
        
        speaker.stop_music()
        self.is_music_playing = False
        
        # Log the event
        csv_logger.log_event("goodnight_stopped", {"reason": "light_detected"})
        
        print("☀️ Goodnight mode: Music stopped (light detected)")
    
    def stop(self) -> None:
        """Stop music and reset state (for cleanup)."""
        if self.is_music_playing:
            self._stop_music()
    
    def get_status(self) -> dict:
        """Get current status of goodnight feature."""
        return {
            "is_active": self.is_music_playing,
            "current_music": self.current_music_file,
            "available_music_count": len(self.available_music),
            "volume": self.music_volume,
            "threshold": self.dark_threshold
        }

