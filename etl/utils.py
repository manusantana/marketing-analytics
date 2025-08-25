import os
from sqlalchemy import create_engine

def get_engine():
    db_url = os.getenv("DB_URL", "sqlite:///db/dev.db")
    return create_engine(db_url)
