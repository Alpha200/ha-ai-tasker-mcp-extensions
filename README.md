# HA AI Tasker MCP Extensions

A FastMCP server that provides Home Assistant integration tools for AI assistants.

## Features

- **User Notifications**: Send notifications to mobile devices through Home Assistant's notify service

## Setup

### Environment Variables

Set the following environment variables:

- `HA_TOKEN`: Your Home Assistant long-lived access token (required)
- `HA_URL`: Your Home Assistant URL (default: `http://localhost:8123`)
- `HA_NOTIFY_SERVICE`: The notify service name (default: `mobile_app_phone`)

### Installation

```bash
poetry install
```

### Running

```bash
python main.py
```

The server will start on `http://0.0.0.0:8100` using Server-Sent Events (SSE) transport.

## Usage

### notify_user Tool

Sends a notification to the user's mobile phone via Home Assistant.

**Parameters:**
- `message_title`: The title of the message
- `message_content`: The content of the message

**Returns:**
- Success: `{"status": "success", "message": "Notification sent successfully"}`
- Error: `{"status": "error", "message": "Error description"}`

## Home Assistant Setup

Make sure you have:
1. A long-lived access token created in Home Assistant
2. The mobile app integration set up for your device
3. The correct notify service name (check in Developer Tools → Services)
