from fastmcp import FastMCP
from typing import Annotated
import aiohttp
import os

HA_URL = os.getenv("HA_URL", "http://localhost:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
HA_NOTIFY_SERVICE = os.getenv("HA_NOTIFY_SERVICE", "mobile_app_phone")

mcp = FastMCP("HA Memory")


@mcp.tool
async def notify_user(
        message_title: Annotated[str, "The title of the message"],
        message_content: Annotated[str, "The content of the message"],
):
    """Send a notification to the user"""

    if not HA_TOKEN:
        raise ValueError("HA_TOKEN environment variable is required")

    api_url = f"{HA_URL}/api/services/notify/{HA_NOTIFY_SERVICE}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": message_title,
        "message": message_content
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return {"status": "success", "message": "Notification sent successfully"}
                else:
                    error_text = await response.text()
                    return {"status": "error", "message": f"Failed to send notification: {response.status} - {error_text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error sending notification: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8100)
