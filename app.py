import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="Retirement Planner", layout="wide")

def main():
    st.title("📊 Retirement Planner")
    st.markdown("This planner replicates the logic and structure of your retirement planning spreadsheet.")

    # --- Sidebar: User Inputs ---
    st.sidebar.header("1. Personal Details")
    curr_age = st.sidebar.number_input("Current Age", value=25, min_value=1)
    ret_age = st.sidebar.number_input("Retirement Age", value=50, min_value=curr_age)
    end_age = st.sidebar.number_input("Expenses planned until age", value=85, min_value=ret_age)
    
    st.sidebar.header("2. Savings & Investments")
    init_savings = st.sidebar.number_input("Current Savings Amount (₹)", value=0.0, step=10000.0)
    monthly_invest = st.sidebar.number_input("Current Monthly Investments (₹)", value=10000.0, step=1000.0)
    step_up_pct = st.sidebar.number_input("Annual Step-up in savings (%)", value=5.0, step=0.5) / 100.0
    
    st.sidebar.header("3. Retirement & Inflation")
    monthly_exp_today = st.sidebar.number_input("Post-retirement monthly amount (Today's rate ₹)", value=50000.0, step=5000.0)
    inflation_pct = st.sidebar.number_input("Annual Inflation (%)", value=5.0, step=0.5) / 100.0

    # --- Investment Portfolio Configuration ---
    st.header("Investment Approach")
    st.write("Configure your asset allocation and expected returns for both life phases.")
    
    asset_names = ["Fixed Returns", "Large Cap Mutual Funds", "Midcap Mutual Funds", "Smallcap mutual funds"]
    def_returns = [0.07, 0.12, 0.15, 0.18]
    def_shares_earning = [0.20, 0.40, 0.30, 0.10]
    def_shares_retire = [0.00, 1.00, 0.00, 0.00]

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Earning Phase Portfolio")
        e_returns = []
        e_shares = []
        for i, name in enumerate(asset_names):
            c_a, c_b = st.columns(2)
            with c_a:
                r = st.number_input(f"{name} Return (%)", value=def_returns[i]*100, key=f"er_{i}") / 100
            with c_b:
                s = st.number_input(f"{name} Share (%)", value=def_shares_earning[i]*100, key=f"es_{i}") / 100
            e_returns.append(r)
            e_shares.append(s)
        
        w_ret_earning = sum(r * s for r, s in zip(e_returns, e_shares))
        st.info(f"Weighted Return (Earning): **{w_ret_earning:.2%}**")
        if sum(e_shares) != 1.0:
            st.warning("Shares must sum to 100%")

    with col2:
        st.subheader("Retirement Phase Portfolio")
        r_returns = []
        r_shares = []
        for i, name in enumerate(asset_names):
            c_a, c_b = st.columns(2)
            with c_a:
                r = st.number_input(f"{name} Return (%)", value=def_returns[i]*100, key=f"rr_{i}") / 100
            with c_b:
                s = st.number_input(f"{name} Share (%)", value=def_shares_retire[i]*100, key=f"rs_{i}") / 100
            r_returns.append(r)
            r_shares.append(s)
        
        w_ret_retire = sum(r * s for r, s in zip(r_returns, r_shares))
        st.info(f"Weighted Return (Retirement): **{w_ret_retire:.2%}**")
        if sum(r_shares) != 1.0:
            st.warning("Shares must sum to 100%")

    # --- Calculation Engine ---
    results = []
    current_savings = init_savings
    prev_add_savings = monthly_invest * 12
    
    # Simulate up to age 100
    for age in range(curr_age, 101):
        if age < ret_age:
            status = "Earning"
        elif age < end_age:
            status = "Retired"
        else:
            status = "Dead"
            
        starting_saving = current_savings
        ret_year_marker = 1 if age == ret_age else 0
        
        planned_exp = 0
        add_savings = 0
        w_ret = 0
        
        if status == "Earning":
            w_ret = w_ret_earning
            if age == curr_age:
                add_savings = monthly_invest * 12
            else:
                add_savings = prev_add_savings * (1 + step_up_pct)
            planned_exp = 0
            
        elif status == "Retired":
            w_ret = w_ret_retire
            add_savings = 0
            # Indexed to inflation from current age
            planned_exp = (monthly_exp_today * 12) * ((1 + inflation_pct) ** (age - curr_age))
            
        else: # Dead status as per excel
            starting_saving = 0
            planned_exp = 0
            add_savings = 0
            w_ret = 0
            
        # The Growth Formula derived from your Excel:
        # Ending = Starting * (1 + Weighted Return) + Additional Savings - Planned Expenses
        if status != "Dead":
            ending_saving = starting_saving * (1 + w_ret) + add_savings - planned_exp
        else:
            ending_saving = 0
            
        warning = "You have run out of money" if (status == "Retired" and ending_saving < 0) else ""
            
        results.append({
            "Age": age,
            "Starting Saving": starting_saving,
            "Planned expenses (post-tax)": planned_exp,
            "Additional Savings": add_savings,
            "Ending Savings": ending_saving,
            "Status": status,
            "Retirement Year": ret_year_marker,
            "Warning": warning
        })
        
        current_savings = ending_saving
        if status == "Earning":
            prev_add_savings = add_savings

    df = pd.DataFrame(results)

    # --- Results Visualization ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    corpus = df[df['Age'] == ret_age]['Starting Saving'].values[0]
    m1.metric("Corpus at Retirement", f"₹{corpus:,.0f}")
    
    # Check sustainability
    run_out = df[(df['Status'] == 'Retired') & (df['Ending Savings'] < 0)]
    if not run_out.empty:
        run_out_age = run_out.iloc[0]['Age']
        m2.error(f"Money runs out at age {run_out_age}")
    else:
        m2.success("Savings last until planned age")
        
    m3.metric("Inflation Adjusted Exp. at Retirement", f"₹{df[df['Age'] == ret_age]['Planned expenses (post-tax)'].values[0]:,.0f}/yr")

    st.subheader("Savings Projection")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Ending Savings'], name="Ending Savings", fill='tozeroy', line=dict(color='green')))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Age", yaxis_title="Savings (₹)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Year-by-Year Breakdown")
    st.dataframe(df.style.format({
        "Starting Saving": "₹{:,.0f}",
        "Planned expenses (post-tax)": "₹{:,.0f}",
        "Additional Savings": "₹{:,.0f}",
        "Ending Savings": "₹{:,.0f}"
    }), height=500)

if __name__ == "__main__":
    main()
