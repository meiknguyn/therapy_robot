# Therapy Robot - Complete Run Guides

This document provides links to all guides for running the Therapy Robot project.

## 📚 Documentation Index

### Quick Start Guides

1. **[QUICK_START.md](QUICK_START.md)** - Complete quick start guide
   - Initial setup
   - Permission fixes
   - Running main project
   - Running dashboard
   - Troubleshooting

2. **[COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)** - Quick command reference
   - All commands in one place
   - Copy-paste ready
   - One-liners for common tasks

### Detailed Run Guides

3. **[RUN_MAIN_PROJECT.md](RUN_MAIN_PROJECT.md)** - Running the main therapy robot
   - Step-by-step instructions
   - Voice commands
   - Hardware features
   - Troubleshooting

4. **[RUN_DASHBOARD.md](RUN_DASHBOARD.md)** - Running the web dashboard
   - Dashboard setup
   - Access methods
   - API endpoints
   - Features overview

5. **[FIX_PERMISSIONS.md](FIX_PERMISSIONS.md)** - Fixing hardware permissions
   - SPI permission fixes
   - GPIO permission fixes
   - Multiple methods (temporary/permanent)
   - Verification steps

## 🚀 Quick Start (TL;DR)

```bash
# 1. Setup
cd /home/mike/therapy_robot
./setup.sh

# 2. Fix permissions
sudo chmod 666 /dev/spidev0.0

# 3. Run main project
cd /home/mike
source therapy_robot/venv/bin/activate
export GEMINI_API_KEY="YOUR_KEY_HERE"
python -m therapy_robot.main

# 4. Run dashboard (in another terminal)
cd /home/mike/therapy_robot
source venv/bin/activate
python dashboard/web_app.py
```

## 📖 Reading Order

**For first-time setup:**
1. Start with `QUICK_START.md`
2. If you get permission errors → `FIX_PERMISSIONS.md`
3. For main project details → `RUN_MAIN_PROJECT.md`
4. For dashboard details → `RUN_DASHBOARD.md`

**For quick reference:**
- Use `COMMANDS_REFERENCE.md` for copy-paste commands

**For troubleshooting:**
- Check the troubleshooting section in each guide
- See `FIX_PERMISSIONS.md` for permission issues

## 🔗 Related Documentation

- **[README.md](README.md)** - Original quick start guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview and features
- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Dashboard features
- **[WEB_DASHBOARD_GUIDE.md](WEB_DASHBOARD_GUIDE.md)** - Web dashboard details

## 📝 File Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `QUICK_START.md` | Complete setup guide | First time setup |
| `COMMANDS_REFERENCE.md` | All commands | Quick lookup |
| `RUN_MAIN_PROJECT.md` | Main project details | Running main app |
| `RUN_DASHBOARD.md` | Dashboard details | Running dashboard |
| `FIX_PERMISSIONS.md` | Permission fixes | Hardware errors |

## 🆘 Need Help?

1. **Permission errors?** → See `FIX_PERMISSIONS.md`
2. **Module not found?** → See `RUN_MAIN_PROJECT.md` (run from `/home/mike`)
3. **Dashboard not working?** → See `RUN_DASHBOARD.md`
4. **General issues?** → See `QUICK_START.md` troubleshooting section

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list`)
- [ ] SPI permissions fixed (`ls -l /dev/spidev0.0`)
- [ ] GPIO permissions fixed (`groups | grep gpio`)
- [ ] API key set (`echo $GEMINI_API_KEY`)
- [ ] Main project runs without errors
- [ ] Dashboard accessible at `http://localhost:5000`
- [ ] Hardware initializes correctly (check startup messages)

---

**Last Updated:** December 2025  
**Project:** Therapy Robot  
**Location:** `/home/mike/therapy_robot`

