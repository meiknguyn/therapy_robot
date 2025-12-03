# Environment Variables (.env File) Guide

## Overview

The project now uses a `.env` file to store sensitive configuration like API keys. This keeps secrets out of your code and makes it easier to manage.

## File Created

**`.env`** - Contains your Gemini API key

## How It Works

1. The `.env` file is automatically loaded by `config.py` using `python-dotenv`
2. Your API key is read from the file when the program starts
3. No need to manually export environment variables!

## File Location

```
/home/mike/therapy_robot/.env
```

## File Contents

```env
# Therapy Robot Environment Variables
GEMINI_API_KEY=AIzaSyA4tutODEl2iZA7wiGYn9Wzk7l14FlHLeE
```

## Security

✅ **`.env` is in `.gitignore`** - Won't be committed to git  
✅ **File permissions**: 600 (read/write for owner only)  
✅ **Keep it secret**: Don't share this file!

## How to Edit

### Option 1: Using nano

```bash
cd /home/mike/therapy_robot
nano .env
```

Add or edit:
```env
GEMINI_API_KEY=your_key_here
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### Option 2: Using echo

```bash
cd /home/mike/therapy_robot
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Option 3: Using cat

```bash
cd /home/mike/therapy_robot
cat > .env << 'EOF'
GEMINI_API_KEY=your_key_here
EOF
```

## Testing

Test if the .env file is loaded:

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python3 -c "
from therapy_robot import config
print(f'API Key: {config.GEMINI_API_KEY[:10]}...{config.GEMINI_API_KEY[-4:]}')
"
```

## Usage in Code

The API key is automatically loaded! Just use:

```python
from therapy_robot import config

# API key is already loaded from .env
api_key = config.GEMINI_API_KEY
```

## Running the Program

Now you can run the program without exporting the API key:

```bash
cd /home/mike/therapy_robot
source venv/bin/activate
python -m therapy_robot.main
```

No need for: `export GEMINI_API_KEY='...'` anymore!

## Adding More Variables

You can add more environment variables to `.env`:

```env
GEMINI_API_KEY=your_key_here
SOME_OTHER_KEY=some_value
ANOTHER_SETTING=123
```

Then access them in `config.py`:
```python
SOME_OTHER_KEY = os.getenv("SOME_OTHER_KEY", "default_value")
```

## Troubleshooting

### API key not loading?

1. Check file exists: `ls -la /home/mike/therapy_robot/.env`
2. Check file permissions: Should be 600
3. Check file contents: `cat /home/mike/therapy_robot/.env`
4. Verify format: `GEMINI_API_KEY=your_key_here` (no spaces around `=`)

### File not found?

Make sure you're running from the project directory or parent directory:
```bash
cd /home/mike  # or /home/mike/therapy_robot
```

## Backup

**Important**: Keep a backup of your `.env` file in a safe place!

```bash
# Backup
cp /home/mike/therapy_robot/.env ~/therapy_robot_env_backup

# Restore
cp ~/therapy_robot_env_backup /home/mike/therapy_robot/.env
```

## Summary

✅ `.env` file created with your API key  
✅ Automatically loaded by `config.py`  
✅ No need to export environment variables  
✅ Secure (in .gitignore, proper permissions)  
✅ Easy to edit and manage  

Your API key is now stored securely in `.env`! 🎉

