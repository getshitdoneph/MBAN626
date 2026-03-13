import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Telco Customer Churn Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Telco Customer Churn Analytics Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Contract filter
contracts = ['All'] + sorted(df['contract'].unique().tolist())
selected_contract = st.sidebar.selectbox("Contract Type", contracts)

# Payment method filter
payments = ['All'] + sorted(df['paymentmethod'].unique().tolist())
selected_payment = st.sidebar.selectbox("Payment Method", payments)

# Tenure range filter
min_tenure, max_tenure = int(df['tenure'].min()), int(df['tenure'].max())
tenure_range = st.sidebar.slider("Tenure (months)", min_tenure, max_tenure, (min_tenure, max_tenure))

# Apply filters
filtered_df = df.copy()
if selected_contract != 'All':
    filtered_df = filtered_df[filtered_df['contract'] == selected_contract]
if selected_payment != 'All':
    filtered_df = filtered_df[filtered_df['paymentmethod'] == selected_payment]
filtered_df = filtered_df[(filtered_df['tenure'] >= tenure_range[0]) & 
                          (filtered_df['tenure'] <= tenure_range[1])]

# KPI Cards
st.markdown("## 📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_customers = len(filtered_df)
    st.metric("Total Customers", f"{total_customers:,}")

with col2:
    churn_rate = (filtered_df['churn'] == 'Yes').mean() * 100
    st.metric("Churn Rate", f"{churn_rate:.1f}%")

with col3:
    avg_monthly = filtered_df['monthlycharges'].mean()
    st.metric("Avg Monthly Charge", f"${avg_monthly:.2f}")

with col4:
    avg_tenure = filtered_df['tenure'].mean()
    st.metric("Avg Tenure", f"{avg_tenure:.1f} months")

st.markdown("---")

# ============================================================================
# VISUALIZATION 1: Churn Distribution (Pie Chart)
# ============================================================================
st.subheader("1️⃣ Churn Distribution")
churn_counts = filtered_df['churn'].value_counts().reset_index()
churn_counts.columns = ['Churn', 'Count']

fig = px.pie(churn_counts, values='Count', names='Churn', 
             color='Churn', color_discrete_map={'No': '#66b3ff', 'Yes': '#ff9999'},
             title=f'Overall Churn Rate: {churn_rate:.1f}%')
fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 2: Churn by Contract Type (Bar Chart)
# ============================================================================
st.subheader("2️⃣ Churn Rate by Contract Type")
contract_churn = filtered_df.groupby('contract')['churn'].apply(
    lambda x: (x == 'Yes').mean() * 100).reset_index()
contract_churn.columns = ['Contract', 'Churn Rate']

fig = px.bar(contract_churn, x='Contract', y='Churn Rate',
             color='Churn Rate', color_continuous_scale='RdYlGn_r',
             title='Which contract types have highest churn?',
             text_auto='.1f')
fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 3: Churn by Tenure (Line Chart)
# ============================================================================
st.subheader("3️⃣ Churn Rate by Customer Tenure")

# Create tenure groups if not already in data
if 'tenure_group' not in filtered_df.columns:
    filtered_df['tenure_group'] = pd.cut(filtered_df['tenure'],
                                         bins=[0, 6, 12, 24, 48, 72],
                                         labels=['0-6 months', '7-12 months', 
                                                '13-24 months', '25-48 months', '49-72 months'])

tenure_churn = filtered_df.groupby('tenure_group')['churn'].apply(
    lambda x: (x == 'Yes').mean() * 100).reset_index()
tenure_churn.columns = ['Tenure Group', 'Churn Rate']

fig = px.line(tenure_churn, x='Tenure Group', y='Churn Rate',
              markers=True, title='How does churn change over time?')
fig.update_traces(line_color='red', line_width=3, marker_size=10)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 4: Monthly Charges Distribution (Histogram)
# ============================================================================
st.subheader("4️⃣ Monthly Charges: Retained vs Churned")
fig = go.Figure()
fig.add_trace(go.Histogram(x=filtered_df[filtered_df['churn']=='No']['monthlycharges'],
                           name='Retained', opacity=0.7, marker_color='#66b3ff'))
fig.add_trace(go.Histogram(x=filtered_df[filtered_df['churn']=='Yes']['monthlycharges'],
                           name='Churned', opacity=0.7, marker_color='#ff9999'))
fig.update_layout(barmode='overlay', 
                  title='Do customers with higher monthly charges churn more?',
                  xaxis_title='Monthly Charges ($)',
                  yaxis_title='Number of Customers')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 5: Payment Method Analysis (Horizontal Bar)
# ============================================================================
st.subheader("5️⃣ Churn Rate by Payment Method")
payment_churn = filtered_df.groupby('paymentmethod')['churn'].apply(
    lambda x: (x == 'Yes').mean() * 100).sort_values().reset_index()
payment_churn.columns = ['Payment Method', 'Churn Rate']

fig = px.bar(payment_churn, x='Churn Rate', y='Payment Method',
             orientation='h', color='Churn Rate',
             color_continuous_scale='RdYlGn_r',
             title='Which payment methods have highest risk?')
fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
fig.update_layout(xaxis_title='Churn Rate (%)', yaxis_title='')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 6: Senior Citizen Analysis (Bar Chart)
# ============================================================================
st.subheader("6️⃣ Churn: Senior Citizens vs Non-Seniors")
senior_churn = filtered_df.groupby('seniorcitizen')['churn'].apply(
    lambda x: (x == 'Yes').mean() * 100).reset_index()
senior_churn['seniorcitizen'] = senior_churn['seniorcitizen'].map({0: 'Non-Senior', 1: 'Senior'})
senior_churn.columns = ['Customer Type', 'Churn Rate']

fig = px.bar(senior_churn, x='Customer Type', y='Churn Rate',
             color='Customer Type', 
             color_discrete_map={'Senior': '#ff9999', 'Non-Senior': '#66b3ff'},
             title='Do senior citizens churn more?',
             text_auto='.1f')
fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# VISUALIZATION 7: Partner & Dependents Impact
# ============================================================================
st.subheader("7️⃣ Impact of Family Status on Churn")

col1, col2 = st.columns(2)

with col1:
    partner_churn = filtered_df.groupby('partner')['churn'].apply(
        lambda x: (x == 'Yes').mean() * 100).reset_index()
    partner_churn.columns = ['Has Partner', 'Churn Rate']
    fig = px.bar(partner_churn, x='Has Partner', y='Churn Rate',
                 color='Has Partner',
                 color_discrete_map={'Yes': '#66b3ff', 'No': '#ff9999'},
                 title='Churn by Partner Status')
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    dependents_churn = filtered_df.groupby('dependents')['churn'].apply(
        lambda x: (x == 'Yes').mean() * 100).reset_index()
    dependents_churn.columns = ['Has Dependents', 'Churn Rate']
    fig = px.bar(dependents_churn, x='Has Dependents', y='Churn Rate',
                 color='Has Dependents',
                 color_discrete_map={'Yes': '#66b3ff', 'No': '#ff9999'},
                 title='Churn by Dependents Status')
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# Key Insights Panel
# ============================================================================
st.subheader("🔑 Key Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**⚠️ High-Risk Segments:**")
    
    contract_risk = filtered_df.groupby('contract')['churn'].apply(
        lambda x: (x == 'Yes').mean() * 100)
    high_contract = contract_risk.idxmax()
    
    payment_risk = filtered_df.groupby('paymentmethod')['churn'].apply(
        lambda x: (x == 'Yes').mean() * 100)
    high_payment = payment_risk.idxmax()
    
    st.info(f"📝 **Highest churn contract:** {high_contract} ({contract_risk.max():.1f}%)")
    st.info(f"💳 **Highest churn payment:** {high_payment} ({payment_risk.max():.1f}%)")

with col2:
    st.markdown("**💡 Retention Opportunities:**")
    
    month_to_month = filtered_df[filtered_df['contract'] == 'Month-to-month']['churn'].tolist()
    two_year = filtered_df[filtered_df['contract'] == 'Two year']['churn'].tolist()
    
    if len(month_to_month) > 0 and len(two_year) > 0:
        month_rate = (filtered_df[filtered_df['contract'] == 'Month-to-month']['churn'] == 'Yes').mean() * 100
        two_rate = (filtered_df[filtered_df['contract'] == 'Two year']['churn'] == 'Yes').mean() * 100
        st.success(f"📉 **Contract incentives:** Converting to 2-year could reduce churn by {month_rate - two_rate:.1f}%")

st.markdown("---")
st.markdown("📊 Dashboard powered by Streamlit | Telco Customer Churn Analysis")
