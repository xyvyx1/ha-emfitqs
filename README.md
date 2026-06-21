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

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
 This repository is part of the default HACS store. Search for the "Emfit QS Sleep Tracker" component in HACS and install it from there.

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
| bed_presence | `binary_sensor` | Bed presence |
| heart_rate | `sensor` | Heart rate (BPM) |
| respiratory_rate | `sensor` | Respiratory rate (BPM) |
| activity_level | `sensor` | Activity level |
| seconds_in_bed | `sensor` | Number of seconds in bed |
