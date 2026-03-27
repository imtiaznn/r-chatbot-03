from db.database import AsyncSessionLocal
from db.models import Event

async def insert_event(
    path: str,
    sid: str = None,
    user_id: str = None,
    duration_ms: float = None,
    data= None,
):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(Event(
                event=path,
                sid=sid,
                user_id=user_id,
                duration_ms=duration_ms,
                data=data
            ))

            print(f"""---- ADDED EVENT:\n
                    \tevent: {path}, 
                    \tsid: {sid}, 
                    \tuserID: {user_id}""")