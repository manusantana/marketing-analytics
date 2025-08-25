import streamlit as st
from etl.settings import set_setting, get_setting

st.set_page_config(page_title="Conectores", layout="wide")
st.title("🔌 Conectores y credenciales")
st.caption("Se guardan en la tabla 'settings'.")

with st.form("ga4"):
    st.subheader("Google Analytics 4")
    property_id = st.text_input("Property ID (GA4)", value=get_setting("ga4_property_id",""))
    ga4_json = st.text_area("Service Account JSON (pega el contenido)", value=get_setting("ga4_service_json",""), height=200)
    ok = st.form_submit_button("Guardar GA4")
    if ok:
        set_setting("ga4_property_id", property_id.strip())
        set_setting("ga4_service_json", ga4_json.strip())
        st.success("Credenciales GA4 guardadas.")

with st.form("meta"):
    st.subheader("Meta Ads")
    meta_token = st.text_input("Access Token", value=get_setting("meta_token",""), type="password")
    ad_account = st.text_input("Ad Account ID (act_123456789)", value=get_setting("meta_ad_account",""))
    ok2 = st.form_submit_button("Guardar Meta")
    if ok2:
        set_setting("meta_token", meta_token.strip())
        set_setting("meta_ad_account", ad_account.strip())
        st.success("Credenciales Meta guardadas.")

with st.form("shopify"):
    st.subheader("Shopify Admin API")
    shop = st.text_input("Shop (mi-tienda.myshopify.com)", value=get_setting("shopify_shop",""))
    token = st.text_input("Admin API Access Token", value=get_setting("shopify_token",""), type="password")
    ok3 = st.form_submit_button("Guardar Shopify")
    if ok3:
        set_setting("shopify_shop", shop.strip())
        set_setting("shopify_token", token.strip())
        st.success("Credenciales Shopify guardadas.")
