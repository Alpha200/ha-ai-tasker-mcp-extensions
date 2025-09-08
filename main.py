import datetime

import pytz
from fastmcp import FastMCP
from typing import Annotated
import aiohttp
import os
from matrix_client import MatrixClient

HA_URL = os.getenv("HA_URL", "http://localhost:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
HA_NOTIFY_SERVICE = os.getenv("HA_NOTIFY_SERVICE", "mobile_app_phone")
HA_DEVICE_TRACKER_ENTITY = os.getenv("HA_DEVICE_TRACKER_ENTITY", "device_tracker.phone")
HA_WEATHER_ENTITY = os.getenv("HA_WEATHER_ENTITY", "weather.forecast_home")
HA_CALENDAR_ENTITY = os.getenv("HA_CALENDAR_ENTITY", "calendar.personal")
HA_TIMEZONE = os.getenv("HA_TIMEZONE", "Europe/Berlin")
NOTIFICATION_METHOD = os.getenv("NOTIFICATION_METHOD", "homeassistant")  # "homeassistant" or "matrix"

# Matrix configuration
MATRIX_HOMESERVER_URL = os.getenv("MATRIX_HOMESERVER_URL")
MATRIX_USERNAME = os.getenv("MATRIX_USERNAME")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD")
MATRIX_ROOM_ID = os.getenv("MATRIX_ROOM_ID")

mcp = FastMCP("HA Tasker MCP Extensions")

# Initialize Matrix client if needed
matrix_client = None
if NOTIFICATION_METHOD.lower() == "matrix":
    try:
        matrix_client = MatrixClient(
            homeserver_url=MATRIX_HOMESERVER_URL,
            username=MATRIX_USERNAME,
            password=MATRIX_PASSWORD,
            room_id=MATRIX_ROOM_ID
        )
    except (ValueError, TypeError) as e:
        print(f"Matrix configuration error: {e}")
        print("Falling back to Home Assistant notifications")
        NOTIFICATION_METHOD = "homeassistant"


@mcp.tool
async def get_current_time_for_user() -> str:
    """Get the current date and time in the user's timezone in ISO format"""
    timezone = pytz.timezone(HA_TIMEZONE)
    return datetime.datetime.now(timezone).isoformat()


async def ha_request(method: str, endpoint: str, payload: dict = None) -> dict:
    """Generalized async request to Home Assistant API."""
    if not HA_TOKEN:
        raise ValueError("HA_TOKEN environment variable is required")
    url = f"{HA_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        try:
            if method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    data = await response.json(content_type=None)
                    return {"status": response.status, "data": data}
            elif method.upper() == "POST":
                async with session.post(url, json=payload, headers=headers) as response:
                    data = await response.json(content_type=None)
                    return {"status": response.status, "data": data}
            else:
                return {"status": 405, "data": f"Method {method} not allowed"}
        except Exception as e:
            return {"status": 500, "data": str(e)}


@mcp.tool
async def notify_user(
        message_content: Annotated[str, "The content of the message"],
):
    """Send a notification to the user via Home Assistant or Matrix (based on configuration)"""

    if NOTIFICATION_METHOD.lower() == "matrix" and matrix_client:
        # Use Matrix messaging
        result = await matrix_client.send_message(message_content)
        return result
    else:
        # Use Home Assistant notifications (default)
        if not HA_TOKEN:
            return {"status": "error", "message": "HA_TOKEN not configured for Home Assistant notifications"}

        payload = {
            "message": message_content
        }
        result = await ha_request("POST", f"/api/services/notify/{HA_NOTIFY_SERVICE}", payload)
        if result["status"] == 200:
            return {"status": "success", "message": "Notification sent successfully"}
        else:
            return {"status": "error", "message": f"Failed to send notification: {result['status']} - {result['data']}"}


@mcp.tool
async def get_current_geofence_for_user() -> str:
    """Fetch the current geofence (zone) of the user from Home Assistant via the device tracker entity."""
    entity_id = HA_DEVICE_TRACKER_ENTITY
    result = await ha_request("GET", f"/api/states/{entity_id}")
    if result["status"] == 200:
        geofence = result["data"].get("state", None)
        if geofence is not None:
            return geofence
        else:
            return "on the way"
    elif result["status"] == 404:
        return f"Entity '{entity_id}' not found in Home Assistant."
    else:
        return f"Failed to fetch geofence: {result['status']} - {result['data']}"


@mcp.tool
async def get_weather_forecast_24h() -> dict:
    """Fetch the weather forecast for the next 24 hours.

    Returns hourly forecast data with:
    - datetime: ISO timestamp for each forecast hour
    - condition: weather condition (sunny, partlycloudy, cloudy, rainy, etc.)
    - temperature: temperature in Celsius (°C)
    - wind_speed: wind speed in km/h
    """
    entity_id = HA_WEATHER_ENTITY

    # Get forecast data using the weather.get_forecasts service with return_response parameter
    forecast_payload = {
        "entity_id": entity_id,
        "type": "hourly"
    }
    forecast_result = await ha_request("POST", "/api/services/weather/get_forecasts?return_response", forecast_payload)

    if forecast_result["status"] != 200:
        return {
            "status": "error",
            "message": f"Failed to fetch weather forecast: {forecast_result['status']} - {forecast_result['data']}"
        }

    forecast_data = []
    service_data = forecast_result["data"]

    if "service_response" in service_data and entity_id in service_data["service_response"]:
        entity_data = service_data["service_response"][entity_id]
        if "forecast" in entity_data:
            all_forecasts = entity_data["forecast"]
            limited_forecasts = all_forecasts[:24] if len(all_forecasts) >= 24 else all_forecasts

            for forecast in limited_forecasts:
                forecast_data.append({
                    "datetime": forecast.get("datetime"),
                    "condition": forecast.get("condition"),
                    "temperature": forecast.get("temperature"),
                    "wind_speed": forecast.get("wind_speed")
                })

    return {
        "status": "success",
        "forecast_24h": forecast_data,
        "forecast_count": len(forecast_data)
    }


@mcp.tool
async def get_calendar_events_48h() -> dict:
    """Fetch users calendar events for the next 48 hours.
    If the time component of a calendar entry is missing, it is an all-day event.

    Returns calendar events with:
    - start: Event start datetime
    - end: Event end datetime
    - summary: Event title/summary
    - description: Event description (if available)
    - location: Event location (if available)
    """
    entity_id = HA_CALENDAR_ENTITY

    timezone = pytz.timezone(HA_TIMEZONE)
    now = datetime.datetime.now(timezone)
    end_time = now + datetime.timedelta(hours=48)

    start_time_iso = now.isoformat()
    end_time_iso = end_time.isoformat()

    calendar_payload = {
        "entity_id": entity_id,
        "start_date_time": start_time_iso,
        "end_date_time": end_time_iso
    }
    calendar_result = await ha_request("POST", "/api/services/calendar/get_events?return_response", calendar_payload)

    if calendar_result["status"] != 200:
        return {
            "status": "error",
            "message": f"Failed to fetch calendar events: {calendar_result['status']} - {calendar_result['data']}"
        }

    events_data = []
    service_data = calendar_result["data"]

    if "service_response" in service_data and entity_id in service_data["service_response"]:
        entity_data = service_data["service_response"][entity_id]
        if "events" in entity_data:
            events = entity_data["events"]

            for event in events:
                event_data = {
                    "start": event.get("start"),
                    "end": event.get("end"),
                    "summary": event.get("summary")
                }

                description = event.get("description")
                if description:
                    event_data["description"] = description

                location = event.get("location")
                if location:
                    event_data["location"] = location

                events_data.append(event_data)

    return {
        "status": "success",
        "events": events_data,
    }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8100)
