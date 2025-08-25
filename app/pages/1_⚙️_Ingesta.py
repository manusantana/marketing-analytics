# --- resolver imports relativos ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from etl.utils import get_engine, ensure_aux_tables, load_config, bump_data_version

REQUIRED_COLS = {  # columnas mínimas requeridas por tabla
    "products": ["id", "name", "category", "cost", "price"],
    "customers": ["id", "name", "country", "segment"],
    "orders": ["id", "customer_id", "date", "product_id", "qty", "net_revenue", "cogs"],
    "campaigns": ["id", "source", "medium", "campaign_name", "date", "cost"],
    "ga_sessions": ["date", "source", "medium", "country", "sessions", "transactions", "revenue", "users", "bounces"],
}


ensure_aux_tables()
engine = get_engine()
cfg = load_config()

st.set_page_config(page_title="Ingesta", layout="wide")
st.title("⚙️ Ingesta de datos (Excel/CSV)")

allowed = cfg.get("ingest", {}).get("allowed_tables",
           ["products","customers","orders","campaigns","ga_sessions"])
table = st.selectbox("Tabla destino", allowed, index=0)

mode = st.radio("Modo de escritura", ["replace","append"],
                index=0 if cfg.get("ingest",{}).get("default_write_mode","replace")=="replace" else 1,
                horizontal=True)

upl = st.file_uploader("Sube un archivo CSV o Excel", type=["csv","xlsx","xls"])
if upl is not None:
    if upl.name.endswith((".xlsx",".xls")):
        df = pd.read_excel(upl)
    else:
        df = pd.read_csv(upl)
    st.write("Preview:", df.head())
    # validación mínima de columnas por tabla
    missing = [c for c in REQUIRED_COLS.get(table, []) if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas en {table}: {', '.join(missing)}")  # bloquea si faltan
        st.stop()

    # casting seguro de tipos
    if table == "orders":
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date  # normaliza fechas
        for c in ("qty","net_revenue","cogs","cost","price","sessions","transactions","revenue","users","bounces"):
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")  # fuerza numéricos

        if st.button("Cargar"):
            if df.empty:
                st.warning("El archivo no tiene filas.")
            else:
                if_exists = "replace" if mode == "replace" else "append"  # modo escritura
                df.to_sql(table, engine, if_exists=if_exists, index=False)  # escribe en DB
                with engine.begin() as c:
                    c.execute(text("""
                        INSERT INTO ingest_log(table_name, rows, mode, filename)
                VALUES(:t,:r,:m,:f)
            """), {"t": table, "r": int(len(df)), "m": mode, "f": upl.name})
        st.success(f"Cargadas {len(df)} filas en '{table}' (modo {mode}).")  # feedback

        ts = bump_data_version()               # sube versión global
        st.cache_data.clear()                  # invalida caché
        st.session_state["data_version"] = ts  # propaga versión
        st.switch_page("Dashboard.py")         # navega al dashboard

st.subheader("Histórico de cargas")
try:
    log = pd.read_sql("SELECT when_ts, table_name, rows, mode, filename FROM ingest_log ORDER BY when_ts DESC", engine)
    st.dataframe(log, use_container_width=True)
except Exception:
    st.info("Aún no hay histórico.")
