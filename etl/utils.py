import os, yaml
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def load_config(path: str = "config.yml") -> dict:
    if os.path.exists(path):
        import io
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def get_db_url():
    # prioriza ENV > config.yml > SQLite por defecto
    raw = os.getenv("DB_URL") or load_config().get("db_url") or "sqlite:///db/dev.db"
    if raw.startswith("sqlite:///"):
        rel = raw.replace("sqlite:///", "")  # extrae la ruta
        if not os.path.isabs(rel):           # convierte a absoluta desde la raíz del repo
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            rel = os.path.join(repo_root, rel)
        return f"sqlite:///{rel}"
    return raw


def get_engine():
    return create_engine(get_db_url())

def ensure_aux_tables():
    """Crea tablas auxiliares si no existen (settings, ingest_log)."""
    eng = get_engine()
    with eng.begin() as c:
        c.execute(text("""
        CREATE TABLE IF NOT EXISTS settings (
          key TEXT PRIMARY KEY,
          value TEXT
        );
        """))
        c.execute(text("""
        CREATE TABLE IF NOT EXISTS ingest_log (
          id INTEGER PRIMARY KEY,
          when_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          table_name TEXT,
          rows INT,
          mode TEXT,
          filename TEXT
        );
        """))

def save_setting(key: str, value: str):
    eng = get_engine()
    with eng.begin() as c:
        c.execute(text("""
            INSERT INTO settings(key, value) VALUES(:k,:v)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """), {"k": key, "v": value})

def get_setting(key: str, default: str = "") -> str:
    eng = get_engine()
    with eng.begin() as c:
        r = c.execute(text("SELECT value FROM settings WHERE key=:k"), {"k": key}).fetchone()
    return r[0] if r else default

# --- Actualizar versión de datos sin hacer nada ---
from datetime import datetime

def bump_data_version():
    """Actualiza un timestamp para invalidar caches del dashboard."""
    eng = get_engine()
    ts = datetime.utcnow().isoformat()
    with eng.begin() as c:
        c.execute(text("""
            INSERT INTO settings(key, value) VALUES('data_version', :v)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """), {"v": ts})
    return ts

def get_data_version():
    """Lee el timestamp; si no existe, devuelve '0'."""
    eng = get_engine()
    with eng.begin() as c:
        r = c.execute(text("SELECT value FROM settings WHERE key='data_version'")).fetchone()
    return r[0] if r else "0"
    
def get_db_path() -> str:
    # devuelve la ruta absoluta del fichero SQLite si aplica, o la URL completa si es Postgres
    url = get_db_url()
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return url
