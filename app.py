import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Retirement Planner", layout="wide")

def main():
    st.title("Retirement Planner")
    
    # --- Assumptions ---
    st.header("Assumptions")
    a1, a2, a3 = st.columns(3)
    curr_age = a1.number_input("Current Age", value=25)
    ret_age = a2.number_input("Retirement Age", value=50)
    end_age = a3.number_input("Expenses until age", value=85)

    a4, a5, a6 = st.columns(3)
    init_savings = a4.number_input("Current Savings", value=0)
    monthly_invest = a5.number_input("Monthly Investments", value=10000)
    step_up = a6.number_input("Annual Step-up (%)", value=5.0) / 100

    a7, a8 = st.columns(2)
    monthly_exp_today = a7.number_input("Post-retirement monthly expense (Today's rate)", value=50000)
    inflation = a8.number_input("Inflation (%)", value=5.0) / 100

    # --- Investment & Tax Approach ---
    st.header("Investment Approach")
    asset_names = ["Fixed Returns", "Large Cap Mutual Funds", "Midcap Mutual Funds", "Smallcap mutual funds"]
    def_returns = [0.07, 0.12, 0.15, 0.18]
    def_taxes = [0.30, 0.20, 0.20, 0.20]
    
    col_e, col_r = st.columns(2)

    with col_e:
        st.subheader("Earning Phase")
        e_shares = [0.20, 0.40, 0.30, 0.10]
        e_results = []
        for i, name in enumerate(asset_names):
            c1, c2, c3 = st.columns([2, 1, 1])
            r = c1.number_input(f"{name} Return", value=def_returns[i], format="%.2f", key=f"er_{i}")
            t = c2.number_input(f"Tax", value=def_taxes[i], format="%.2f", key=f"et_{i}")
            s = c3.number_input(f"Share", value=e_shares[i], format="%.2f", key=f"es_{i}")
            e_results.append({"r": r, "t": t, "s": s})
        
        # Excel Logic: Row 11 Weighted Values
        w_ret_e = sum(d['r'] * d['s'] for d in e_results)
        w_tax_e = sum(d['t'] * d['s'] for d in e_results)
        st.write(f"Weighted Return: {w_ret_e:.3f} | Weighted Tax: {w_tax_e:.3f}")

    with col_r:
        st.subheader("Retirement Phase")
        r_shares = [0.00, 1.00, 0.00, 0.00]
        r_results = []
        for i, name in enumerate(asset_names):
            c1, c2, c3 = st.columns([2, 1, 1])
            r = c1.number_input(f"{name} Return", value=def_returns[i], format="%.2f", key=f"rr_{i}")
            t = c2.number_input(f"Tax", value=def_taxes[i], format="%.2f", key=f"rt_{i}")
            s = c3.number_input(f"Share", value=r_shares[i], format="%.2f", key=f"rs_{i}")
            r_results.append({"r": r, "t": t, "s": s})
            
        w_ret_r = sum(d['r'] * d['s'] for d in r_results)
        w_tax_r = sum(d['t'] * d['s'] for d in r_results)
        st.write(f"Weighted Return: {w_ret_r:.3f} | Weighted Tax: {w_tax_r:.3f}")

    # --- Calculations ---
    data = []
    current_bal = init_savings
    annual_inv = monthly_invest * 12

    for age in range(curr_age, 101):
        if age < ret_age:
            status, rate = "Earning", w_ret_e
            inv = annual_inv if age == curr_age else annual_inv * ((1 + step_up) ** (age - curr_age))
            exp = 0
        elif age < end_age:
            status, rate = "Retired", w_ret_r
            inv = 0
            exp = (monthly_exp_today * 12) * ((1 + inflation) ** (age - curr_age))
        else:
            status, rate, inv, exp, current_bal = "Dead", 0, 0, 0, 0

        start_bal = current_bal
        # Ending Savings = Starting * (1 + Weighted Return) + Additional Savings - Planned Expenses
        end_bal = (start_bal * (1 + rate)) + inv - exp if status != "Dead" else 0
        
        data.append({
            "Age": age, "Status": status, "Starting Saving": start_bal,
            "Investment": inv, "Expenses": exp, "Ending Saving": end_bal
        })
        current_bal = end_bal

    df = pd.DataFrame(data)

    # --- Visuals ---
    st.header("Results")
    m1, m2 = st.columns(2)
    corpus = df[df['Age'] == ret_age]['Starting Saving'].values[0]
    m1.metric("Retirement Corpus", f"{corpus:,.0f}")
    
    out_of_money = df[(df['Status'] == 'Retired') & (df['Ending Saving'] < 0)]
    if not out_of_money.empty:
        m2.error(f"Funds exhausted at age {out_of_money.iloc[0]['Age']}")
    else:
        m2.success("Sustainable Plan")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['Ending Saving'], fill='tozeroy', name="Savings"))
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("Detailed Breakdown")
    st.dataframe(df)

if __name__ == "__main__":
    main()
