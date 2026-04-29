# Written by Group 09
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Users, Sessions, Events

async def get_user(session: AsyncSession, name: str, email: str) -> tuple[Users, bool]:
    result = await session.execute(
        select(Users).where(Users.email == email)
    )
    user = result.scalar_one_or_none()
    is_returning = user is not None

    if not is_returning:
        user = Users(name=name, email=email)
        session.add(user)
        await session.flush()

    return user, is_returning

async def get_session(session: AsyncSession, sid: str, user_id: str) -> Sessions:
    new_session = Sessions(
        id=sid,
        user_id=user_id
    )
    session.add(new_session)
    await session.flush()  # populates new_session.id before commit
    return new_session