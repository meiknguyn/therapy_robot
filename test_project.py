#!/usr/bin/env python3
"""Comprehensive test script for Therapy Robot project."""

import sys
import os
import time
from pathlib import Path

# Add project root to path (parent directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Therapy Robot - Component Test Suite")
print("=" * 60)
print()

# Track test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test(name, func):
    """Run a test and track results."""
    print(f"\n[TEST] {name}")
    print("-" * 60)
    try:
        result = func()
        if result is True or result is None:
            print(f"✓ PASSED: {name}")
            results["passed"].append(name)
        elif isinstance(result, str) and result.startswith("WARN"):
            print(f"⚠ WARNING: {name} - {result[4:]}")
            results["warnings"].append(f"{name}: {result[4:]}")
        else:
            print(f"✗ FAILED: {name}")
            results["failed"].append(name)
    except Exception as e:
        print(f"✗ FAILED: {name} - {type(e).__name__}: {e}")
        results["failed"].append(f"{name}: {e}")
    print()

# Test 1: Configuration
def test_config():
    """Test configuration module."""
    try:
        from therapy_robot import config
        assert hasattr(config, 'BASE_DIR')
        assert hasattr(config, 'LED_PIN')
        assert hasattr(config, 'SPI_DEVICE')
        assert hasattr(config, 'GEMINI_MODEL')
        print(f"  BASE_DIR: {config.BASE_DIR}")
        print(f"  LED_PIN: {config.LED_PIN}")
        print(f"  SPI_DEVICE: {config.SPI_DEVICE}")
        print(f"  GEMINI_MODEL: {config.GEMINI_MODEL}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Test 2: Imports
def test_imports():
    """Test that all modules can be imported."""
    modules = [
        'therapy_robot.config',
        'therapy_robot.ai.gemini_client',
        'therapy_robot.audio.speaker',
        'therapy_robot.hardware.led_ctrl',
        'therapy_robot.hardware.photoresistor',
        'therapy_robot.dashboard.csv_logger',
    ]
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            return False
    return True

# Test 3: Gemini API Key
def test_gemini_key():
    """Test Gemini API key configuration."""
    from therapy_robot import config
    if config.GEMINI_API_KEY:
        print(f"  API Key: {config.GEMINI_API_KEY[:10]}...{config.GEMINI_API_KEY[-4:]}")
        return True
    else:
        print("  API Key: NOT SET")
        print("  Set with: export GEMINI_API_KEY='your_key_here'")
        return "WARN: Gemini API key not set (some features will not work)"

# Test 4: Directories
def test_directories():
    """Test that required directories exist."""
    from therapy_robot import config
    dirs = [
        config.LOG_DIR,
        config.MUSIC_DIR,
        config.PROOFS_DIR,
    ]
    for dir_path in dirs:
        if dir_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (missing)")
            return False
    return True

# Test 5: LED Controller (hardware)
def test_led():
    """Test LED controller initialization."""
    try:
        from therapy_robot.hardware.led_ctrl import LEDController
        led = LEDController()
        print("  LED controller initialized (gpiod)")
        
        # Test on/off
        led.on()
        print("  LED turned ON")
        time.sleep(0.3)
        
        led.off()
        print("  LED turned OFF")
        time.sleep(0.3)
        
        # Test brightness setting
        led.set_brightness(0.3)
        print("  Set brightness to 0.3")
        time.sleep(0.5)
        
        led.set_brightness(0.7)
        print("  Set brightness to 0.7")
        time.sleep(0.5)
        
        # Test breathing animation
        led.breathing_start()
        print("  Started breathing animation")
        time.sleep(2.0)  # Let it breathe for 2 seconds
        
        led.breathing_stop()
        print("  Stopped breathing animation")
        
        led.off()
        print("  Turned off LED")
        
        led.close()
        return True
    except PermissionError as e:
        print(f"  Permission error: {e}")
        print("  Try: sudo usermod -a -G gpio $USER")
        return "WARN: LED access denied (check GPIO permissions)"
    except FileNotFoundError as e:
        print(f"  Device not found: {e}")
        print("  Check that /dev/gpiochip2 exists")
        return "WARN: GPIO chip not found"
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 6: Photoresistor (SPI/ADC)
def test_photoresistor():
    """Test photoresistor reading via SPI."""
    try:
        from therapy_robot.hardware.photoresistor import Photoresistor
        ldr = Photoresistor()
        print("  Photoresistor initialized")
        
        # Read a few values
        for i in range(3):
            value = ldr.read_normalized()
            print(f"  Reading {i+1}: {value:.3f} (normalized)")
            time.sleep(0.2)
        
        ldr.close()
        return True
    except PermissionError as e:
        print(f"  Permission error: {e}")
        print("  Try: sudo usermod -a -G spi $USER")
        return "WARN: SPI access denied (check SPI permissions)"
    except FileNotFoundError as e:
        print(f"  Device not found: {e}")
        return "WARN: SPI device not available"
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Test 7: Gemini Client (without API call)
def test_gemini_client():
    """Test Gemini client initialization."""
    try:
        from therapy_robot.ai import gemini_client
        from therapy_robot import config
        
        if not config.GEMINI_API_KEY:
            return "WARN: Cannot test Gemini client without API key"
        
        # Test emotion analysis (keyword-based, doesn't need API)
        result = gemini_client.analyze_emotion_with_cache("I feel happy today!")
        print(f"  Emotion analysis test: score={result['score']}/10")
        assert 'score' in result
        assert 'raw_text' in result
        assert 1 <= result['score'] <= 10
        
        # Test cache
        result2 = gemini_client.analyze_emotion_with_cache("I feel happy today!")
        print(f"  Cache test: same result = {result == result2}")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Test 8: CSV Logger
def test_csv_logger():
    """Test CSV logging functionality."""
    try:
        from therapy_robot.dashboard import csv_logger
        from therapy_robot import config
        
        # Test event logging
        csv_logger.log_event("test_event", {"test": "value", "number": 42})
        print("  Event logged successfully")
        
        # Test chat logging
        csv_logger.log_chat("Test message", 5, "Test response")
        print("  Chat logged successfully")
        
        # Check if files exist
        if config.EVENT_LOG_PATH.exists():
            print(f"  Event log: {config.EVENT_LOG_PATH} ({config.EVENT_LOG_PATH.stat().st_size} bytes)")
        else:
            print(f"  Event log: {config.EVENT_LOG_PATH} (not created yet)")
        
        if config.CHAT_LOG_PATH.exists():
            print(f"  Chat log: {config.CHAT_LOG_PATH} ({config.CHAT_LOG_PATH.stat().st_size} bytes)")
        else:
            print(f"  Chat log: {config.CHAT_LOG_PATH} (not created yet)")
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Test 9: Audio/Speaker
def test_audio():
    """Test audio module."""
    try:
        from therapy_robot.audio import speaker
        from therapy_robot import config
        
        # Check if music file exists
        music_file = config.MUSIC_DIR / "calm.wav"
        if music_file.exists():
            print(f"  Music file found: {music_file}")
            print("  (Skipping actual playback test to avoid blocking)")
            return True
        else:
            print(f"  Music file not found: {music_file}")
            return "WARN: Music file not found (optional)"
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Test 10: Hardware permissions
def test_permissions():
    """Test hardware device permissions."""
    issues = []
    
    # Check SPI
    spi_path = Path("/dev/spidev0.0")
    if spi_path.exists():
        stat = spi_path.stat()
        if oct(stat.st_mode)[-3:] != "666" and oct(stat.st_mode)[-3:] != "664":
            issues.append(f"SPI device permissions: {oct(stat.st_mode)[-3:]}")
    else:
        issues.append("SPI device not found")
    
    # Check GPIO
    gpio_paths = [Path(f"/dev/gpiochip{i}") for i in range(3)]
    for gpio_path in gpio_paths:
        if gpio_path.exists():
            stat = gpio_path.stat()
            print(f"  {gpio_path}: permissions {oct(stat.st_mode)[-3:]}")
    
    if issues:
        print("  Issues found:")
        for issue in issues:
            print(f"    - {issue}")
        return "WARN: Some permission issues detected"
    else:
        print("  All device permissions look OK")
        return True

# Run all tests
print("\nRunning tests...\n")

test("Configuration Module", test_config)
test("Module Imports", test_imports)
test("Gemini API Key", test_gemini_key)
test("Directory Structure", test_directories)
test("LED Controller", test_led)
test("Photoresistor (SPI/ADC)", test_photoresistor)
test("Gemini Client", test_gemini_client)
test("CSV Logger", test_csv_logger)
test("Audio Module", test_audio)
test("Hardware Permissions", test_permissions)

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"✓ Passed: {len(results['passed'])}")
print(f"⚠ Warnings: {len(results['warnings'])}")
print(f"✗ Failed: {len(results['failed'])}")

if results['failed']:
    print("\nFailed tests:")
    for item in results['failed']:
        print(f"  - {item}")

if results['warnings']:
    print("\nWarnings:")
    for item in results['warnings']:
        print(f"  - {item}")

print("\n" + "=" * 60)
if len(results['failed']) == 0:
    print("✓ All critical tests passed!")
    if results['warnings']:
        print("⚠ Some optional features may not work (see warnings above)")
    sys.exit(0)
else:
    print("✗ Some tests failed. Please review the errors above.")
    sys.exit(1)

