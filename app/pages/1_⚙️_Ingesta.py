# ruta raíz para importar 'etl'
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from etl.utils import get_engine, ensure_aux_tables, load_config, bump_data_version  # utilidades de DB y config

# columnas mínimas requeridas por tabla
REQUIRED_COLS = {
    "products":  ["id","name","category","cost","price"],
    "customers": ["id","name","country","segment"],
    "orders":    ["id","customer_id","date","product_id","qty","net_revenue","cogs"],
    "campaigns": ["id","source","medium","campaign_name","date","cost"],
    "ga_sessions":["date","source","medium","country","sessions","transactions","revenue","users","bounces"],
}

st.set_page_config(page_title="Ingesta", layout="wide")
st.title("⚙️ Ingesta de datos (Excel/CSV)")

engine = get_engine()                    # motor SQLAlchemy
ensure_aux_tables()                      # crea settings/ingest_log si faltan
cfg = load_config()                      # lee config.yml/.env

allowed = cfg.get("ingest", {}).get("allowed_tables",
           ["products","customers","orders","campaigns","ga_sessions"])  # tablas destino permitidas
table = st.selectbox("Tabla destino", allowed, index=0)                  # selector de tabla

mode = st.radio("Modo de escritura", ["replace","append"],               # política de escritura
                index=0 if cfg.get("ingest",{}).get("default_write_mode","replace")=="replace" else 1,
                horizontal=True)

upl = st.file_uploader("Sube archivo CSV o Excel", type=["csv","xlsx","xls"])  # selector de archivo

if upl is not None:
    # lectura de archivo tolerante (CSV/Excel)
    if upl.name.lower().endswith((".xlsx",".xls")):
        df = pd.read_excel(upl)  # lectura de Excel
    else:
        try:
            df = pd.read_csv(upl)  # lectura CSV por defecto
        except UnicodeDecodeError:
            df = pd.read_csv(upl, encoding="latin-1")  # fallback de encoding

    st.write("Preview:", df.head())  # vista previa

    # validación de columnas mínimas
    missing = [c for c in REQUIRED_COLS.get(table, []) if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas en {table}: {', '.join(missing)}")  # error si faltan columnas
        st.stop()

    # casting seguro de tipos (fechas y numéricos)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date  # normaliza fechas
    for c in ("qty","net_revenue","cogs","cost","price","sessions","transactions","revenue","users","bounces"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")  # fuerza numéricos

    # botón de carga
    if st.button("Cargar"):
        if df.empty:
            st.warning("El archivo no tiene filas.")  # aviso si no hay datos
        else:
            if_exists = "replace" if mode == "replace" else "append"  # modo de escritura
            df.to_sql(table, engine, if_exists=if_exists, index=False)  # inserta en DB
            with engine.begin() as c:
                c.execute(text("""
                    INSERT INTO ingest_log(table_name, rows, mode, filename)
                    VALUES(:t,:r,:m,:f)
                """), {"t": table, "r": int(len(df)), "m": mode, "f": upl.name})  # registra histórico

            st.success(f"Cargadas {len(df)} filas en '{table}' (modo {mode}).")  # confirmación

            ts = bump_data_version()                 # sube versión global de datos
            st.cache_data.clear()                    # invalida caché global
            st.session_state["data_version"] = ts    # propaga versión en sesión
            st.switch_page("Dashboard.py")           # navega al dashboard

st.subheader("Histórico de cargas")  # listado de ingestas previas
try:
    log = pd.read_sql("SELECT when_ts, table_name, rows, mode, filename FROM ingest_log ORDER BY when_ts DESC", engine)
    st.dataframe(log, use_container_width=True)  # muestra histórico
except Exception:
    st.info("Aún no hay histórico.")  # sin registros todavía
