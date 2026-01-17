import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page Config
st.set_page_config(page_title="Pro Retirement Planner", layout="wide")

st.title("🎯 Professional Retirement & Fire Planner")
st.markdown("Based on your multi-asset portfolio and step-up investment strategy.")

# --- SIDEBAR: CORE SETTINGS ---
with st.sidebar:
    st.header("⏳ Timeline")
    curr_age = st.number_input("Current Age", value=25)
    retire_age = st.number_input("Retirement Age", value=50)
    life_expectancy = st.number_input("Expenses planned until age", value=85)
    
    st.header("💰 Initial Financials")
    curr_savings = st.number_input("Current Savings ($)", value=0)
    monthly_invest = st.number_input("Starting Monthly Investment ($)", value=10000)
    step_up = st.slider("Annual Step-up in Savings (%)", 0, 20, 5) / 100
    
    st.header("📈 Inflation & Lifestyle")
    inflation = st.slider("Expected Inflation (%)", 0, 10, 5) / 100
    post_retire_exp = st.number_input("Monthly Expense Needed Today ($)", value=50000)

# --- ASSET ALLOCATION & RETURNS ---
st.write("### 🏗️ Portfolio Strategy")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pre-Retirement Returns")
    # Weighted average return based on your Excel logic
    fixed_r = st.slider("Fixed Income (%)", 0.0, 15.0, 7.0) / 100
    lc_r = st.slider("Large Cap (%)", 0.0, 20.0, 12.0) / 100
    mc_r = st.slider("Mid Cap (%)", 0.0, 25.0, 15.0) / 100
    sc_r = st.slider("Small Cap (%)", 0.0, 30.0, 18.0) / 100
    
    # Calculating Weighted Average Return (Simplified for this UI)
    avg_return = (fixed_r * 0.2) + (lc_r * 0.4) + (mc_r * 0.3) + (sc_r * 0.1)

with col2:
    st.subheader("Post-Retirement Strategy")
    pr_return = st.slider("Safe Withdrawal Return (%)", 1.0, 15.0, 12.0) / 100
    st.info(f"Weighted Pre-Retire Return: **{avg_return:.2%}**")

# --- SIMULATION ENGINE ---
ages = list(range(curr_age, life_expectancy + 1))
corpus_data = []
current_corpus = curr_savings
yearly_invest = monthly_invest * 12
current_expense = post_retire_exp * 12

# Inflate expenses to the point of retirement
retirement_expense_at_start = current_expense * ((1 + inflation) ** (retire_age - curr_age))

for age in ages:
    status = "Earning" if age < retire_age else "Retired"
    
    # Calculate returns for the year
    rate = avg_return if status == "Earning" else pr_return
    
    start_bal = current_corpus
    
    if status == "Earning":
        expense = 0
        savings = yearly_invest
        # Apply Step-up for next year
        yearly_invest *= (1 + step_up)
    else:
        expense = retirement_expense_at_start
        savings = 0
        # Inflate expenses for next year
        retirement_expense_at_start *= (1 + inflation)

    current_corpus = (current_corpus + savings - expense) * (1 + rate)
    
    corpus_data.append({
        "Age": age,
        "Status": status,
        "Start Balance": round(start_bal, 2),
        "Outflow/Inflow": round(savings - expense, 2),
        "End Balance": round(max(0, current_corpus), 2)
    })
    
    if current_corpus < 0:
        current_corpus = 0

df = pd.DataFrame(corpus_data)

# --- VISUALIZATION TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Wealth Projection", "📑 Detailed Ledger", "⚙️ Parameters"])

with tab1:
    fig = go.Figure()
    # Fill area for the corpus
    fig.add_trace(go.Scatter(x=df["Age"], y=df["End Balance"], fill='tozeroy', 
                             name='Corpus', line_color='rgb(0, 200, 150)'))
    
    # Vertical line for retirement
    fig.add_vline(x=retire_age, line_dash="dash", line_color="red", annotation_text="Retirement")

    fig.update_layout(title="Total Wealth Evolution", height=500, template="plotly_dark",
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics
    m1, m2, m3 = st.columns(3)
    final_val = df[df['Age'] == retire_age]['End Balance'].values[0]
    m1.metric("Corpus at Retirement", f"${final_val:,.0f}")
    m2.metric("Age Corpus Runs Out", "Never" if df.iloc[-1]['End Balance'] > 0 else df[df['End Balance'] == 0]['Age'].min())
    m3.metric("Monthly Expense at 50", f"${(retirement_expense_at_start/12):,.0f}")

with tab2:
    st.dataframe(df, use_container_width=True)

with tab3:
    st.write("This model accounts for **annual compounding** and **step-up SIP**.")
    st.write("The expense model uses **lifestyle inflation** to adjust your post-retirement needs.")
