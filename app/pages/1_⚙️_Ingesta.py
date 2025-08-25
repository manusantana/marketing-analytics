# --- resolver imports relativos ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from etl.utils import get_engine, ensure_aux_tables, load_config, bump_data_version


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

    if st.button("Cargar"):
        if df.empty:
            st.warning("El archivo no tiene filas.")
        else:
            if_exists = "replace" if mode=="replace" else "append"
            df.to_sql(table, engine, if_exists=if_exists, index=False)
            with engine.begin() as c:
                c.execute(text("""
                    INSERT INTO ingest_log(table_name, rows, mode, filename) 
                    VALUES(:t,:r,:m,:f)
                """), {"t": table, "r": int(len(df)), "m": mode, "f": upl.name})
            st.success(f"Cargadas {len(df)} filas en '{table}' (modo {mode}).")
            ts = bump_data_version()                 # 1) sube versión global en DB
            st.cache_data.clear()                    # 2) invalida caché global
            st.session_state["data_version"] = ts    # 3) propaga versión a la sesión
            st.switch_page("Dashboard.py")              # 4) navega a la página principal
            
            bump_data_version()
            st.cache_data.clear()
            st.toast("Datos actualizados. Puedes volver al Dashboard.")

st.subheader("Histórico de cargas")
try:
    log = pd.read_sql("SELECT when_ts, table_name, rows, mode, filename FROM ingest_log ORDER BY when_ts DESC", engine)
    st.dataframe(log, use_container_width=True)
except Exception:
    st.info("Aún no hay histórico.")
