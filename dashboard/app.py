
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.append(str(SRC_PATH))


# --------------------------------------------------
# Import project modules
# --------------------------------------------------

from analysis_agent import analysis_agent
from output_formatter import format_analysis_output
from agent_workflow import app


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📊 AI Business Analyst")

st.write(
    "Business performance dashboard powered by "
    "PostgreSQL, Python, AI agents and forecasting."
)


# --------------------------------------------------
# Load business analysis
# --------------------------------------------------

@st.cache_data
def load_business_analysis():

    result = analysis_agent(
        "Analyze the overall business performance."
    )

    return format_analysis_output(result)


data = load_business_analysis()


# --------------------------------------------------
# KPI section
# --------------------------------------------------

st.subheader("Business KPIs")

kpi1, kpi2, kpi3 = st.columns(3)


with kpi1:

    st.metric(
        "Total Revenue",
        f"{data['kpis']['revenue']:,.2f} BRL"
    )


with kpi2:

    st.metric(
        "Total Orders",
        f"{data['kpis']['orders']:,}"
    )


with kpi3:

    st.metric(
        "Average Order Value",
        f"{data['kpis']['aov']:,.2f} BRL"
    )


# --------------------------------------------------
# AI Business Question
# --------------------------------------------------

st.subheader("🤖 Ask the AI Business Analyst")

question = st.text_input(
    "Ask a business question:",
    placeholder="Example: What is the total revenue?",
    key="business_question"
)

if st.button("Analyze Question", type="primary"):

    if question.strip():

        with st.spinner("Analyzing your question..."):

            result = app.invoke(
                {
                    "question": question
                }
            )

        st.markdown("### 💡 AI Answer")

        final_answer = result.get(
            "result",
            "No answer was generated."
        )

        st.markdown(final_answer)

        # --------------------------------------------------
        # Optional technical details
        # --------------------------------------------------

        route = result.get("route")

        if route == "SQL_AGENT":

            with st.expander("🔍 Show technical details"):

                technical_details = result.get(
                    "technical_details"
                )

                if technical_details:

                    st.markdown("**SQL Agent Output**")

                    st.json(
                        technical_details
                    )

                else:

                    st.info(
                        "No technical details available."
                    )

    else:

        st.warning(
            "Please enter a business question."
        )


# --------------------------------------------------
# Monthly Revenue Trend
# --------------------------------------------------

st.subheader("Monthly Revenue Trend")

monthly_df = pd.DataFrame(
    data["monthly_revenue"]
)

if not monthly_df.empty:

    monthly_df["month"] = pd.to_datetime(
        monthly_df["month"]
    )

    monthly_df = monthly_df.sort_values(
        "month"
    )

    revenue_chart = (
        alt.Chart(monthly_df)
        .mark_line(point=True)
        .encode(

            x=alt.X(
                "month:T",
                title="Month",
                axis=alt.Axis(
                    format="%b %Y",
                    labelAngle=-45,
                    tickCount=8
                )
            ),

            y=alt.Y(
                "price:Q",
                title="Revenue (BRL)"
            ),

            tooltip=[
                alt.Tooltip(
                    "month:T",
                    title="Month",
                    format="%b %Y"
                ),

                alt.Tooltip(
                    "price:Q",
                    title="Revenue",
                    format=",.2f"
                )
            ]
        )
        .properties(
            height=350
        )
    )

    st.altair_chart(
        revenue_chart,
        use_container_width=True
    )


# --------------------------------------------------
# Revenue Forecast
# --------------------------------------------------

st.subheader("Revenue Forecast")

forecast_df = pd.DataFrame(
    data["forecast"]["values"]
)

if not forecast_df.empty:

    # --------------------------------------------------
    # Convert date column
    # --------------------------------------------------

    forecast_df["ds"] = pd.to_datetime(
        forecast_df["ds"]
    )

    # --------------------------------------------------
    # Create one row per month
    # --------------------------------------------------

    forecast_df["month"] = (
        forecast_df["ds"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Keep one forecast value per month

    forecast_df = (
        forecast_df
        .sort_values("ds")
        .groupby("month", as_index=False)
        .first()
    )

    # --------------------------------------------------
    # Forecast confidence range
    # --------------------------------------------------

    forecast_area = (
        alt.Chart(forecast_df)
        .mark_area(opacity=0.2)
        .encode(

            x=alt.X(
                "month:T",
                title="Month",
                axis=alt.Axis(
                    format="%b %Y",
                    labelAngle=-45,
                    tickCount=6
                )
            ),

            y=alt.Y(
                "yhat_lower:Q",
                title="Revenue (BRL)"
            ),

            y2="yhat_upper:Q",

            tooltip=[
                alt.Tooltip(
                    "month:T",
                    title="Month",
                    format="%b %Y"
                ),

                alt.Tooltip(
                    "yhat:Q",
                    title="Forecast",
                    format=",.2f"
                ),

                alt.Tooltip(
                    "yhat_lower:Q",
                    title="Lower",
                    format=",.2f"
                ),

                alt.Tooltip(
                    "yhat_upper:Q",
                    title="Upper",
                    format=",.2f"
                )
            ]
        )
    )

    # --------------------------------------------------
    # Forecast line
    # --------------------------------------------------

    forecast_line = (
        alt.Chart(forecast_df)
        .mark_line(point=True)
        .encode(

            x=alt.X(
                "month:T",
                title="Month",
                axis=alt.Axis(
                    format="%b %Y",
                    labelAngle=-45,
                    tickCount=6
                )
            ),

            y=alt.Y(
                "yhat:Q",
                title="Revenue (BRL)"
            ),

            tooltip=[
                alt.Tooltip(
                    "month:T",
                    title="Month",
                    format="%b %Y"
                ),

                alt.Tooltip(
                    "yhat:Q",
                    title="Forecast",
                    format=",.2f"
                )
            ]
        )
    )

    # --------------------------------------------------
    # Combine charts
    # --------------------------------------------------

    forecast_chart = (
        forecast_area + forecast_line
    ).properties(
        height=350
    )

    st.altair_chart(
        forecast_chart,
        use_container_width=True
    )

    # --------------------------------------------------
    # Forecast validation
    # --------------------------------------------------

    st.caption(
        f"Forecast validation MAE: "
        f"{data['forecast']['validation_mae']:,.2f} BRL"
    )


# --------------------------------------------------
# Category Analysis
# --------------------------------------------------

st.subheader("Category Analysis")

category_df = pd.DataFrame(
    data["category_analysis"]
)

if not category_df.empty:

    # --------------------------------------------------
    # Select top 10 categories by revenue
    # --------------------------------------------------

    category_df = (
        category_df
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(10)
        .sort_values(
            "revenue",
            ascending=True
        )
    )

    # --------------------------------------------------
    # Category revenue chart
    # --------------------------------------------------

    category_chart = (
        alt.Chart(category_df)
        .mark_bar()
        .encode(

            x=alt.X(
                "revenue:Q",
                title="Revenue (BRL)"
            ),

            y=alt.Y(
                "category:N",
                title="Product Category",
                sort=None
            ),

            tooltip=[
                alt.Tooltip(
                    "category:N",
                    title="Category"
                ),

                alt.Tooltip(
                    "revenue:Q",
                    title="Revenue",
                    format=",.2f"
                ),

                alt.Tooltip(
                    "order_count:Q",
                    title="Orders",
                    format=","
                ),

                alt.Tooltip(
                    "revenue_contribution_%:Q",
                    title="Revenue Contribution",
                    format=".2f"
                )
            ]
        )
        .properties(
            height=400
        )
    )

    st.altair_chart(
        category_chart,
        use_container_width=True
    )

else:

    st.info(
        "No category analysis data available."
    )


# --------------------------------------------------
# Data Quality
# --------------------------------------------------

st.subheader("Data Quality")

low_volume = data["low_volume_months"]

if low_volume:

    st.write(
        "Months with fewer than 100 orders:"
    )

    low_volume_df = pd.DataFrame(
        low_volume
    )

    low_volume_df["month"] = (
        low_volume_df["month"].astype(str)
    )

    low_volume_df["order_count"] = (
        low_volume_df["order_count"].astype(int)
    )

    low_volume_df = low_volume_df[
        ["month", "order_count"]
    ]

    st.table(
        low_volume_df
    )

else:

    st.write(
        "No low-volume months detected."
    )


missing_months = data["forecast"]["missing_months"]

if missing_months:

    st.write(
        "Missing months in the historical data:"
    )

    formatted_missing_months = []

    for month in missing_months:

        formatted_month = pd.to_datetime(
            month
        ).strftime("%B %Y")

        formatted_missing_months.append(
            formatted_month
        )

    st.write(
        ", ".join(formatted_missing_months)
    )

