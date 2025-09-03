import datetime

import pytz
from fastmcp import FastMCP
from typing import Annotated
import aiohttp
import os

HA_URL = os.getenv("HA_URL", "http://localhost:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
HA_NOTIFY_SERVICE = os.getenv("HA_NOTIFY_SERVICE", "mobile_app_phone")
HA_DEVICE_TRACKER_ENTITY = os.getenv("HA_DEVICE_TRACKER_ENTITY", "device_tracker.phone")

mcp = FastMCP("HA Tasker MCP Extensions")


@mcp.tool
async def get_current_time_for_user() -> str:
    """Get the current date and time in the user's timezone in ISO format"""
    timezone = pytz.timezone('Europe/Berlin')
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
        message_title: Annotated[str, "The title of the message"],
        message_content: Annotated[str, "The content of the message"],
):
    """Send a notification to the user"""
    payload = {
        "title": message_title,
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


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8100)
