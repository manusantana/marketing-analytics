# --- resolver imports relativos ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


import streamlit as st
from etl.utils import ensure_aux_tables, get_setting, save_setting

# Garantiza tablas auxiliares (settings)
ensure_aux_tables()

st.set_page_config(page_title="Conectores", layout="wide")
st.title("🔌 Conectores")

st.markdown("#### Google Analytics 4 (GA4)")
ga4_enabled = st.checkbox("Activar GA4", value=(get_setting("ga4_enabled","false")=="true"))
ga4_property = st.text_input("GA4 property_id", value=get_setting("ga4_property_id",""))
ga4_json_path = st.text_input("Ruta JSON Service Account", value=get_setting("ga4_credentials_json_path",""))
if st.button("Guardar GA4"):
    save_setting("ga4_enabled", "true" if ga4_enabled else "false")
    save_setting("ga4_property_id", ga4_property)
    save_setting("ga4_credentials_json_path", ga4_json_path)
    st.success("GA4 guardado.")

st.divider()
st.markdown("#### Meta Ads")
meta_enabled = st.checkbox("Activar Meta Ads", value=(get_setting("meta_enabled","false")=="true"))
meta_token = st.text_input("Access Token", value=get_setting("meta_access_token",""))
meta_acct = st.text_input("Ad Account ID", value=get_setting("meta_ad_account_id",""))
if st.button("Guardar Meta Ads"):
    save_setting("meta_enabled", "true" if meta_enabled else "false")
    save_setting("meta_access_token", meta_token)
    save_setting("meta_ad_account_id", meta_acct)
    st.success("Meta Ads guardado.")

st.divider()
st.markdown("#### Shopify")
shop_enabled = st.checkbox("Activar Shopify", value=(get_setting("shop_enabled","false")=="true"))
shop_name = st.text_input("Shop (midominio.myshopify.com)", value=get_setting("shop_name",""))
shop_token = st.text_input("Admin API Token", value=get_setting("shop_admin_token",""), type="password")
if st.button("Guardar Shopify"):
    save_setting("shop_enabled", "true" if shop_enabled else "false")
    save_setting("shop_name", shop_name)
    save_setting("shop_admin_token", shop_token)
    st.success("Shopify guardado.")

st.caption("Solo guarda credenciales. La extracción vive en etl/pull_*.py.")
