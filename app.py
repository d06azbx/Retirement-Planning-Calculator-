import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Retirement Planner", layout="wide")

st.title("🚀 Interactive Retirement Corpus Planner")
st.markdown("Estimate your future wealth by adjusting the variables in the sidebar.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("User Inputs")

curr_age = st.sidebar.slider("Current Age", 18, 70, 30)
retire_age = st.sidebar.slider("Retirement Age", curr_age + 1, 80, 60)
years_to_grow = retire_age - curr_age

st.sidebar.divider()

initial_savings = st.sidebar.number_input("Current Savings ($)", value=10000, step=1000)
monthly_invest = st.sidebar.slider("Monthly Investment ($)", 0, 10000, 1000)
expected_return = st.sidebar.slider("Expected Annual Return (%)", 1.0, 15.0, 8.0)
inflation_rate = st.sidebar.slider("Expected Inflation (%)", 0.0, 10.0, 3.0)

# --- CALCULATIONS ---
# We calculate the "Real" rate of return to see the value in today's purchasing power
# Formula: ((1 + nominal) / (1 + inflation)) - 1
real_return_rate = ((1 + (expected_return / 100)) / (1 + (inflation_rate / 100))) - 1
monthly_real_rate = (1 + real_return_rate) ** (1/12) - 1

data = []
current_corpus = initial_savings

for year in range(years_to_grow + 1):
    age = curr_age + year
    data.append({"Age": age, "Corpus": round(current_corpus, 2)})
    
    # Grow the corpus for the year using monthly compounding
    for month in range(12):
        current_corpus = (current_corpus + monthly_invest) * (1 + monthly_real_rate)

df = pd.DataFrame(data)
final_corpus = df.iloc[-1]["Corpus"]

# --- VISUALIZATION ---
col1, col2 = st.columns([1, 3])

with col1:
    st.metric("Estimated Corpus (Today's Value)", f"${final_corpus:,.0f}")
    st.info(f"""
    **Assumptions:**
    * Years to Retirement: {years_to_grow}
    * Inflation-adjusted Return: {real_return_rate:.2%}
    """)

with col2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Age"], 
        y=df["Corpus"], 
        mode='lines+markers',
        name='Wealth Projection',
        line=dict(color='#1f77b4', width=3),
        hovertemplate="Age %{x}<br>Corpus: $%{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Wealth Growth Over Time",
        xaxis_title="Age",
        yaxis_title="Corpus Value ($)",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- DATA TABLE ---
with st.expander("View Yearly Breakdown"):
    st.table(df)
