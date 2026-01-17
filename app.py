import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="Retirement Planner", layout="centered")

def main():
    st.title("🎯 Retirement Planner")
    st.markdown("Plan your future by adjusting the parameters below.")

    # --- INPUT SECTION (Tabs for organization) ---
    tab_params, tab_assets = st.tabs(["📋 Main Parameters", "📈 Asset Allocation & Tax"])

    with tab_params:
        col1, col2 = st.columns(2)
        with col1:
            curr_age = st.number_input("Current Age", value=25)
            ret_age = st.number_input("Retirement Age", value=50)
            end_age = st.number_input("Plan Until (Age)", value=85)
        with col2:
            init_savings = st.number_input("Current Savings (₹)", value=0)
            monthly_invest = st.number_input("Monthly Investment (₹)", value=10000)
            step_up = st.number_input("Annual Step-up (%)", value=5.0) / 100

        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            monthly_exp_today = st.number_input("Monthly Expenses Today (₹)", value=50000)
        with col4:
            inflation = st.number_input("Expected Inflation (%)", value=5.0) / 100

    with tab_assets:
        st.subheader("Investment Mix")
        asset_names = ["Fixed Returns", "Large Cap", "Midcap", "Smallcap"]
        # Defaults from your Excel
        def_r = [0.07, 0.12, 0.15, 0.18]
        def_t = [0.30, 0.20, 0.20, 0.20]
        
        # Earning Phase
        with st.expander("Configure Earning Phase Portfolio", expanded=True):
            e_shares = [0.20, 0.40, 0.30, 0.10]
            e_cols = st.columns(4)
            final_e_shares = []
            for i, name in enumerate(asset_names):
                final_e_shares.append(e_cols[i].number_input(f"{name} %", value=int(e_shares[i]*100), key=f"e{i}")/100)
            
            w_ret_e = sum(r * s for r, s in zip(def_r, final_e_shares))
            w_tax_e = sum(t * s for t, s in zip(def_t, final_e_shares))
            st.caption(f"Weighted Return: {w_ret_e:.2%} | Weighted Tax: {w_tax_e:.2%}")

        # Retirement Phase
        with st.expander("Configure Retirement Phase Portfolio"):
            r_shares = [0.0, 1.0, 0.0, 0.0]
            r_cols = st.columns(4)
            final_r_shares = []
            for i, name in enumerate(asset_names):
                final_r_shares.append(r_cols[i].number_input(f"{name} %", value=int(r_shares[i]*100), key=f"r{i}")/100)
            
            w_ret_r = sum(r * s for r, s in zip(def_r, final_r_shares))
            w_tax_r = sum(t * s for t, s in zip(def_t, final_r_shares))
            st.caption(f"Weighted Return: {w_ret_r:.2%} | Weighted Tax: {w_tax_r:.2%}")

    # --- CALCULATION ENGINE ---
    data = []
    balance = init_savings
    yearly_invest = monthly_invest * 12

    for age in range(curr_age, 101):
        if age < ret_age:
            status = "Earning"
            rate = w_ret_e
            investment = yearly_invest if age == curr_age else yearly_invest * ((1+step_up)**(age-curr_age))
            expense = 0
        elif age < end_age:
            status = "Retired"
            rate = w_ret_r
            investment = 0
            expense = (monthly_exp_today * 12) * ((1 + inflation) ** (age - curr_age))
        else:
            status = "Dead"
            rate, investment, expense, balance = 0, 0, 0, 0

        start_bal = balance
        if status != "Dead":
            # Growth Calculation: (Start * Return) + New Savings - Expenses
            balance = (start_bal * (1 + rate)) + investment - expense
        
        data.append({"Age": age, "Status": status, "Start": start_bal, "End": balance, "Exp": expense})

    df = pd.DataFrame(data)

    # --- OUTPUT SECTION ---
    st.divider()
    
    # 1. Summary Metrics
    m1, m2, m3 = st.columns(3)
    retirement_corpus = df[df['Age'] == ret_age]['Start'].values[0]
    m1.metric("Retirement Corpus", f"₹{retirement_corpus:,.0f}")
    
    out_of_money = df[(df['Status'] == 'Retired') & (df['End'] < 0)]
    if not out_of_money.empty:
        age_failed = out_of_money.iloc[0]['Age']
        m2.error(f"Runs out at Age {age_failed}")
    else:
        m2.success("Sustainable Plan ✅")
    
    peak_exp = df[df['Status'] == 'Retired']['Exp'].max()
    m3.metric("Max Yearly Expense", f"₹{peak_exp:,.0f}")

    # 2. Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Age'], y=df['End'], name="Wealth", line=dict(color='#2ecc71', width=3), fill='tozeroy'))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Age", yaxis_title="Savings (₹)")
    st.plotly_chart(fig, use_container_width=True)

    # 3. Table
    with st.expander("View Year-by-Year Details"):
        st.dataframe(df.style.format("₹{:,.0f}", subset=["Start", "End", "Exp"]), use_container_width=True)

if __name__ == "__main__":
    main()
