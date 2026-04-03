# main.py
import os

import socketio
import uvicorn
import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text

from db.database import engine, AsyncSessionLocal
from db.models import Base
from db.crud import get_user
from db.queries import run_query, run_all_queries, get_date_filter

from app.pipeline import process_user_message
from app.tracking_server import sio

async def periodic_checkpoint():
    """Force WAL checkpoint every 5 minutes to prevent file growth."""
    while True:
        await asyncio.sleep(300)
        try:
            async with engine.begin() as conn:
                await conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        except Exception as e:
            print(f"---- ERROR: checkpoint failed: {e}")

@asynccontextmanager
async def lifespan(app : FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    checkpoint_task = asyncio.create_task(periodic_checkpoint())

    yield

    checkpoint_task.cancel()
    await asyncio.gather(
        checkpoint_task, 
        return_exceptions=True
    )

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))

    # Shutdown
    await engine.dispose()

fastapi_app = FastAPI(lifespan=lifespan)
fastapi_app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

# Static Files
@fastapi_app.get("/")
async def serve_chatbot():
    return FileResponse(os.path.join("dist", "index.html"))

app = socketio.ASGIApp(sio, fastapi_app)

# API
@fastapi_app.get("/api/dashboard")
async def get_dashboard_data(period: str = "all", start: str = None, end: str = None):
    date_start, date_end = get_date_filter(period, start, end)
    async with AsyncSessionLocal() as session:
        return await run_all_queries(session, date_start, date_end, period)

@fastapi_app.get("/api/dashboard/{metric}")
async def get_dashboard_metric(metric: str):
    async with AsyncSessionLocal() as session:
        return await run_query(session, metric)

@fastapi_app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(os.path.join("dist", "dashboard.html"))

@sio.event
async def dashboard_join(sid):
    await sio.enter_room(sid, "dashboard")
    print(f"---- DASHBOARD: {sid} joined dashboard room")

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
    text = data.get("text")
    print("---- RECEIVED:", data)

    sio_session = await sio.get_session(sid)
    session_id = sio_session.get("session_id")

    print(f"---- USER ({session_id}): {text}")

    # Process user message (import pipeline lazily and handle errors)
    try:
        response = process_user_message(text, session_id)
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
    await sio.leave_room(sid, "dashboard")
    print("---- CLIENT DISCONNECTED:", sid)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5005,
        reload=True
    )