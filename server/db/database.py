from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = f"sqlite+aiosqlite:///{BASE_DIR}/store/app.db"

engine  = create_async_engine(
      DB_URL, 
      echo=False,
)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA wal_autocheckpoint=100")   # checkpoint every 100 pages
    cursor.execute("PRAGMA cache_size=-8000")         # 8MB cache limit
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal as session:
            yield session