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

from app.pipeline import process_user_message

class TrackingServer(socketio.AsyncServer):
    async def _trigger_event(self, event, *args, **kwargs):
        # This fires for every socket event — user_uttered, connect, disconnect etc
        
        sid = args[0]

        session = await self.get_session(sid)
        user_id = session.get("user_id")

        start = time.perf_counter()
        result = await super()._trigger_event(event, *args, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000

        asyncio.create_task(
            insert_event(
                path=event,                             # event name, e.g. "user_uttered"
                sid=sid,                                # socket session id
                user_id=user_id,
                duration_ms=round(duration_ms, 2),
            )
        )

        return result
    
# Server Initializations
sio = TrackingServer(
        async_mode="asgi", 
        cors_allowed_origins="*" # DEV ONLY
)

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

# Keep track of sessions
sessions = {}

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
        # await sio.emit("form_error", {"message": "Name and email are required"}, to=sid)
        return

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                result = await session.execute(
                    select(Users).where(Users.email == email)
                )
                user = result.scalar_one_or_none()
                is_returning = user is not None

                if not is_returning:
                    user = Users(name=name, email=email)
                    session.add(user)
                    await session.flush()

                user_id = user.id

        await sio.save_session(sid, {"user_id": user_id})
        await sio.emit("form_success", {
            "user_id": user_id,
            "is_returning": is_returning
        }, to=sid)

    except Exception as e:
        print(f"---- ERROR: (access_form_submit) {e}")
        # await sio.emit("form_error", {"message": "Something went wrong, please try again"}, to=sid)

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
async def error(sid, data):
    print(f"---- ERROR: {data.get(type)}")
    await sio.emit(
        "bot_uttered",
        {"text": data.get(type)},
        to=sid
    )

# Handle disconnects
@sio.event
async def disconnect(sid):
    print("---- CLIENT DISCONNECTED:", sid)
    sessions.pop(sid, None)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5005,
        reload=True
    )