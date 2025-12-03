# Fixing Hardware Permissions

Complete guide to fix permission denied errors for hardware access.

## Quick Fix (Temporary)

```bash
sudo chmod 666 /dev/spidev0.0
```

This makes the SPI device readable/writable by all users. **Note:** This resets after reboot.

## Understanding the Errors

### SPI Permission Errors

Affects:
- **Photoresistor** (ambient light detection)
- **Accelerometer** (motion/fall detection)
- **Joystick** (volume control)

Error message:
```
⚠ Photoresistor unavailable: [Errno 13] Permission denied
⚠ Accelerometer unavailable: [Errno 13] Permission denied
⚠ Joystick unavailable: [Errno 13] Permission denied
```

Device: `/dev/spidev0.0`

### GPIO Permission Errors

Affects:
- **LED Controller** (visual feedback)
- **Rotary Button** (alarm control)

Error message:
```
⚠ LED controller unavailable: [Errno 13] Permission denied
⚠ Rotary button unavailable: [Errno 13] Permission denied
```

Device: `/dev/gpiochip2` (or other gpiochip devices)

## Check Current Status

### Check Your Groups

```bash
groups
```

You should see `spi` and `gpio` in the list if permissions are set up correctly.

### Check Device Permissions

```bash
# Check SPI device
ls -l /dev/spidev0.0

# Check GPIO device
ls -l /dev/gpiochip2
```

**Expected permissions:**
- SPI: `crw-rw-rw-` (666) or `crw-rw----` (664) with spi group
- GPIO: `crw-rw----` (664) with gpio group

## Fix SPI Permissions

### Method 1: Quick Fix (Temporary - Resets on Reboot)

```bash
sudo chmod 666 /dev/spidev0.0
```

**Pros:** Immediate, no logout required  
**Cons:** Resets after reboot, less secure

### Method 2: Create SPI Group (Persistent)

```bash
# Create spi group (if it doesn't exist)
sudo groupadd spi

# Add your user to spi group
sudo usermod -a -G spi $USER

# Change SPI device group ownership
sudo chgrp spi /dev/spidev0.0

# Set group read/write permissions
sudo chmod 664 /dev/spidev0.0

# Activate new group (or logout/login)
newgrp spi
```

**Pros:** Persistent, more secure  
**Cons:** Requires logout/login or newgrp

**Verify:**
```bash
groups | grep spi
ls -l /dev/spidev0.0
```

Should show `spi` in groups and `crw-rw----` permissions.

### Method 3: Udev Rule (Most Permanent - Survives Reboots)

```bash
# Create udev rule file
sudo bash -c 'echo "KERNEL==\"spidev0.0\", MODE=\"0666\"" > /etc/udev/rules.d/99-spi-permissions.rules'

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Pros:** Most permanent, survives reboots  
**Cons:** Less secure (world-writable)

**Alternative (more secure with group):**
```bash
# Create spi group first
sudo groupadd spi
sudo usermod -a -G spi $USER

# Create udev rule with group
sudo bash -c 'echo "KERNEL==\"spidev0.0\", GROUP=\"spi\", MODE=\"0664\"" > /etc/udev/rules.d/99-spi-permissions.rules'

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Activate group
newgrp spi
```

## Fix GPIO Permissions

### Add User to GPIO Group

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Activate group (or logout/login)
newgrp gpio
```

**Verify:**
```bash
groups | grep gpio
ls -l /dev/gpiochip2
```

Should show `gpio` in groups and `crw-rw----` permissions.

### If GPIO Group Doesn't Exist

```bash
# Create gpio group
sudo groupadd gpio

# Add user to gpio group
sudo usermod -a -G gpio $USER

# Change GPIO device group ownership
sudo chgrp gpio /dev/gpiochip2
sudo chmod 664 /dev/gpiochip2

# Activate group
newgrp gpio
```

## Complete Setup Script

Run this to set up all permissions:

```bash
#!/bin/bash

# Create groups
sudo groupadd spi 2>/dev/null || true
sudo groupadd gpio 2>/dev/null || true

# Add user to groups
sudo usermod -a -G spi $USER
sudo usermod -a -G gpio $USER

# Fix SPI permissions
sudo chgrp spi /dev/spidev0.0 2>/dev/null || true
sudo chmod 664 /dev/spidev0.0 2>/dev/null || true

# Create udev rule for SPI (persistent)
sudo bash -c 'echo "KERNEL==\"spidev0.0\", GROUP=\"spi\", MODE=\"0664\"" > /etc/udev/rules.d/99-spi-permissions.rules'
sudo udevadm control --reload-rules
sudo udevadm trigger

# Activate groups
newgrp spi
newgrp gpio

echo "Permissions fixed! You may need to logout/login for changes to take full effect."
```

Save as `fix_permissions.sh`, make executable, and run:
```bash
chmod +x fix_permissions.sh
./fix_permissions.sh
```

## Testing Permissions

### Test SPI Access

```bash
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000
print('✓ SPI access successful!')
spi.close()
"
```

### Test GPIO Access

```bash
python3 -c "
import gpiod
chip = gpiod.Chip('/dev/gpiochip2')
print('✓ GPIO access successful!')
chip.close()
"
```

### Test Full Hardware

```bash
cd /home/mike
source therapy_robot/venv/bin/activate
python therapy_robot/test_project.py
```

## Troubleshooting

### "newgrp: no such group"

**Cause:** Group doesn't exist yet.

**Solution:** Create the group first:
```bash
sudo groupadd spi
sudo usermod -a -G spi $USER
newgrp spi
```

### "Permission denied" After Adding to Group

**Cause:** Group membership not activated.

**Solution:** 
1. Logout and login again, OR
2. Run `newgrp spi` and `newgrp gpio`, OR
3. Start a new shell session

### Permissions Reset After Reboot

**Cause:** Using temporary fix (chmod 666).

**Solution:** Use udev rule (Method 3) for permanent fix.

### "Operation not permitted"

**Cause:** Need sudo privileges.

**Solution:** Make sure you're using `sudo` for commands that modify system files.

### Still Getting Permission Errors

**Check:**
1. Groups are correct: `groups`
2. Device permissions: `ls -l /dev/spidev0.0`
3. Group ownership: `ls -l /dev/spidev0.0 | grep spi`
4. Activated groups: `id`

**Try:**
```bash
# Logout and login again
# Or restart the system
```

## Verification Checklist

After fixing permissions, verify:

- [ ] User is in `spi` group: `groups | grep spi`
- [ ] User is in `gpio` group: `groups | grep gpio`
- [ ] SPI device has correct permissions: `ls -l /dev/spidev0.0`
- [ ] GPIO device has correct permissions: `ls -l /dev/gpiochip2`
- [ ] Test SPI access works (see Testing section)
- [ ] Test GPIO access works (see Testing section)
- [ ] Main project starts without permission errors

## Next Steps

After fixing permissions:
1. Run the main project: See `RUN_MAIN_PROJECT.md`
2. Run the dashboard: See `RUN_DASHBOARD.md`
3. See `QUICK_START.md` for complete setup

