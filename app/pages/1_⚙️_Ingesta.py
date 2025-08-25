import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os, uuid
from datetime import datetime

st.set_page_config(page_title="Ingesta de datos", layout="wide")

DB_URL = os.getenv("DB_URL","sqlite:///db/dev.db")
engine = create_engine(DB_URL)

st.title("⚙️ Ingesta de datos (Excel/CSV)")

with st.form("uploader"):
    target = st.selectbox("Tabla destino", ["products","customers","orders","campaigns","ga_sessions"])
    mode = st.radio("Modo de carga", ["replace","append"], horizontal=True, help="replace = reemplaza tabla; append = añade filas")
    file = st.file_uploader("Sube un archivo .xlsx o .csv", type=["xlsx","csv"])
    submitted = st.form_submit_button("Cargar")

msg = st.empty()

def log_ingestion(rows:int, status:str, message:str):
    try:
        import pandas as pd
        from sqlalchemy import create_engine
        import os, uuid
        from datetime import datetime
        engine = create_engine(os.getenv("DB_URL","sqlite:///db/dev.db"))
        df = pd.DataFrame([{
            "id": str(uuid.uuid4())[:8],
            "source": "upload",
            "target_table": target,
            "mode": mode,
            "rows": rows,
            "status": status,
            "message": message,
            "ts": datetime.utcnow().isoformat(sep=' ', timespec='seconds')
        }])
        df.to_sql("ingestion_logs", engine, if_exists="append", index=False)
    except Exception:
        pass

if submitted:
    if not file:
        st.warning("Sube un archivo primero.")
    else:
        try:
            if file.name.lower().endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
            st.write("Vista previa:", df.head())
            df.to_sql(target, engine, if_exists=mode, index=False)
            msg.success(f"Cargado en '{target}': {len(df)} filas ({mode}).")
            log_ingestion(len(df), "success", "ok")
        except Exception as e:
            msg.error(f"Error: {e}")
            log_ingestion(0, "error", str(e))

st.divider()
st.subheader("Histórico de cargas")
try:
    hist = pd.read_sql("SELECT * FROM ingestion_logs ORDER BY ts DESC", engine)
    st.dataframe(hist, use_container_width=True)
except Exception:
    st.info("Aún no hay historial.")
