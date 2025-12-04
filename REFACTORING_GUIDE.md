# Therapy Robot Refactoring Guide

This document outlines the refactoring changes needed to complete all 4 tasks.

## Task 1: Central Config Module ✅

**Status**: COMPLETED

- Created `config.py` with all constants
- All pins, thresholds, paths centralized
- Environment variable support added

**Next Steps**: Update all modules to import from config (in progress)

## Task 2: Hardware Simulation Mode ✅

**Status**: COMPLETED (structure), NEEDS INTEGRATION

- Created `simulation.py` with simulated hardware classes
- SimulatedLED, SimulatedPhotoresistor, SimulatedJoystick, SimulatedRotaryEncoder, SimulatedFallDetector implemented

**Next Steps**: 
- Complete hardware module refactoring to use config + simulation
- Update each module to check `config.USE_SIMULATION` and use appropriate class

## Task 3: AI Rate Limiting

**Status**: PENDING

**Implementation Plan**:
1. Add threading.Lock for thread safety
2. Store last_request_timestamp and last_emotion_result
3. Check cache before calling Gemini API
4. Respect `config.GEMINI_EMOTION_CACHE_SECONDS`

## Task 4: Mental Health Analyzer Extensions

**Status**: PENDING

**Implementation Plan**:
1. Add trend classification function (improving/stable/declining)
2. Add daily summary context builder
3. Add Gemini API function for daily summary generation
4. Add dashboard endpoint `/api/mental-health/daily-summary`
5. Update dashboard UI to show daily summary

## Implementation Notes

All modules should use imports like:
```python
try:
    from therapy_robot import config
    from therapy_robot import simulation
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import config
    import simulation
```

For hardware modules, use pattern:
```python
if config.USE_SIMULATION:
    ControllerClass = simulation.SimulatedController
else:
    ControllerClass = RealController

# Export the appropriate class
Controller = ControllerClass
```

