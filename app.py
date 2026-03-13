
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Telco Churn Dashboard")

df = pd.read_csv("data.csv")

# Sidebar
st.sidebar.header("Filters")
contract = st.sidebar.selectbox("Contract", ["All"] + list(df["contract"].unique()))

# Filter
filtered = df if contract == "All" else df[df["contract"] == contract]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Customers", len(filtered))
col2.metric("Churn Rate", f"{(filtered['churn']=='Yes').mean()*100:.1f}%")
col3.metric("Avg Monthly", f"${filtered['monthlycharges'].mean():.2f}")

# Chart
fig = px.pie(filtered, names="churn")
st.plotly_chart(fig)
