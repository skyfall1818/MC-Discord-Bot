import MC_discord_bot

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def handle_message():
    # 1. Receive the incoming message
    if request.is_json:
        # Parse the JSON data from the request body into a Python dictionary
        incoming_data = request.get_json()
        received_message = incoming_data.get("message", "No message provided")
        
        # Log the received message (optional)
        print(f"Received message: {received_message}")

        # 2. Process the message and prepare a reply
        reply_message = f"Server received: '{received_message}'. Status: Success."

        # 3. Send the reply
        # Return a JSON response with a status code
        return jsonify({
            "status": "received",
            "reply": reply_message
        }), 200 # 200 OK status code

    else:
        # Handle non-JSON requests
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400 # 400 Bad Request status code

if __name__ == '__main__':
    # Run the server on http://localhost:5000
    app.run(debug=True, port=5000)









'''
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List

app = FastAPI()

# Connection Manager class to handle multiple clients
class ConnectionManager:
    def __init__(self):
        # Use a dictionary for easier lookup if you need to send to specific users (e.g., keyed by user ID)
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    await manager.broadcast(f"User #{user_id} joined the chat")
    try:
        while True:
            # Receive message asynchronously
            data = await websocket.receive_text()
            # Reply to the sender
            await manager.send_personal_message(f"You wrote: {data}", user_id)
            # Broadcast to others
            await manager.broadcast(f"User #{user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"User #{user_id} left the chat")
'''