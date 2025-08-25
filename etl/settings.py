from sqlalchemy import text
from .utils import get_engine

def set_setting(key: str, value: str):
    e = get_engine()
    with e.begin() as c:
        c.execute(text("""INSERT INTO settings(key, value)
                          VALUES(:k, :v)
                          ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP"""),
                  {"k": key, "v": value})

def get_setting(key: str, default: str = "") -> str:
    e = get_engine()
    with e.connect() as c:
        row = c.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": key}).fetchone()
        return row[0] if row else default
