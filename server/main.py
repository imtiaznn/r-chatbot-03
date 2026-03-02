# main.py
import socketio
import uvicorn

from fastapi import FastAPI
from app.pipeline import process_user_message

# Async Socket.IO server
sio = socketio.AsyncServer(
        async_mode="asgi", 
        cors_allowed_origins="*" # DEV ONLY
    )
fastapi_app = FastAPI()
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

# Keep track of sessions
sessions = {}

# Client connects
@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

# Handle session request from frontend
@sio.event
async def session_request(sid, data):
    session_id = data.get("session_id")
    sessions[sid] = session_id
    print(f"Session requested: {session_id} (sid={sid})")
    await sio.emit("session_confirm", {"session_id": session_id}, to=sid)

# Handle user messages
@sio.event
async def user_uttered(sid, data):
    message = data.get("message")
    session_id = sessions.get(sid)

    print(f"USER ({session_id}): {message}")

    # Process user message
    response = process_user_message(message, session_id)

    # Bot response
    bot_response = f"{response}"

    # Emit bot response to frontend
    print(f"\nBOT ({session_id}): {bot_response}")
    await sio.emit("bot_uttered", {"text": bot_response}, to=sid)
    print("\n\n")

# Handle disconnects
@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
    sessions.pop(sid, None)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5005,
        reload=True
    )