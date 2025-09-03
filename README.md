# HA AI Tasker MCP Extensions

A FastMCP server that provides Home Assistant integration tools for AI assistants.

## Features

- **User Notifications**: Send notifications to mobile devices through Home Assistant's notify service
- **Current Time**: Get the current date and time in the user's timezone
- **Current Geofence**: Fetch the user's current geofence (zone) from Home Assistant via a device tracker entity

## Setup

### Environment Variables

Set the following environment variables before running:

- `HA_TOKEN`: Your Home Assistant long-lived access token (**required**)
- `HA_URL`: Your Home Assistant URL (default: `http://localhost:8123`)
- `HA_NOTIFY_SERVICE`: The notify service name (default: `mobile_app_phone`)
- `HA_DEVICE_TRACKER_ENTITY`: The device tracker entity ID to use for geofence queries (default: `device_tracker.phone`)

## Installation

```bash
poetry install
```

## Running

```bash
python main.py
```

The server will start on `http://0.0.0.0:8100` using Server-Sent Events (SSE) transport.

## Tools

### notify_user
Sends a notification to the user's mobile phone via Home Assistant.

**Parameters:**
- `message_title`: The title of the message
- `message_content`: The content of the message

**Returns:**
- Success: `{"status": "success", "message": "Notification sent successfully"}`
- Error: `{"status": "error", "message": "Error description"}`

### get_current_time_for_user
Returns the current date and time in the user's timezone (Europe/Berlin) in ISO format.

### get_current_geofence_for_user
Fetches the current geofence (zone) of the user from Home Assistant using the configured device tracker entity.

**Parameters:**
- None

**Returns:**
- The current geofence/zone as a string (e.g., `home`, `work`, `not_home`, or `on the way`)
- If the entity is not found: `Entity '<entity_id>' not found in Home Assistant.`
- On error: `Failed to fetch geofence: <status> - <error>`

## Home Assistant Setup

Make sure you have:
1. A long-lived access token created in Home Assistant
2. The mobile app integration set up for your device
3. The correct notify service name (check in Developer Tools → Services)
