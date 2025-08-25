# ruta raíz para importar 'etl'
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.utils import get_engine, load_config, ensure_aux_tables, get_data_version
import streamlit as st
import pandas as pd

cfg = load_config()                     # lee config.yml/.env
engine = get_engine()                   # motor SQLAlchemy
ensure_aux_tables()                     # crea settings/ingest_log si faltan
data_version = st.session_state.get("data_version") or get_data_version()
  # usa versión de sesión o DB
       # clave para invalidar caché

@st.cache_data(show_spinner=False)
def load_table(name: str, version: str) -> pd.DataFrame:
    # lee una tabla SQL; se recachea cuando cambia 'version'
    try:
        return pd.read_sql_table(name, engine)
    except Exception:
        return pd.DataFrame()

st.set_page_config(page_title="Marketing Analytics – MVP", layout="wide")
st.title("📊 Marketing Analytics – MVP")

orders = load_table("orders", data_version)       # pedidos (ventas/cogs)
products = load_table("products", data_version)   # catálogo
customers = load_table("customers", data_version) # clientes

revenue = float(orders["net_revenue"].sum()) if not orders.empty else 0.0  # ingresos
cogs = float(orders["cogs"].sum()) if not orders.empty else 0.0            # coste
margin = revenue - cogs                                                     # margen bruto
pct_margin = (margin / revenue * 100) if revenue else 0.0                  # % margen

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingresos", f"€{revenue:,.0f}")
c2.metric("COGS", f"€{cogs:,.0f}")
c3.metric("Margen bruto", f"€{margin:,.0f}")
c4.metric("% Margen", f"{pct_margin:.1f}%")

st.subheader("ABC Productos")
if not orders.empty:
    df_abc = (
        orders.groupby("product_id", as_index=False)["net_revenue"].sum()
        .sort_values("net_revenue", ascending=False)
    )
    df_abc["cum_pct"] = df_abc["net_revenue"].cumsum() / df_abc["net_revenue"].sum()
    df_abc["ABC"] = pd.cut(df_abc["cum_pct"], bins=[0, 0.8, 0.95, 1.0], labels=["A", "B", "C"], include_lowest=True)
    st.dataframe(df_abc, use_container_width=True)
else:
    st.info("No hay datos en 'orders'. Usa la pestaña **Ingesta** para cargar datos.")

st.subheader("Clientes – RFM (simple)")
if not orders.empty:
    o = orders.copy()
    o["date"] = pd.to_datetime(o["date"])                                  # normaliza fecha
    today = pd.Timestamp.today().normalize()                               # día actual
    rfm = (
        o.groupby("customer_id")
         .agg(recency_days=("date", lambda x: (today - x.max()).days),
              frequency=("id", "count"),
              monetary=("net_revenue", "sum"))
         .reset_index()
    )
    st.dataframe(rfm, use_container_width=True)
else:
    st.info("Sin pedidos para calcular RFM.")
