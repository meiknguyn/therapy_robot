# Music Files Information

## Current Music Library

The therapy robot currently has the following ambient music files:

- **beach.wav** - Beach ambiance sounds
- **windchime.wav** - Wind chime sounds

## Automatic Detection

The system automatically detects all music files in the `assets/music/` directory when:
- The application starts
- Music playback begins
- Track switching occurs

## Supported Formats

The system supports these audio formats:
- `.wav` (recommended for best compatibility)
- `.mp3`
- `.ogg`
- `.flac`

## How to Add More Music

1. Place your music files in `assets/music/` directory
2. Use supported formats (`.wav` is recommended)
3. The system will automatically detect them on next music start
4. No restart required - files are detected dynamically

## Playing Music

Use these voice commands:
- **"play music"** - Starts random track
- **"calm me"** - Starts ambient music
- **"start ambient"** - Starts music
- **"relax"** - Starts music

## Control Music

- **Joystick Up/Down** - Volume control
- **Joystick Left/Right** - Switch tracks
- **Joystick Press** - Play/Pause toggle
- **Rotary Encoder** - Fine volume adjustment

## File Verification

On startup, the system will print:
```
[Speaker] Found 2 music file(s): beach.wav, windchime.wav
```

If you see "No music files found", check:
- Files are in `assets/music/` directory
- Files have correct extensions (.wav, .mp3, .ogg, .flac)
- Files are valid audio files (not corrupted)

---

**Note**: The system uses pygame mixer for audio playback, which works best with uncompressed formats like WAV.

