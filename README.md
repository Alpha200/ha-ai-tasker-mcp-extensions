# Home Assistant AI Tasker MCP Extensions

This project provides MCP (Model Context Protocol) extensions for integrating with Home Assistant, allowing AI assistants to interact with your smart home devices and services.

## Features

The following MCP tools are available:

### 🕒 Time Management
- **get_current_time_for_user**: Get the current date and time in the user's configured timezone in ISO format

### 📍 Location Services  
- **get_current_geofence_for_user**: Fetch the current geofence (zone) of the user from Home Assistant via the device tracker entity

### 🌤️ Weather Services
- **get_weather_forecast_24h**: Fetch the weather forecast for the next 24 hours from Home Assistant. Returns hourly forecast data with datetime, condition, temperature (°C), and wind speed (km/h)

### 📅 Calendar Services
- **get_calendar_events_48h**: Fetch calendar events for the next 48 hours from Home Assistant. Returns event details including start/end times, summary, description, and location

### 📱 Notifications
- **notify_user**: Send notifications to the user via Home Assistant or Matrix (configurable)

## Environment Variables

Configure the following environment variables:

| Variable                   | Description                            | Default Value            |
|----------------------------|----------------------------------------|--------------------------|
| `HA_URL`                   | Home Assistant base URL                | `http://localhost:8123`  |
| `HA_TOKEN`                 | Home Assistant long-lived access token | Required for HA features |
| `HA_NOTIFY_SERVICE`        | Notification service name              | `mobile_app_phone`       |
| `HA_DEVICE_TRACKER_ENTITY` | Device tracker entity ID               | `device_tracker.phone`   |
| `HA_WEATHER_ENTITY`        | Weather entity ID                      | `weather.forecast_home`  |
| `HA_CALENDAR_ENTITY`       | Calendar entity ID                     | `calendar.personal`      |
| `HA_TIMEZONE`              | Timezone for time calculations         | `Europe/Berlin`          |
| `NOTIFICATION_METHOD`      | Notification method                    | `homeassistant`          |

### Matrix Configuration (when NOTIFICATION_METHOD=matrix)

| Variable                | Description                              | Required |
|-------------------------|------------------------------------------|----------|
| `MATRIX_HOMESERVER_URL` | Matrix homeserver URL (e.g., matrix.org) | Yes      |
| `MATRIX_USERNAME`       | Matrix bot username                      | Yes      |
| `MATRIX_PASSWORD`       | Matrix bot password                      | Yes      |
| `MATRIX_ROOM_ID`        | Matrix room ID to send messages to       | Yes      |

## Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up your environment variables in a `.env` file or export them directly

3. Run the MCP server:
   ```bash
   python main.py
   ```

The server will start on `http://0.0.0.0:8100` using Server-Sent Events (SSE) transport.

## Home Assistant Configuration

Ensure you have the following entities configured in your Home Assistant:

- A weather integration providing hourly forecasts
- A calendar integration for event management
- A device tracker for location services
- A notification service for mobile alerts (if using Home Assistant notifications)

## Matrix Configuration

To use Matrix for notifications instead of Home Assistant:

1. Set `NOTIFICATION_METHOD=matrix`
2. Configure the Matrix environment variables:
   - `MATRIX_HOMESERVER_URL`: Your Matrix homeserver (e.g., `matrix.org` or `https://matrix.example.com`)
   - `MATRIX_USERNAME`: Your Matrix bot username (e.g., `@botname:matrix.org`)
   - `MATRIX_PASSWORD`: Your Matrix bot password
   - `MATRIX_ROOM_ID`: The room ID where notifications should be sent (e.g., `!roomid:matrix.org`)

The application will automatically fall back to Home Assistant notifications if Matrix configuration is incomplete or fails.

## API Details

### Weather Forecast Response

The weather forecast tool returns 24 hours of hourly forecast data with:
- **datetime**: ISO timestamp for each forecast hour
- **condition**: Weather condition (sunny, partlycloudy, cloudy, rainy, etc.)
- **temperature**: Temperature in Celsius (°C)
- **wind_speed**: Wind speed in km/h
- **status**: Success/error status and forecast count

### Calendar Events Response

The calendar events tool returns events for the next 48 hours with:
- **start**: Event start datetime (ISO format)
- **end**: Event end datetime (ISO format)
- **summary**: Event title/summary
- **description**: Event description (if available)
- **location**: Event location (if available)
- **status**: Success/error status, event count, and time range

### Geofence Response

Returns the current zone/location of the tracked device, or "on the way" if between zones.

### Notification Response

Provides success/error status for sent notifications. Supports both Home Assistant and Matrix messaging based on configuration.
