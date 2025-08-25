from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os

router = APIRouter()

def eng():
    return create_engine(os.getenv("DB_URL", "sqlite:///db/dev.db"))

@router.get("/summary")
def summary():
    e = eng()
    with e.connect() as c:
        rev = c.execute(text("SELECT COALESCE(sum(net_revenue),0) FROM orders")).scalar() or 0
        cogs = c.execute(text("SELECT COALESCE(sum(cogs),0) FROM orders")).scalar() or 0
    margin = rev - cogs
    pct = (margin / rev * 100) if rev else 0
    return {"revenue": rev, "cogs": cogs, "gross_margin": margin, "margin_pct": pct}
