# main.py
import os

import socketio
import uvicorn
import time
import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import engine, AsyncSessionLocal
from db.models import Base, Users
from db.events import insert_event
from db.crud import get_user

from app.pipeline import process_user_message
from app.tracking_server import sio

# class TrackingServer(socketio.AsyncServer):
#     async def _trigger_event(self, event, *args, **kwargs):
#         start = time.perf_counter()
#         result = await super()._trigger_event(event, *args, **kwargs)
#         duration_ms = (time.perf_counter() - start) * 1000

#         sid = args[0] if args else None

#         user_id = None
#         if event != "connect" and sid is not None:
#             try:
#                 sio_session = await self.get_session(sid)
#                 user_id = sio_session.get("user_id")
#             except KeyError:
#                 pass

#         asyncio.create_task(
#             insert_event(
#                 # event_type="socketio",
#                 path=event,
#                 sid=sid,
#                 user_id=user_id,
#                 duration_ms=round(duration_ms, 2),
#             )
#         )

#         return result

@asynccontextmanager
async def lifespan(app : FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

fastapi_app = FastAPI(lifespan=lifespan)
fastapi_app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@fastapi_app.get("/{full_path:path}")
def serve_react(full_path: str):
    return FileResponse(os.path.join("dist", "index.html"))

app = socketio.ASGIApp(sio, fastapi_app)

# Client connects
@sio.event
async def connect(sid, environ):
    print("---- CLIENT CONNECTED:", sid)

@sio.event
async def access_form_submit(sid, data):
    print("---- RECEIVED FORM DATA", data)

    name  = data.get("name")
    email = data.get("email")

    if not name or not email:
        return

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                user, is_returning = await get_user(session, name, email)

                user_id = user.id
                session_id = sid

        # Save both user_id and session_id into sio session
        await sio.save_session(sid, {
            "user_id": user_id,
            "session_id": session_id
        })

        await sio.emit("form_success", {
            "user_id": user_id,
            "session_id": session_id,
            "is_returning": is_returning
        }, to=sid)

    except Exception as e:
        print(f"---- ERROR: (access_form_submit) {e}")

# Handle session request from frontend
@sio.event
async def session_request(sid, data):
    session_id = data.get("session_id")
    print(f"---- SESSION REQUESTED: {session_id} (sid={sid})")
    
    # merge with existing session data instead of a separate dict
    existing = await sio._safe_get_session(sid)
    await sio.save_session(sid, {**existing, "session_id": session_id})
    
    await sio.emit("session_confirm", {"session_id": session_id}, to=sid)

# Handle user messages
@sio.event
async def user_uttered(sid, data):
    message = data.get("message")
    print("---- RECEIVED:", data)

    sio_session = await sio.get_session(sid)
    session_id = sio_session.get("session_id")

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
async def error(sid, data):
    print(f"---- ERROR: {data.get(type)}")
    await sio.emit(
        "bot_uttered",
        {"message": data.get(type)},
        to=sid
    )

# Handle disconnects
@sio.event
async def disconnect(sid):
    print("---- CLIENT DISCONNECTED:", sid)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5005,
        reload=True
    )