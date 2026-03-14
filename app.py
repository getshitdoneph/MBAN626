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

# ============================================================================
# CUSTOM TAB IMPLEMENTATION WITH BUTTONS
# ============================================================================

# Create a row of buttons for tab selection
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    overview_clicked = st.button("📊 OVERVIEW", use_container_width=True)
with col2:
    contract_clicked = st.button("📝 CONTRACT", use_container_width=True)
with col3:
    payment_clicked = st.button("💳 PAYMENT", use_container_width=True)
with col4:
    tenure_clicked = st.button("📅 TENURE", use_container_width=True)
with col5:
    insights_clicked = st.button("🔑 INSIGHTS", use_container_width=True)

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'overview'

# Update based on button clicks
if overview_clicked:
    st.session_state.current_view = 'overview'
if contract_clicked:
    st.session_state.current_view = 'contract'
if payment_clicked:
    st.session_state.current_view = 'payment'
if tenure_clicked:
    st.session_state.current_view = 'tenure'
if insights_clicked:
    st.session_state.current_view = 'insights'

st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS (Always visible)
# ============================================================================
with st.sidebar:
    st.header("🔍 Filters")
    
    # Contract filter
    contracts = ['All'] + sorted(df['contract'].unique().tolist())
    selected_contract = st.selectbox("Contract Type", contracts)
    
    # Payment method filter
    payments = ['All'] + sorted(df['paymentmethod'].unique().tolist())
    selected_payment = st.selectbox("Payment Method", payments)
    
    # Tenure range filter
    min_tenure, max_tenure = int(df['tenure'].min()), int(df['tenure'].max())
    tenure_range = st.slider("Tenure (months)", min_tenure, max_tenure, (min_tenure, max_tenure))

# Apply filters
filtered_df = df.copy()
if selected_contract != 'All':
    filtered_df = filtered_df[filtered_df['contract'] == selected_contract]
if selected_payment != 'All':
    filtered_df = filtered_df[filtered_df['paymentmethod'] == selected_payment]
filtered_df = filtered_df[(filtered_df['tenure'] >= tenure_range[0]) & 
                          (filtered_df['tenure'] <= tenure_range[1])]

# KPI Cards (Always visible)
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
# DISPLAY DIFFERENT VIEWS BASED ON BUTTON CLICK
# ============================================================================

# OVERVIEW TAB
if st.session_state.current_view == 'overview':
    st.header("📊 Overview Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Churn distribution
        fig = px.pie(filtered_df, names='churn', title='Churn Distribution',
                     color_discrete_map={'No': '#66b3ff', 'Yes': '#ff9999'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly charges distribution
        fig = px.histogram(filtered_df, x='monthlycharges', color='churn',
                          title='Monthly Charges Distribution',
                          color_discrete_map={'No': '#66b3ff', 'Yes': '#ff9999'},
                          nbins=30)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tenure distribution
        fig = px.histogram(filtered_df, x='tenure', color='churn',
                          title='Tenure Distribution',
                          color_discrete_map={'No': '#66b3ff', 'Yes': '#ff9999'},
                          nbins=30)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Senior citizen analysis
        senior_churn = filtered_df.groupby('seniorcitizen')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100).reset_index()
        senior_churn['seniorcitizen'] = senior_churn['seniorcitizen'].map({0: 'Non-Senior', 1: 'Senior'})
        senior_churn.columns = ['Customer Type', 'Churn Rate']
        fig = px.bar(senior_churn, x='Customer Type', y='Churn Rate',
                     title='Churn: Senior vs Non-Senior',
                     color='Customer Type',
                     color_discrete_map={'Senior': '#ff9999', 'Non-Senior': '#66b3ff'})
        st.plotly_chart(fig, use_container_width=True)

# CONTRACT TAB
elif st.session_state.current_view == 'contract':
    st.header("📝 Contract Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Contract distribution
        contract_counts = filtered_df['contract'].value_counts().reset_index()
        contract_counts.columns = ['Contract', 'Count']
        fig = px.pie(contract_counts, values='Count', names='Contract',
                     title='Contract Type Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churn by contract
        contract_churn = filtered_df.groupby('contract')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100).reset_index()
        contract_churn.columns = ['Contract', 'Churn Rate']
        fig = px.bar(contract_churn, x='Contract', y='Churn Rate',
                     title='Churn Rate by Contract Type',
                     color='Churn Rate', color_continuous_scale='RdYlGn_r',
                     text_auto='.1f')
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Contract insights
    st.markdown("### 📊 Contract Insights")
    contract_stats = filtered_df.groupby('contract').agg({
        'churn': lambda x: (x == 'Yes').mean() * 100,
        'customerid': 'count',
        'monthlycharges': 'mean'
    }).round(2)
    contract_stats.columns = ['Churn Rate (%)', 'Customer Count', 'Avg Monthly Charges']
    st.dataframe(contract_stats, use_container_width=True)

# PAYMENT TAB
elif st.session_state.current_view == 'payment':
    st.header("💳 Payment Method Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Payment method distribution
        payment_counts = filtered_df['paymentmethod'].value_counts().reset_index()
        payment_counts.columns = ['Payment Method', 'Count']
        fig = px.bar(payment_counts, x='Count', y='Payment Method',
                     orientation='h', title='Payment Method Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churn by payment method
        payment_churn = filtered_df.groupby('paymentmethod')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100).sort_values().reset_index()
        payment_churn.columns = ['Payment Method', 'Churn Rate']
        fig = px.bar(payment_churn, x='Churn Rate', y='Payment Method',
                     orientation='h', color='Churn Rate',
                     color_continuous_scale='RdYlGn_r',
                     title='Churn Rate by Payment Method',
                     text_auto='.1f')
        fig.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 💡 Payment Insights")
    st.info("Electronic check users have the highest churn rate. Consider promoting automatic payment methods with small discounts.")

# TENURE TAB
elif st.session_state.current_view == 'tenure':
    st.header("📅 Tenure Analysis")
    
    # Create tenure groups
    filtered_df['tenure_group'] = pd.cut(filtered_df['tenure'],
                                         bins=[0, 6, 12, 24, 48, 72],
                                         labels=['0-6 months', '7-12 months', 
                                                '13-24 months', '25-48 months', '49-72 months'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tenure distribution
        tenure_dist = filtered_df['tenure_group'].value_counts().sort_index().reset_index()
        tenure_dist.columns = ['Tenure Group', 'Count']
        fig = px.bar(tenure_dist, x='Tenure Group', y='Count',
                     title='Customer Distribution by Tenure')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churn by tenure
        tenure_churn = filtered_df.groupby('tenure_group')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100).reset_index()
        tenure_churn.columns = ['Tenure Group', 'Churn Rate']
        fig = px.line(tenure_churn, x='Tenure Group', y='Churn Rate',
                      markers=True, title='Churn Rate by Tenure')
        fig.update_traces(line_color='red', line_width=3, marker_size=10)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Tenure Insights")
    st.warning("Customers in their first 6 months have the highest churn rate (over 50%). Focus retention efforts on new customers.")

# INSIGHTS TAB
elif st.session_state.current_view == 'insights':
    st.header("🔑 Key Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ High-Risk Segments")
        
        # Contract risk
        contract_risk = filtered_df.groupby('contract')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100)
        high_contract = contract_risk.idxmax()
        
        # Payment risk
        payment_risk = filtered_df.groupby('paymentmethod')['churn'].apply(
            lambda x: (x == 'Yes').mean() * 100)
        high_payment = payment_risk.idxmax()
        
        st.info(f"📝 **Highest churn contract:** {high_contract} ({contract_risk.max():.1f}%)")
        st.info(f"💳 **Highest churn payment:** {high_payment} ({payment_risk.max():.1f}%)")
        
        # Tenure risk
        early_tenure = filtered_df[filtered_df['tenure'] <= 6]['churn'].tolist()
        if len(early_tenure) > 0:
            early_churn = (filtered_df[filtered_df['tenure'] <= 6]['churn'] == 'Yes').mean() * 100
            st.info(f"📅 **First 6 months churn:** {early_churn:.1f}%")
    
    with col2:
        st.markdown("### 💡 Retention Opportunities")
        
        # Contract opportunity
        month_rate = (filtered_df[filtered_df['contract'] == 'Month-to-month']['churn'] == 'Yes').mean() * 100
        two_rate = (filtered_df[filtered_df['contract'] == 'Two year']['churn'] == 'Yes').mean() * 100
        if not pd.isna(month_rate) and not pd.isna(two_rate):
            st.success(f"📉 **Contract incentives:** Converting to 2-year could reduce churn by {month_rate - two_rate:.1f}%")
        
        # Payment opportunity
        electronic = filtered_df[filtered_df['paymentmethod'].str.contains('Electronic', case=False, na=False)]
        mailed = filtered_df[filtered_df['paymentmethod'].str.contains('Mailed', case=False, na=False)]
        if len(electronic) > 0 and len(mailed) > 0:
            electronic_rate = (electronic['churn'] == 'Yes').mean() * 100
            mailed_rate = (mailed['churn'] == 'Yes').mean() * 100
            st.success(f"💳 **Auto-pay promotion:** Auto-pay could reduce churn by {mailed_rate - electronic_rate:.1f}%")
    
    st.markdown("---")
    st.markdown("### 🎯 Recommended Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**1️⃣ Contract Incentives**\n\nOffer discounts for 1-2 year commitments")
    
    with col2:
        st.info("**2️⃣ Auto-Pay Promotion**\n\nDiscount for electronic payments")
    
    with col3:
        st.info("**3️⃣ Early Engagement**\n\nWelcome calls for customers < 6 months")

st.markdown("---")
st.markdown("📊 Dashboard powered by Streamlit | Telco Customer Churn Analysis | Click the buttons above to navigate")
