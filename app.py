"""
Streamlit dashboard for the Turso analytics demo.

Run with:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

import queries as q

st.set_page_config(page_title="Turso Analytics Dashboard", layout="wide")

st.title("📊 E-Commerce Analytics Dashboard")
st.caption("Simulated order data stored in Turso (libSQL), queried live with SQL.")


@st.cache_resource
def get_client():
    return q.get_client()


client = get_client()

# --- Monthly revenue -------------------------------------------------------
cols, rows = q.monthly_revenue(client)
df_rev = pd.DataFrame(rows, columns=cols)

col1, col2, col3 = st.columns(3)
col1.metric("Total revenue", f"${df_rev['revenue'].sum():,.0f}")
col2.metric("Total orders", f"{int(df_rev['num_orders'].sum()):,}")

_, rr_rows = q.repeat_purchase_rate(client)
repeat_rate = rr_rows[0][0] if rr_rows and rr_rows[0][0] is not None else 0
col3.metric("Repeat purchase rate", f"{repeat_rate * 100:.1f}%")

st.subheader("Monthly revenue")
fig_rev = px.bar(df_rev, x="month", y="revenue", text_auto=".2s")
st.plotly_chart(fig_rev, use_container_width=True)

# --- Top products ------------------------------------------------------
st.subheader("Top 10 products by revenue")
cols, rows = q.top_products(client)
df_products = pd.DataFrame(rows, columns=cols)
fig_products = px.bar(
    df_products.sort_values("revenue"),
    x="revenue", y="name", color="category", orientation="h",
)
st.plotly_chart(fig_products, use_container_width=True)

# --- Revenue by region --------------------------------------------------
st.subheader("Revenue by region")
cols, rows = q.revenue_by_region(client)
df_region = pd.DataFrame(rows, columns=cols)
c1, c2 = st.columns(2)
with c1:
    fig_region = px.pie(df_region, names="region", values="revenue", hole=0.4)
    st.plotly_chart(fig_region, use_container_width=True)
with c2:
    st.dataframe(df_region, use_container_width=True)

st.caption("Data source: Turso (libSQL) — queried live via `libsql-client`.")
