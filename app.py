import streamlit as st
import pandas as pd
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Business Model Simulator", layout="wide")
st.title("🚀 Business Model Simulator")

# --- Sidebar Inputs ---
st.sidebar.header("Simulation Settings")
simulation_duration_months = st.sidebar.slider("Simulation Duration (Months)", 1, 120, 60)
initial_investment = st.sidebar.number_input("Initial Investment ($)", value=100000.0)
tax_rate_percent = st.sidebar.slider("Tax Rate (%)", 0, 50, 25)

st.sidebar.header("Revenue Parameters")
initial_customers = st.sidebar.number_input("Initial Customers", value=1000)
growth_rate = st.sidebar.slider("Monthly Growth Rate (%)", 0.0, 20.0, 5.0)
churn_rate = st.sidebar.slider("Monthly Churn Rate (%)", 0.0, 10.0, 2.0)
avg_price = st.sidebar.number_input("Average Price per Unit ($)", value=50.0)

st.sidebar.header("Cost Parameters")
fixed_costs = st.sidebar.number_input("Monthly Fixed Costs ($)", value=15000.0)
marketing_spend = st.sidebar.number_input("Monthly Marketing Spend ($)", value=5000.0)
variable_cost_unit = st.sidebar.number_input("Variable Cost per Unit ($)", value=20.0)

st.sidebar.header("Risk Assessment")
market_adoption = st.sidebar.slider("Market Adoption Prob. (%)", 0, 100, 70)
operational_risk = st.sidebar.slider("Operational Risk Impact (%)", 0, 100, 10)

# --- Logic Functions (Based on your Uploaded Code) ---

def calculate_simulation():
    # 1. Revenue Calculation
    monthly_data = []
    current_customers = initial_customers
    for month in range(1, simulation_duration_months + 1):
        new_customers = current_customers * (growth_rate / 100)
        churned_customers = current_customers * (churn_rate / 100)
        current_customers = max(0, round(current_customers + new_customers - churned_customers))
        monthly_revenue = current_customers * avg_price
        
        # 2. Cost Calculation
        monthly_fixed_total = fixed_costs + marketing_spend
        monthly_var_total = current_customers * variable_cost_unit
        total_monthly_cost = monthly_fixed_total + monthly_var_total
        
        monthly_data.append({
            'Month': month,
            'Customers': current_customers,
            'Revenue': monthly_revenue,
            'Costs': total_monthly_cost,
            'Profit': monthly_revenue - total_monthly_cost
        })

    df = pd.DataFrame(monthly_data)
    df['Cumulative Profit'] = df['Profit'].cumsum() - initial_investment
    return df

# --- Execution & Visualization ---
df_results = calculate_simulation()

# Summary Metrics
total_rev = df_results['Revenue'].sum()
total_cost = df_results['Costs'].sum()
gross_profit = total_rev - total_cost
net_profit_after_tax = gross_profit * (1 - (tax_rate_percent / 100))

# Risk Adjusted Profit
risk_adj_rev = total_rev * (market_adoption / 100)
initial_risk_profit = risk_adj_rev - total_cost
risk_adj_net = max(0, initial_risk_profit * (1 - (operational_risk / 100)))

# Break Even Logic
be_row = df_results[df_results['Cumulative Profit'] >= 0].first_valid_index()
be_month = df_results.loc[be_row, 'Month'] if be_row is not None else "Not Reached"

# --- Display Interface ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_rev:,.0f}")
col2.metric("Net Profit (After Tax)", f"${net_profit_after_tax:,.0f}")
col3.metric("Risk-Adjusted Profit", f"${risk_adj_net:,.0f}")
col4.metric("Break-Even Month", f"{be_month}")

st.subheader("Financial Projection Over Time")
st.line_chart(df_results.set_index('Month')[['Revenue', 'Costs', 'Cumulative Profit']])

st.subheader("Monthly Data Breakdown")
st.dataframe(df_results.style.format({
    'Revenue': '${:,.2f}', 
    'Costs': '${:,.2f}', 
    'Profit': '${:,.2f}', 
    'Cumulative Profit': '${:,.2f}'
}))