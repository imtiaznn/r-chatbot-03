# main.py
import os

import socketio
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.pipeline import process_user_message
# Delay importing the processing pipeline until needed to avoid import-time
# heavy dependencies or CLI parsing side-effects. The pipeline will be
# imported inside the `user_uttered` handler.

# Async Socket.IO server
sio = socketio.AsyncServer(
        async_mode="asgi", 
        cors_allowed_origins="*" # DEV ONLY
    )

# Mount UI components
fastapi_app = FastAPI()
fastapi_app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@fastapi_app.get("/{full_path:path}")
def serve_react(full_path: str):
    return FileResponse(os.path.join("dist", "index.html"))


app = socketio.ASGIApp(sio, fastapi_app)

# Keep track of sessions
sessions = {}

# Client connects
@sio.event
async def connect(sid, environ):
    print("---- CLIENT CONNECTED:", sid)

# Handle session request from frontend
@sio.event
async def session_request(sid, data):
    session_id = data.get("session_id")
    sessions[sid] = session_id
    print(f"---- SESSION REQUESTED: {session_id} (sid={sid})")
    await sio.emit("session_confirm", {"session_id": session_id}, to=sid)

# Handle user messages
@sio.event
async def user_uttered(sid, data):
    message = data.get("message")
    print("---- RECEIVED:", data)

    session_id = sessions.get(sid)

    print(f"---- USER ({session_id}): {message}")

    # Process user message (import pipeline lazily and handle errors)
    try:
        response = process_user_message(message, session_id)
    except Exception as e:
        print("---- ERR: error while processsing message", e)
        bot_response = "Server error: failed processing message."
    else:
        bot_response = f"{response}"

    # Emit bot response to frontend
    print(f"\n ---- BOT ({session_id}): {bot_response}")

    await sio.emit(
        "bot_uttered", 
        {"text": bot_response}, 
        to=sid
    )   
   
    print("\n\n")

@sio.event
async def crm_submit(sid, data):
    print("---- RECEIVED CRM DATA", data)

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