import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="UPI Expense Intelligence",
    page_icon="💰",
    layout="wide"
)

st.title("Smart UPI Expense Intelligence System")
st.write("Upload your PhonePe / GPay transaction CSV and get instant financial insights")

with st.expander("How to download your transaction CSV from PhonePe / GPay"):
    st.write("""
    **PhonePe:**
    1. Open PhonePe app
    2. Go to History
    3. Click Download Statement
    4. Select date range and download CSV

    **Google Pay:**
    1. Open GPay app
    2. Go to Settings
    3. Click Download transaction history
    4. Download CSV file
    """)

uploaded_file = st.file_uploader(
    "Upload your UPI transaction CSV",
    type=['csv']
)

if uploaded_file:

    with st.spinner("Analyzing your transactions..."):


        response = requests.post(
            "http://localhost:8000/upload",
            files={"file": uploaded_file}
        )
        result = response.json()
        session_id = result['session_id']

        analysis = requests.post(
            "http://localhost:8000/analysis",
            json={"session_id": session_id}
        ).json()

    st.success(f"Analyzed {result['total_transactions']} transactions successfully!")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Income",
        f"Rs {analysis['total_income']:,.0f}"
    )
    col2.metric(
        "Total Expenses",
        f"Rs {analysis['total_expense']:,.0f}"
    )
    col3.metric(
        "Savings",
        f"Rs {analysis['savings']:,.0f}",
        delta="Good" if analysis['savings'] > 0 else "Overspent"
    )
    col4.metric(
        "Financial Health Score",
        f"{analysis['health_score']} / 100"
    )

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Spending by Category")

   
        categories = list(analysis['category_spending'].keys())
        amounts = list(analysis['category_spending'].values())

        fig_pie = px.pie(
            values=amounts,
            names=categories,
            title="Where is your money going?",
            hole=0.4  
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("Income vs Expenses Flow")

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=["Income"] + categories + ["Savings"],
                color=["#1D9E75"] + ["#378ADD"] * len(categories) + ["#639922"]
            ),
            link=dict(
                source=[0] * len(categories),
                target=list(range(1, len(categories) + 1)),
                value=amounts
            )
        )])
        fig_sankey.update_layout(title_text="Money Flow Sankey Chart", height=400)
        st.plotly_chart(fig_sankey, use_container_width=True)

    st.divider()

    col_score, col_tips = st.columns(2)

    with col_score:
        st.subheader("Financial Health Score")

        score = analysis['health_score']

        if score >= 75:
            color = "green"
            label = "Excellent"
        elif score >= 50:
            color = "orange"
            label = "Average"
        else:
            color = "red"
            label = "Needs Improvement"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': f"Score: {label}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': '#FCEBEB'},
                    {'range': [40, 70], 'color': '#FAEEDA'},
                    {'range': [70, 100], 'color': '#EAF3DE'}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_tips:
        st.subheader("Personalized Action Tips")
        for i, tip in enumerate(analysis['tips']):
            st.info(f"Tip {i+1}: {tip}")

    st.divider()

    st.subheader("Money Leaks Detected")
    st.write("These are recurring small payments you may have forgotten about:")

    if analysis['money_leaks']:
        leaks_df = pd.DataFrame(analysis['money_leaks'])
        leaks_df.columns = ['Description', 'Times', 'Total Spent (Rs)', 'Avg Amount (Rs)']
        st.dataframe(leaks_df, use_container_width=True)
    else:
        st.success("No money leaks detected! Great job tracking your expenses.")