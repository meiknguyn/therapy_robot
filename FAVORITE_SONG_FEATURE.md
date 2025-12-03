# Favorite Song Feature

## Overview

The Therapy Robot can play your favorite song when you ask for it! Just say "Let's play my favorite song" and it will play `myfavsong.wav` from the music directory.

## How to Use

Simply type any of these phrases:
- "Let's play my favorite song"
- "Lets play my favorite song"
- "Play my favorite song"
- "Play favorite song"
- "My favorite song"

The robot will:
1. Stop any currently playing music (including goodnight ambient music)
2. Start playing `myfavsong.wav`
3. Continue chatting with you while the song plays

## Setup

### 1. Add Your Favorite Song

Place your favorite song file in the music directory:

```bash
# Copy your song file
cp /path/to/your/song.wav /home/mike/therapy_robot/assets/music/myfavsong.wav

# Or rename an existing file
mv /home/mike/therapy_robot/assets/music/your_song.wav \
   /home/mike/therapy_robot/assets/music/myfavsong.wav
```

**Supported formats:**
- `.wav` (recommended)
- `.mp3`
- `.ogg`
- `.flac`

### 2. Verify File Exists

```bash
ls -la /home/mike/therapy_robot/assets/music/myfavsong.wav
```

## Example Usage

```
You: Let's play my favorite song

🎵 Playing your favorite song: myfavsong.wav
   (You can continue chatting while it plays)

Robot (mood=7/10):
That's a great idea! Music can be so uplifting. I'm glad you're taking a moment to enjoy something you love. How does it make you feel?

You: It makes me feel relaxed

Robot (mood=8/10):
...
```

## Features

✅ **Flexible Phrase Detection**: Works with various phrasings  
✅ **Automatic Music Switching**: Stops ambient/goodnight music and plays your favorite  
✅ **Continuous Playback**: Song loops so you can enjoy it while chatting  
✅ **Event Logging**: All favorite song plays are logged to `logs/events.csv`  
✅ **Error Handling**: Friendly message if the file doesn't exist  

## Troubleshooting

### "Sorry, I couldn't find 'myfavsong.wav'"

**Solution:**
1. Check if the file exists:
   ```bash
   ls -la /home/mike/therapy_robot/assets/music/myfavsong.wav
   ```

2. Make sure the filename is exactly `myfavsong.wav` (case-sensitive)

3. Check the file format (should be `.wav`, `.mp3`, `.ogg`, or `.flac`)

### Song doesn't play

1. **Check file format**: Try converting to `.wav` format
2. **Check file permissions**: Make sure the file is readable
3. **Check audio system**: Make sure your audio output is working

### Song plays but stops immediately

- This might happen if the goodnight feature detects light changes
- The favorite song will continue playing unless you explicitly stop it or the program exits

## Logging

Favorite song plays are logged to `logs/events.csv`:

```csv
timestamp,event_type,data
2024-12-02 10:30:15,favorite_song_played,"{""song"": ""myfavsong.wav""}"
```

View recent plays:
```bash
grep favorite_song_played /home/mike/therapy_robot/logs/events.csv
```

## Customization

### Change the Song File

Edit `main.py` and change:
```python
favorite_song = "myfavsong.wav"
```

To:
```python
favorite_song = "your_song.wav"
```

### Change the Volume

Edit `main.py` and change:
```python
speaker.play_music(favorite_song, loop=True, volume=0.6)
```

Adjust `volume=0.6` to your preference (0.0 to 1.0).

### Change Phrase Detection

Edit the `favorite_song_phrases` list in `main.py` to add or remove phrases.

## Summary

✅ **Easy to use**: Just ask naturally  
✅ **Flexible**: Works with various phrasings  
✅ **Smart**: Stops other music automatically  
✅ **Logged**: All plays are recorded  
✅ **Continuous**: Song plays while you chat  

Enjoy your favorite song! 🎵

