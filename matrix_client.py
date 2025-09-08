import os
from nio import AsyncClient, LoginResponse, RoomSendResponse


class MatrixClient:
    """Matrix client using matrix-nio for sending messages."""

    def __init__(self, homeserver_url: str, username: str, password: str, room_id: str):
        self.homeserver_url = homeserver_url
        self.username = username
        self.password = password
        self.room_id = room_id

        if not all([self.homeserver_url, self.username, self.password, self.room_id]):
            raise ValueError("Matrix configuration incomplete. Required: homeserver_url, username, password, room_id")

        # Ensure the homeserver URL has the correct format
        if not self.homeserver_url.startswith(('http://', 'https://')):
            self.homeserver_url = f"https://{self.homeserver_url}"

    async def send_message(self, message: str) -> dict:
        """Send a text message to the configured Matrix room."""
        client = None
        try:
            # Create the client
            client = AsyncClient(self.homeserver_url, self.username)

            # Login with username and password
            login_response = await client.login(self.password)

            if not isinstance(login_response, LoginResponse):
                return {
                    "status": "error",
                    "message": f"Failed to login to Matrix: {login_response.message if hasattr(login_response, 'message') else str(login_response)}"
                }

            # Send the message
            response = await client.room_send(
                room_id=self.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message
                }
            )

            # Check if the message was sent successfully
            if isinstance(response, RoomSendResponse):
                return {
                    "status": "success",
                    "message": "Matrix message sent successfully",
                    "event_id": response.event_id
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to send Matrix message: {response.message if hasattr(response, 'message') else str(response)}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send Matrix message: {str(e)}"
            }
        finally:
            # Always close the client if it was created
            if client:
                await client.close()
