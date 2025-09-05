# Home Assistant AI Tasker MCP Extensions

This project provides MCP (Model Context Protocol) extensions for integrating with Home Assistant, allowing AI assistants to interact with your smart home devices and services.

## Features

The following MCP tools are available:

### 🕒 Time Management
- **get_current_time_for_user**: Get the current date and time in the user's timezone (Europe/Berlin) in ISO format

### 📍 Location Services  
- **get_current_geofence_for_user**: Fetch the current geofence (zone) of the user from Home Assistant via the device tracker entity

### 🌤️ Weather Services
- **get_weather_forecast_24h**: Fetch the weather forecast for the next 24 hours from Home Assistant. Returns hourly forecast data with datetime, condition, temperature (°C), and wind speed (km/h)

### 📱 Notifications
- **notify_user**: Send notifications to the user's mobile device through Home Assistant

## Environment Variables

Configure the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `HA_URL` | Home Assistant base URL | `http://localhost:8123` |
| `HA_TOKEN` | Home Assistant long-lived access token | Required |
| `HA_NOTIFY_SERVICE` | Notification service name | `mobile_app_phone` |
| `HA_DEVICE_TRACKER_ENTITY` | Device tracker entity ID | `device_tracker.phone` |
| `HA_WEATHER_ENTITY` | Weather entity ID | `weather.forecast_home` |

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
- A device tracker for location services
- A notification service for mobile alerts

## API Details

### Weather Forecast Response

The weather forecast tool returns 24 hours of hourly forecast data with:
- **datetime**: ISO timestamp for each forecast hour
- **condition**: Weather condition (sunny, partlycloudy, cloudy, rainy, etc.)
- **temperature**: Temperature in Celsius (°C)
- **wind_speed**: Wind speed in km/h
- **status**: Success/error status and forecast count

### Geofence Response

Returns the current zone/location of the tracked device, or "on the way" if between zones.

### Notification Response

Provides success/error status for sent notifications.
