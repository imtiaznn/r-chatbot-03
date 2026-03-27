from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = f"sqlite+aiosqlite:///{BASE_DIR}/store/app.db"

engine  = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal as session:
            yield session