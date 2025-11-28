# modules/ambient_music.py
"""
Ambient Music Module
Manages ambient calming music playback and logging.
"""
import os
import random
from audio.speaker import Speaker


class AmbientMusic:
    """
    Ambient music controller that manages playback through Speaker.
    Handles random track selection and event logging.
    """

    def __init__(self, speaker: Speaker, log_callback=None):
        """
        Initialize ambient music controller.
        
        Args:
            speaker: Speaker instance for playback
            log_callback: Optional callback function(event_type, details) for logging
        """
        self.speaker = speaker
        self.log_callback = log_callback
        self.current_track_index = 0
        self.track_list = []
        self._refresh_track_list()

    def _refresh_track_list(self):
        """Refresh list of available music tracks."""
        self.track_list = self.speaker.list_available_files()
        if not self.track_list:
            print("[AmbientMusic] No music files found in assets/music/")

    def _log(self, event_type: str, details: dict):
        """Log event using callback."""
        if self.log_callback:
            try:
                self.log_callback(event_type, details)
            except Exception as e:
                print(f"[AmbientMusic] Error in log callback: {e}")

    def start(self, track_name=None):
        """
        Start ambient music playback.
        
        Args:
            track_name: Optional specific track name. If None, plays random track.
        """
        # Refresh track list in case new files were added
        self._refresh_track_list()
        
        if not self.track_list:
            print("[AmbientMusic] No music files available")
            return False
        
        # Select track
        if track_name:
            if track_name not in self.track_list:
                print(f"[AmbientMusic] Track '{track_name}' not found, using random track")
                track_name = None
        
        if track_name is None:
            # Select random track or next track in sequence
            if self.track_list:
                track_name = random.choice(self.track_list)
        
        # Play the track
        success = self.speaker.play_file(track_name, loop=True)
        
        if success:
            self.current_track_index = self.track_list.index(track_name) if track_name in self.track_list else 0
            self._log("ambient_music_start", {
                "track": track_name,
                "volume": self.speaker.get_volume(),
                "loop": True
            })
            print(f"[AmbientMusic] Started playing: {track_name}")
            return True
        else:
            return False

    def stop(self):
        """Stop ambient music playback."""
        self.speaker.stop()
        self._log("ambient_music_stop", {
            "track": self.speaker.get_current_file()
        })
        print("[AmbientMusic] Stopped playback")

    def next_track(self):
        """Switch to next track in playlist."""
        self._refresh_track_list()
        if not self.track_list:
            return False
        
        self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
        track_name = self.track_list[self.current_track_index]
        
        success = self.speaker.play_file(track_name, loop=True)
        if success:
            self._log("ambient_music_change", {
                "track": track_name,
                "direction": "next"
            })
        return success

    def previous_track(self):
        """Switch to previous track in playlist."""
        self._refresh_track_list()
        if not self.track_list:
            return False
        
        self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
        track_name = self.track_list[self.current_track_index]
        
        success = self.speaker.play_file(track_name, loop=True)
        if success:
            self._log("ambient_music_change", {
                "track": track_name,
                "direction": "previous"
            })
        return success

    def set_volume(self, volume: float):
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        old_volume = self.speaker.get_volume()
        self.speaker.set_volume(volume)
        
        self._log("ambient_music_volume_change", {
            "old_volume": old_volume,
            "new_volume": volume
        })

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.speaker.is_playing:
            self.speaker.toggle_play_pause()
            self._log("ambient_music_toggle", {
                "action": "play_pause",
                "track": self.speaker.get_current_file()
            })

    def is_playing(self):
        """Check if music is currently playing."""
        return self.speaker.is_playing

