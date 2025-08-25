import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Marketing Analytics – MVP", layout="wide")

DB_URL = os.getenv("DB_URL","sqlite:///db/dev.db")
engine = create_engine(DB_URL)

st.title("📊 Marketing Analytics – Dashboard")

@st.cache_data
def load_table(name):
    try:
        return pd.read_sql_table(name, engine)
    except Exception:
        return pd.DataFrame()

orders = load_table('orders')
products = load_table('products')
customers = load_table('customers')

# KPIs básicos
revenue = float(orders['net_revenue'].sum()) if not orders.empty else 0.0
cogs = float(orders['cogs'].sum()) if not orders.empty else 0.0
margin = revenue - cogs
pct_margin = (margin/revenue*100) if revenue else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingresos", f"€{revenue:,.0f}")
c2.metric("COGS", f"€{cogs:,.0f}")
c3.metric("Margen bruto", f"€{margin:,.0f}")
c4.metric("% Margen", f"{pct_margin:.1f}%")

# ABC Productos
st.subheader("ABC Productos")
if not orders.empty:
    df = orders.groupby('product_id', as_index=False)['net_revenue'].sum().sort_values('net_revenue', ascending=False)
    df['cum_pct'] = df['net_revenue'].cumsum() / df['net_revenue'].sum()
    df['ABC'] = pd.cut(df['cum_pct'], bins=[0,0.8,0.95,1.0], labels=['A','B','C'], include_lowest=True)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No hay datos en 'orders'. Ve a ⚙️ Ingesta para cargar datos.")

st.sidebar.success("Usa las páginas: ⚙️ Ingesta · 🔌 Conectores")
