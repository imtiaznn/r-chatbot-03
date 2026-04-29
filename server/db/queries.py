# Written by Group 09
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

QUERIES = {
    # KPIs
    "total_users": """
        SELECT COUNT(*) AS total_users
        FROM users
    """,

    "total_sessions": """
        SELECT COUNT(*) AS total_sessions
        FROM sessions
        WHERE timestamp BETWEEN :start AND :end
    """,

    "total_messages": """
        SELECT COUNT(*) AS total_messages
        FROM messages
        WHERE timestamp BETWEEN :start AND :end
    """,

    "avg_bot_response_time": """
        SELECT AVG(duration_ms) AS avg_bot_response_time_ms
        FROM events
        WHERE event = 'bot_uttered'
        AND timestamp BETWEEN :start AND :end
    """,

    # Trends
    "sessions_over_time": """
        SELECT DATE(timestamp) AS day, COUNT(*) AS sessions
        FROM sessions
        WHERE timestamp BETWEEN :start and :end
        GROUP BY DATE(timestamp)
        ORDER BY day
    """,

    "sessions_over_time_hourly": """
        SELECT STRFTIME('%Y-%m-%d %H:00', timestamp) AS day, COUNT(*) AS sessions
        FROM sessions
        WHERE timestamp BETWEEN :start AND :end
        GROUP BY STRFTIME('%Y-%m-%d %H:00', timestamp)
        ORDER BY day
    """,

    "messages_over_time": """
        SELECT DATE(timestamp) AS day, COUNT(*) AS messages
        FROM messages
        WHERE timestamp BETWEEN :start and :end
        GROUP BY DATE(timestamp)
        ORDER BY day
    """,

    "messages_over_time_hourly": """
        SELECT STRFTIME('%Y-%m-%d %H:00', timestamp) AS day, COUNT(*) AS messages
        FROM messages
        WHERE timestamp BETWEEN :start AND :end
        GROUP BY STRFTIME('%Y-%m-%d %H:00', timestamp)
        ORDER BY day
    """,

    "hourly_activity": """
        SELECT CAST(STRFTIME('%H', timestamp) AS INTEGER) AS hour, COUNT(*) AS messages
        FROM messages
        WHERE sender = 'user'
        AND timestamp BETWEEN :start AND :end
        GROUP BY STRFTIME('%H', timestamp)
        ORDER BY hour
    """,

    "users_with_stats": """
        SELECT
            u.id,
            u.name,
            u.email,
            COUNT(DISTINCT s.id)  AS total_sessions,
            COUNT(m.id)           AS total_messages,
            MAX(s.timestamp)      AS last_seen
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id
        LEFT JOIN messages m ON m.session_id = s.id AND m.sender = 'user'
        GROUP BY u.id, u.name, u.email
        ORDER BY total_messages DESC
    """,

    "recent_events": """
        SELECT session_id, event, user_id, duration_ms, timestamp, data
        FROM events
        ORDER BY timestamp DESC
        LIMIT 10
    """,

    "message_categories_over_time": """
        SELECT DATE(timestamp) AS day, sender, COUNT(*) AS count
        FROM messages
        WHERE timestamp BETWEEN :start AND :end
        GROUP BY DATE(timestamp), sender
        ORDER BY day, sender
    """,

    "user_messages": """
    SELECT m.text, m.sender, m.timestamp
    FROM messages m
    JOIN sessions s ON s.id = m.session_id
    WHERE s.user_id = :user_id
    ORDER BY m.timestamp ASC
    """,
}

PERIOD_QUERY_OVERRIDES = {
    "day": {
        "messages_over_time": "messages_over_time_hourly",
        "sessions_over_time": "sessions_over_time_hourly",
    }
}

def get_date_filter(period: str, start: str = None, end: str = None) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    if period == "day":
        return (now - timedelta(days=1)).isoformat(), now.isoformat()
    elif period == "week":
        return (now - timedelta(weeks=1)).isoformat(), now.isoformat()
    elif period == "year":
        return (now - timedelta(days=365)).isoformat(), now.isoformat()
    elif period == "custom" and start and end:
        return start, end
    else:
        # default — all time
        return "2000-01-01", now.isoformat()

# Fetch a single metric
async def run_query(session: AsyncSession, key: str, start: str, end: str) -> list[dict]:
    if key not in QUERIES:
        raise KeyError(f"Query '{key}' not found")

    result = await session.execute(text(QUERIES[key]), {"start": start, "end": end})
    rows    = result.fetchall()
    columns = result.keys()
    return [dict(zip(columns, row)) for row in rows]

# Fetch all metrics
async def run_all_queries(session: AsyncSession, start: str, end: str, period: str = "all") -> dict:
    overrides = PERIOD_QUERY_OVERRIDES.get(period, {})
    
    EXCLUDE = {"user_messages", "users_with_stats"}
 
    return {
        key: await run_query(session, overrides.get(key, key), start, end)
        for key in QUERIES
        if not key.endswith("_hourly") and key not in EXCLUDE
    }