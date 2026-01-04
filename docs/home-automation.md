# Home Automation Integration

> Smart home control via Home Assistant and MQTT

## Overview

J.A.R.V.I.S. integrates with Home Assistant for comprehensive smart home control. It also supports direct MQTT communication for IoT devices.

## Setup

### Home Assistant

1. **Generate Long-Lived Access Token:**
   - Go to your Home Assistant profile
   - Scroll to "Long-Lived Access Tokens"
   - Create token, copy immediately

2. **Configure J.A.R.V.I.S.:**

   Via environment:
   ```bash
   HOME_ASSISTANT__ENABLED=true
   HOME_ASSISTANT__URL=http://homeassistant.local:8123
   HOME_ASSISTANT__TOKEN=your_token_here
   ```

   Or via Web UI at `http://localhost:8080`

3. **Test Connection:**
   - Use the "Test Connection" button in Web UI
   - Or via API: `POST /api/test-connection`

### MQTT (Optional)

```bash
MQTT__ENABLED=true
MQTT__HOST=localhost
MQTT__PORT=1883
MQTT__USERNAME=user
MQTT__PASSWORD=pass
```

## Supported Devices

### Lights

| Command | Example Voice | Code |
|---------|---------------|------|
| Turn on | "Turn on the kitchen light" | `await home.turn_on("kitchen light")` |
| Turn off | "Turn off the lights" | `await home.turn_off("lights")` |
| Brightness | "Set bedroom to 50%" | `await home.set_brightness("bedroom", 50)` |
| Color | "Make it blue" | `await home.set_color("light", "blue")` |

**Supported Colors:**
- red, green, blue, yellow, purple, orange, pink, white, warm, cool
- RGB tuples: `(255, 100, 50)`

```python
# Examples
await home.turn_on("living room", brightness=75)
await home.set_color("accent light", "warm")
await home.set_color("party light", (255, 0, 128))  # RGB
```

---

### Locks

| Command | Example Voice | Code |
|---------|---------------|------|
| Lock | "Lock the front door" | `await home.lock("front door")` |
| Unlock | "Unlock the garage" | `await home.unlock("garage")` |

```python
await home.lock("front door")
await home.unlock("back door")
```

---

### Climate/Thermostat

| Command | Example Voice | Code |
|---------|---------------|------|
| Set temp | "Set temperature to 72" | `await home.set_temperature("thermostat", 72)` |
| Mode | "Turn on heating" | `await home.set_hvac_mode("thermostat", "heat")` |
| Status | "What's the temperature?" | `await home.get_temperature("thermostat")` |

**HVAC Modes:** `heat`, `cool`, `auto`, `off`

```python
# Set to 72°F
await home.set_temperature("living room", 72)

# Cool mode
await home.set_hvac_mode("thermostat", "cool")

# Get current state
state = await home.get_temperature("thermostat")
# {"current_temperature": 74, "target_temperature": 72, "hvac_mode": "cool"}
```

---

### Media Players

| Command | Example Voice | Code |
|---------|---------------|------|
| Play | "Play music" | `await home.media_play("speaker")` |
| Pause | "Pause" | `await home.media_pause("speaker")` |
| Stop | "Stop playback" | `await home.media_stop("speaker")` |
| Next | "Skip song" | `await home.media_next("speaker")` |
| Previous | "Previous track" | `await home.media_previous("speaker")` |
| Volume | "Volume to 50" | `await home.set_volume("speaker", 50)` |

```python
await home.media_play("living room speaker")
await home.set_volume("living room speaker", 60)
await home.media_next("living room speaker")
```

---

### Covers (Blinds, Garage Doors)

| Command | Example Voice | Code |
|---------|---------------|------|
| Open | "Open the blinds" | `await home.open_cover("blinds")` |
| Close | "Close garage" | `await home.close_cover("garage door")` |
| Position | "Set blinds to 50%" | `await home.set_cover_position("blinds", 50)` |

```python
await home.open_cover("bedroom blinds")
await home.set_cover_position("office blinds", 30)  # 30% open
await home.close_cover("garage door")
```

---

### Scenes

| Command | Example Voice | Code |
|---------|---------------|------|
| Activate | "Activate movie night" | `await home.activate_scene("movie night")` |

```python
await home.activate_scene("Movie Night")
await home.activate_scene("Good Morning")
await home.activate_scene("scene.away_mode")  # By entity_id
```

---

### Vacuums

| Command | Example Voice | Code |
|---------|---------------|------|
| Start | "Start vacuuming" | `await home.vacuum_start("vacuum")` |
| Stop | "Stop the vacuum" | `await home.vacuum_stop("vacuum")` |
| Dock | "Send vacuum home" | `await home.vacuum_return_home("vacuum")` |

```python
await home.vacuum_start("roomba")
await home.vacuum_return_home("roomba")
```

---

### Automations & Scripts

```python
# Trigger automation
await home.trigger_automation("motion_lights")

# Run script
await home.run_script("bedtime_routine")
```

## Device Discovery

### Fuzzy Matching

J.A.R.V.I.S. uses fuzzy matching to find devices:

```python
# All of these find "Living Room Ceiling Light"
await home.get_device("living room light")
await home.get_device("living room")
await home.get_device("ceiling light")
await home.get_device("Living Room Ceiling Light")  # Exact
await home.get_device("light.living_room_ceiling")  # Entity ID
```

### By Type

```python
from home.automation import DeviceType

# Get all lights
lights = await home.get_devices_by_type(DeviceType.LIGHT)

# Get all thermostats
thermostats = await home.get_devices_by_type(DeviceType.THERMOSTAT)
```

### By Area

```python
# Get devices in living room
devices = await home.get_devices_by_area("living room")
```

## State Summary

Get an overview of your home:

```python
summary = await home.get_state_summary()
# {
#     "lights": {"on": 3, "total": 12},
#     "locks": {"locked": 2, "total": 2},
#     "thermostat": {
#         "current": 74,
#         "target": 72,
#         "mode": "cool"
#     },
#     "total_devices": 45
# }
```

## MQTT Direct Control

For devices not in Home Assistant:

```python
# Connect
await home.connect_mqtt()

# Publish
await home.publish_mqtt("zigbee/light/set", '{"state": "ON", "brightness": 200}')

# Subscribe
messages = await home.subscribe_mqtt("zigbee/sensors/#")
async for msg in messages:
    print(f"{msg.topic}: {msg.payload}")
```

## Voice Command Examples

These natural language commands are understood:

**Lights:**
- "Turn on the living room lights"
- "Dim the bedroom"
- "Set the kitchen to 50 percent"
- "Make the accent light blue"

**Climate:**
- "Set the temperature to 72"
- "Turn on the AC"
- "What's the temperature?"

**Media:**
- "Play music in the kitchen"
- "Pause the living room"
- "Turn up the volume"

**Scenes:**
- "Activate movie night"
- "Set the scene for dinner"

**General:**
- "Lock all the doors"
- "Close all the blinds"
- "What's the status of the house?"

## Error Handling

```python
try:
    await home.turn_on("nonexistent light")
except ValueError as e:
    print(f"Device not found: {e}")

try:
    await home.call_service("light", "turn_on", "light.foo")
except aiohttp.ClientResponseError as e:
    print(f"Home Assistant error: {e.status}")
```

## Best Practices

1. **Refresh devices periodically:**
   ```python
   # Refresh every 5 minutes
   await home.refresh_devices()
   ```

2. **Use areas for group control:**
   ```python
   for device in await home.get_devices_by_area("bedroom"):
       await home.turn_off(device)
   ```

3. **Create scenes for complex states:**
   Instead of multiple commands, use Home Assistant scenes.

4. **Test connections on startup:**
   ```python
   try:
       await home.refresh_devices()
       print(f"Connected: {len(home._devices)} devices")
   except Exception as e:
       print(f"Home Assistant unavailable: {e}")
   ```
