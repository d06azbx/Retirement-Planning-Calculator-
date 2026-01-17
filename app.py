import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Retirement Planner", layout="wide")

def main():
    st.title("📊 Retirement Planner (with Tax Logic)")
    
    # --- Sidebar: User Inputs ---
    st.sidebar.header("1. General Settings")
    curr_age = st.sidebar.number_input("Current Age", value=25)
    ret_age = st.sidebar.number_input("Retirement Age", value=50)
    end_age = st.sidebar.number_input("Plan Until Age", value=85)
    
    st.sidebar.header("2. Financials")
    init_savings = st.sidebar.number_input("Current Savings (₹)", value=0.0)
    monthly_invest = st.sidebar.number_input("Monthly Investment (₹)", value=10000.0)
    step_up_pct = st.sidebar.number_input("Annual Step-up (%)", value=5.0) / 100.0
    monthly_exp_today = st.sidebar.number_input("Desired Monthly Expense (Today's ₹)", value=50000.0)
    inflation_pct = st.sidebar.number_input("Annual Inflation (%)", value=5.0) / 100.0

    # --- NEW: Tax Application Toggle ---
    st.sidebar.header("3. Tax Logic")
    apply_tax = st.sidebar.checkbox("Deduct Tax from Investment Returns?", value=False, 
                                    help="If checked, the growth will be based on Post-Tax returns. Your Excel currently uses Pre-Tax returns.")

    # --- Investment & Tax Portfolio ---
    st.header("Investment & Tax Approach")
    asset_names = ["Fixed Returns", "Large Cap Mutual Funds", "Midcap Mutual Funds", "Smallcap mutual funds"]
    def_returns = [0.07, 0.12, 0.15, 0.18]
    def_taxes = [0.30, 0.20, 0.20, 0.20] # From your Excel
    def_shares_earning = [0.20, 0.40, 0.30, 0.10]
    def_shares_retire = [0.00, 1.00, 0.00, 0.00]

    col1, col2 = st.columns(2)
    
    # Earning Phase Calculations
    with col1:
        st.subheader("Earning Phase")
        e_data = []
        for i, name in enumerate(asset_names):
            c_a, c_b, c_c = st.columns(3)
            r = c_a.number_input(f"{name} Ret%", value=def_returns[i]*100, key=f"er_{i}") / 100
            t = c_b.number_input(f"{name} Tax%", value=def_taxes[i]*100, key=f"et_{i}") / 100
            s = c_c.number_input(f"{name} Share%", value=def_shares_earning[i]*100, key=f"es_{i}") / 100
            e_data.append({'r': r, 't': t, 's': s})
        
        w_ret_e = sum(d['r'] * d['s'] for d in e_data)
        w_tax_e = sum(d['t'] * d['s'] for d in e_data)
        post_tax_ret_e = w_ret_e * (1 - w_tax_e)
        
        st.info(f"Weighted Return: **{w_ret_e:.2%}** | Weighted Tax: **{w_tax_e:.2%}**")
        st.caption(f"Effective Post-Tax Return: {post_tax_ret_e:.2%}")

    # Retirement Phase Calculations
    with col2:
        st.subheader("Retirement Phase")
        r_data = []
        for i, name in enumerate(asset_names):
            c_a, c_b, c_c = st.columns(3)
            r = c_a.number_input(f"{name} Ret%", value=def_returns[i]*100, key=f"rr_{i}") / 100
            t = c_b.number_input(f"{name} Tax%", value=def_taxes[i]*100, key=f"rt_{i}") / 100
            s = c_c.number_input(f"{name} Share%", value=def_shares_retire[i]*100, key=f"rs_{i}") / 100
            r_data.append({'r': r, 't': t, 's': s})
        
        w_ret_r = sum(d['r'] * d['s'] for d in r_data)
        w_tax_r = sum(d['t'] * d['s'] for d in r_data)
        post_tax_ret_r = w_ret_r * (1 - w_tax_r)
        
        st.info(f"Weighted Return: **{w_ret_r:.2%}** | Weighted Tax: **{w_tax_r:.2%}**")
        st.caption(f"Effective Post-Tax Return: {post_tax_ret_r:.2%}")

    # --- Simulation ---
    results = []
    current_savings = init_savings
    prev_add_savings = monthly_invest * 12
    
    # Determine which return to use based on the toggle
    ret_earning = post_tax_ret_e if apply_tax else w_ret_e
    ret_retire = post_tax_ret_r if apply_tax else w_ret_r

    for age in range(curr_age, 101):
        if age < ret_age:
            status, w_ret = "Earning", ret_earning
            add_savings = (monthly_invest * 12) if age == curr_age else prev_add_savings * (1 + step_up_pct)
            planned_exp = 0
            prev_add_savings = add_savings
        elif age < end_age:
            status, w_ret = "Retired", ret_retire
            add_savings = 0
            planned_exp = (monthly_exp_today * 12) * ((1 + inflation_pct) ** (age - curr_age))
        else:
            status, w_ret, add_savings, planned_exp = "Dead", 0, 0, 0
            current_savings = 0

        starting_saving = current_savings
        if status != "Dead":
            ending_saving = starting_saving * (1 + w_ret) + add_savings - planned_exp
        else:
            ending_saving = 0
            
        results.append({
            "Age": age, "Starting": starting_saving, "Expenses (Post-Tax)": planned_exp,
            "Investment": add_savings, "Ending": ending_saving, "Status": status
        })
        current_savings = ending_saving

    # Display results
    df = pd.DataFrame(results)
    st.divider()
    
    # Metrics
    m1, m2 = st.columns(2)
    corpus = df[df['Age'] == ret_age]['Starting'].values[0]
    m1.metric("Corpus at Retirement", f"₹{corpus:,.0f}")
    
    run_out = df[(df['Status'] == 'Retired') & (df['Ending'] < 0)]
    if not run_out.empty:
        m2.error(f"Money runs out at age {run_out.iloc[0]['Age']}")
    else:
        m2.success("Savings last until planned age")

    st.subheader("Projection Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Ending'], name="Savings Balance", fill='tozeroy'))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Table")
    st.dataframe(df.style.format("₹{:,.0f}", subset=["Starting", "Expenses (Post-Tax)", "Investment", "Ending"]))

if __name__ == "__main__":
    main()
