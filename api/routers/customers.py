from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os

router = APIRouter()
engine = create_engine(os.getenv("DB_URL", "sqlite:///db/dev.db"))

@router.get("/count")
def customers_count():
    with engine.connect() as c:
        n = c.execute(text("SELECT COUNT(*) FROM customers")).scalar() or 0
    return {"customers": n}
