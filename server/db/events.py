from db.database import AsyncSessionLocal
from db.models import Events, Sessions

async def insert_event(
    path: str,
    sid: str = None,
    user_id: str = None,
    duration_ms: float = None,
    data= None,
):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(Events(
                sid=sid,
                event=path,
                user_id=user_id,
                duration_ms=duration_ms,
                data=data
            ))

            print(f"""---- ADDED EVENT:\n
                    \tevent: {path}, 
                    \tsid: {sid}, 
                    \tuserID: {user_id}""")
            
async def insert_session(
        user_id: int,
):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(Sessions(
                user_id=user_id
            ))