# Emfit QS Sleep Tracker Component for Home Assistant

This component provides real-time data polled directly from Emfit QS Sleep Tracker devices. Useful for automations based on bed presence and sleep detection (via heart rate bpm levels).

![Sensor Card](https://i.imgur.com/vGzT1Ko.jpg)

**NOTE:** This component has only been tested with Emfit QS firmware version 120.2.2.1.


### Supported Features
* Bed Presence binary sensor
* Time in Bed (seconds)
* Heart Rate BPM sensor
* Respiratory Rate sensor
* Activity Level sensor

**IMPORTANT:** Your Emfit QS device must be accessible by Home Assistant on your local area network.


## Installation

### HACS Installation

This repo is not yet part of the HACS store. 

### Manual Installation

Copy the `custom_components/ha-emfitqs` directory into your `/config/custom_components` directory.


## Component Configuration

1. In Home Assistant, go to **Settings → Devices & Services → Add Integration**.
2. Search for **Emfit QS Sleep Tracker**.
3. Enter:
   - `host`: IP address or hostname of your Emfit QS device
   - `scan_interval`: polling interval in seconds (default 30, minimum 10)

The integration auto-creates all supported entities and groups them under a single Emfit QS device.

### Created Entities

| Name  | Type | Description |
| ----- | ---- | ----------- |
| bed_presence | `occupancy` | Bed presence |
| heart_rate | `sensor` | Heart rate (BPM) |
| respiratory_rate | `sensor` | Respiratory rate (BPM) |
| activity_level | `sensor` | Activity level |
| seconds_in_bed | `sensor` | Number of seconds in bed |
