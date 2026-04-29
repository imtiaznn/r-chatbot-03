# Written by Group 09
import time
import socketio
import json
import inspect
from datetime import datetime, timezone

from db.database import AsyncSessionLocal
from db.models import Sender, Messages, Events, Sessions

EXCLUDED_EMIT_EVENTS = {"dashboard_update", "form_success", "form_error", "session_confirm"}

class TrackingServer(socketio.AsyncServer):

    _last_dashboard_broadcast = None
    _dashboard_broadcast_interval = 2

    # Event Handlers tracking
    async def _on_connect(self, session, sid, payload):
        return
    async def _on_disconnect(self, session, sid, payload):
        return
    async def _on_session_request(self, session, sid, payload):
        return
    async def _on_user_uttered(self, session, sid, payload):
        sio_session = await self._safe_get_session(sid)

        session.add(Messages(
               session_id=sio_session.get("session_id"),
               text=payload.get("text"),
               sender=Sender.user
        ))

        return
    async def _on_bot_uttered(self, session, sid, payload):
        sio_session = await self._safe_get_session(sid)

        session.add(Messages(
               session_id=sio_session.get("session_id"),
               text=payload.get("text"),
               sender=Sender.bot
        ))

        return
    async def _on_access_form_submit(self, session, sid, payload):
        sio_session = await self._safe_get_session(sid)

        session.add(Sessions(
            id=sio_session.get("session_id"),
            user_id=sio_session.get("user_id")
        ))
        
        return

    async def _get_user_id(self, event, sid):
        if event == "connect" or sid is None:
            return None
        try:
            sio_session = await self.get_session(sid)
            return sio_session.get("user_id")
        except KeyError:
            return None

    async def _safe_get_session(self, sid) -> dict:
        try:
            return await self.get_session(sid)
        except KeyError:
            return {}

    def _get_incoming_dispatch_table(self):
        """Events received from client — handled in _trigger_event"""
        return {
            "connect": self._on_connect,
            "access_form_submit": self._on_access_form_submit,
            "session_request": self._on_session_request,
            "user_uttered": self._on_user_uttered,
            "disconnect": self._on_disconnect,
        }
    def _get_outgoing_dispatch_table(self):
        """Events emitted to client — handled in _emit_internal"""
        return {
            "bot_uttered": self._on_bot_uttered,
        }

    @staticmethod
    async def _parse_payload(event, payload) -> dict | None:
        # skip environ on connect — not useful to store
        if event == "connect":
            return None

        # resolve if awaitable
        try:
            if callable(getattr(payload, '__await__', None)) or inspect.isawaitable(payload):
                payload = await payload
        except Exception:
            return None

        # parse if string
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {"raw": payload}

        return payload

    async def _track(self, event, sid, user_id, payload, duration_ms, dispatch_table):
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    handler = dispatch_table.get(event)
                    if handler:
                        await handler(session, sid, payload)

                    session.add(Events(
                        session_id=sid,
                        event=event,
                        user_id=user_id,
                        duration_ms=round(duration_ms, 2) if duration_ms else None,
                        data=json.dumps(payload) if payload else None,
                    ))

            # Broadcast to dashboard room after commit
            now = datetime.now(timezone.utc).timestamp()

            if (
                self._last_dashboard_broadcast is None or
                now - self._last_dashboard_broadcast >= self._dashboard_broadcast_interval
            ):
                await self.emit("dashboard_update", {
                    "event":       event, 
                    "session_id":  sid,
                    "user_id":     user_id,
                    "duration_ms": round(duration_ms, 2) if duration_ms else None,
                    "timestamp":   datetime.now(timezone.utc).isoformat(),
                    "data":        json.dumps(payload) if payload else None,
                }, room="dashboard")
            

        except Exception as e:
            print(f"---- ERROR: (tracking_server) {e}")

    async def _trigger_event(self, event, *args, **kwargs):
        start = time.perf_counter()
        result = await super()._trigger_event(event, *args, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000

        sid     = args[1] if len(args) > 1 else None
        payload = await self._parse_payload(event, args[2] if len(args) > 2 else None)
        user_id = await self._get_user_id(event, sid)

        await self._track(event, sid, user_id, payload, duration_ms, self._get_incoming_dispatch_table())
        return result

    async def emit(self, event, data=None, to=None, room=None, skip_sid=None,
                namespace=None, callback=None, ignore_queue=False):
        
        result = await super().emit(event, data, to=to, room=room, skip_sid=skip_sid,
                                    namespace=namespace, callback=callback,
                                    ignore_queue=ignore_queue)

        # Skip internal/system events
        if event in EXCLUDED_EMIT_EVENTS:
            return result

        sid = to or room
        await self._track(event, sid, None, data, None, self._get_outgoing_dispatch_table())

        return result

# Instantiate here so everything imports from one place
sio = TrackingServer(async_mode="asgi", cors_allowed_origins="*")
