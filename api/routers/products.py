from fastapi import APIRouter
from sqlalchemy import create_engine
import os, pandas as pd

router = APIRouter()
engine = create_engine(os.getenv("DB_URL", "sqlite:///db/dev.db"))

@router.get("/")
def list_products():
    try:
        df = pd.read_sql_table("products", engine)
        return df.to_dict(orient="records")
    except Exception:
        return []
