import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Retirement Planner", layout="wide")

def main():
    st.title("Retirement Planner")
    
    # --- 1. General Parameters ---
    st.subheader("General Parameters")
    col_a, col_b, col_c = st.columns(3)
    curr_age = col_a.number_input("Current Age", value=25)
    ret_age = col_b.number_input("Retirement Age", value=50)
    end_age = col_c.number_input("Plan Until Age", value=85)

    col_d, col_e, col_f = st.columns(3)
    init_savings = col_d.number_input("Current Savings (₹)", value=0)
    monthly_invest = col_e.number_input("Monthly Investment (₹)", value=10000)
    step_up = col_f.number_input("Annual Step-up (%)", value=5.0) / 100

    col_g, col_h = st.columns(2)
    monthly_exp_today = col_g.number_input("Monthly Expense (Today's ₹)", value=50000)
    inflation = col_h.number_input("Annual Inflation (%)", value=5.0) / 100

    # --- 2. Investment & Tax (Asset Breakdown) ---
    st.divider()
    st.subheader("Investment & Tax Approach")
    
    asset_names = ["Fixed Returns", "Large Cap Mutual Funds", "Midcap Mutual Funds", "Smallcap Mutual funds"]
    def_returns = [0.07, 0.12, 0.15, 0.18]
    def_taxes = [0.30, 0.20, 0.20, 0.20]

    col_earning, col_retire = st.columns(2)

    # Earning Phase Portfolio
    with col_earning:
        st.markdown("**Earning Phase**")
        e_shares = [0.20, 0.40, 0.30, 0.10]
        e_data = []
        for i, name in enumerate(asset_names):
            c1, c2, c3 = st.columns([2, 1, 1])
            r = c1.number_input(f"{name} Ret", value=def_returns[i], key=f"er_{i}")
            t = c2.number_input(f"Tax", value=def_taxes[i], key=f"et_{i}")
            s = c3.number_input(f"Share", value=e_shares[i], key=f"es_{i}")
            e_data.append({'r': r, 't': t, 's': s})
        
        # Row 11 Weighted Logic
        w_ret_e = sum(d['r'] * d['s'] for d in e_data)
        w_tax_e = sum(d['t'] * d['s'] for d in e_data)
        st.info(f"Weighted Return: {w_ret_e:.3f} | Weighted Tax: {w_tax_e:.3f}")

    # Retirement Phase Portfolio
    with col_retire:
        st.markdown("**Retirement Phase**")
        r_shares = [0.00, 1.00, 0.00, 0.00]
        r_data = []
        for i, name in enumerate(asset_names):
            c1, c2, c3 = st.columns([2, 1, 1])
            r = c1.number_input(f"{name} Ret", value=def_returns[i], key=f"rr_{i}")
            t = c2.number_input(f"Tax", value=def_taxes[i], key=f"rt_{i}")
            s = c3.number_input(f"Share", value=r_shares[i], key=f"rs_{i}")
            r_data.append({'r': r, 't': t, 's': s})
            
        # Row 21 Weighted Logic
        w_ret_r = sum(d['r'] * d['s'] for d in r_data)
        w_tax_r = sum(d['t'] * d['s'] for d in r_data)
        st.info(f"Weighted Return: {w_ret_r:.3f} | Weighted Tax: {w_tax_r:.3f}")

    # --- 3. Calculation Engine ---
    results = []
    current_savings = init_savings
    annual_invest = monthly_invest * 12

    for age in range(curr_age, 101):
        if age < ret_age:
            status, rate = "Earning", w_ret_e
            # Step up calculation matching Excel
            inv = annual_invest if age == curr_age else annual_invest * ((1 + step_up) ** (age - curr_age))
            planned_exp = 0
        elif age < end_age:
            status, rate = "Retired", w_ret_r
            inv = 0
            # Inflation indexed expenses
            planned_exp = (monthly_exp_today * 12) * ((1 + inflation) ** (age - curr_age))
        else:
            status, rate, inv, planned_exp, current_savings = "Dead", 0, 0, 0, 0

        starting_saving = current_savings
        # Excel Logic: Ending = Starting * (1 + Return) + Savings - Expenses
        if status != "Dead":
            ending_saving = (starting_saving * (1 + rate)) + inv - planned_exp
        else:
            ending_saving = 0
            
        results.append({
            "Age": age, 
            "Starting Saving": starting_saving, 
            "Planned expenses": planned_exp,
            "Additional Savings": inv, 
            "Ending Saving": ending_saving, 
            "Status": status
        })
        current_savings = ending_saving

    # --- 4. Dashboard & Chart ---
    df = pd.DataFrame(results)
    st.divider()
    
    col_m1, col_m2 = st.columns(2)
    corpus = df[df['Age'] == ret_age]['Starting Saving'].values[0]
    col_m1.metric("Retirement Corpus", f"₹{corpus:,.0f}")
    
    out_of_money = df[(df['Status'] == 'Retired') & (df['Ending Saving'] < 0)]
    if not out_of_money.empty:
        col_m2.error(f"Funds exhaust at age {out_of_money.iloc[0]['Age']}")
    else:
        col_m2.success("Sustainability: Secure")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Ending Saving'], fill='tozeroy', name="Wealth Balance"))
    fig.update_layout(title="Wealth Projection", xaxis_title="Age", yaxis_title="Savings (₹)")
    st.plotly_chart(fig, use_container_width=True)

    # Full Data Table
    with st.expander("View Annual Table"):
        st.dataframe(df.style.format("{:,.2f}", subset=["Starting Saving", "Planned expenses", "Additional Savings", "Ending Saving"]))

if __name__ == "__main__":
    main()
