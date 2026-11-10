import uuid
from datetime import datetime, timezone
from pathlib import Path

import duckdb


DB_PATH = Path(__file__).resolve().parent.parent / "warehouse" / "chatbot.duckdb"

DDL = """
CREATE TABLE IF NOT EXISTS logs.conversations (
    message_id      VARCHAR,
    ts              TIMESTAMP,
    session_id      VARCHAR,
    message         VARCHAR,
    intent          VARCHAR,
    intent_conf     DOUBLE,
    sentiment       VARCHAR,
    sentiment_conf  DOUBLE,
    route           VARCHAR,
    reply           VARCHAR
)
"""

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_interaction(session_id: str, message: str, result: dict) -> None:
    """Append one row to the warehouse. Opens and closes the connection each time
    so other scripts can read the database between messages."""
    con = duckdb.connect(str(DB_PATH))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS logs")
        con.execute(DDL)
        con.execute(
            "INSERT INTO logs.conversations VALUES (?,?,?,?,?,?,?,?,?,?)",
            [
                str(uuid.uuid4()),
                datetime.now(timezone.utc).replace(tzinfo=None),
                session_id,
                message,
                result["intent"],
                result["intent_conf"],
                result["sentiment"],
                result["sentiment_conf"],
                result["route"],
                result["reply"],
            ],
        )
    finally:
        con.close()