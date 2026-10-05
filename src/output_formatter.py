
import pandas as pd


# --------------------------------------------------
# Convert pandas / NumPy values into normal Python
# --------------------------------------------------

def _clean_value(value):

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, pd.Period):
        return str(value)

    if hasattr(value, "item"):
        return value.item()

    return value


# --------------------------------------------------
# Convert DataFrame into JSON-friendly records
# --------------------------------------------------

def _records(df):

    if df is None or df.empty:
        return []

    records = df.to_dict(orient="records")

    cleaned_records = []

    for row in records:

        cleaned_row = {
            key: _clean_value(value)
            for key, value in row.items()
        }

        cleaned_records.append(cleaned_row)

    return cleaned_records


# --------------------------------------------------
# Format complete Analysis Agent output
# --------------------------------------------------

def format_analysis_output(agent_result):

    analysis = agent_result["analysis"]

    kpis = analysis["kpis"]
    insights = analysis["insights"]
    forecast = analysis["forecast"]

    formatted_output = {

        # ------------------------------------------
        # Concise summary for Response Agent
        # ------------------------------------------

        "summary": {

            "revenue": _clean_value(
                kpis["total_revenue"]
            ),

            "orders": int(
                kpis["total_orders"]
            ),

            "aov": _clean_value(
                kpis["average_order_value"]
            ),

            "revenue_trend": insights["revenue_trend"],

            "growth_percentage": _clean_value(
                insights["revenue_growth_percentage"]
            ),

            "recent_3_month_revenue": _clean_value(
                insights["recent_3_month_revenue"]
            ),

            "previous_3_month_revenue": _clean_value(
                insights["previous_3_month_revenue"]
            ),

            "top_category": insights["top_category"],

            "top_category_orders": int(
                insights["top_category_orders"]
            ),

            "top_category_revenue": _clean_value(
                insights["top_category_revenue"]
            ),

            "top_category_contribution": _clean_value(
                insights["top_category_contribution"]
            ),

            "top_category_revenue_per_order": _clean_value(
                insights["top_category_revenue_per_order"]
            ),

            "forecast_validation_mae": _clean_value(
                forecast["validation_mae"]
            ),

            "missing_months": [
                str(month.date())
                for month in forecast["missing_months"]
            ],

            "low_volume_month_count": len(
                kpis["low_volume_months"]
            )
        },


        # ------------------------------------------
        # KPI section
        # ------------------------------------------

        "kpis": {

            "revenue": _clean_value(
                kpis["total_revenue"]
            ),

            "orders": int(
                kpis["total_orders"]
            ),

            "aov": _clean_value(
                kpis["average_order_value"]
            )
        },


        # ------------------------------------------
        # Revenue trend
        # ------------------------------------------

        "trend": {

            "direction": insights["revenue_trend"],

            "growth_percentage": _clean_value(
                insights["revenue_growth_percentage"]
            ),

            "recent_3_month_revenue": _clean_value(
                insights["recent_3_month_revenue"]
            ),

            "previous_3_month_revenue": _clean_value(
                insights["previous_3_month_revenue"]
            )
        },


        # ------------------------------------------
        # Top category
        # ------------------------------------------

        "category": {

            "name": insights["top_category"],

            "orders": int(
                insights["top_category_orders"]
            ),

            "revenue": _clean_value(
                insights["top_category_revenue"]
            ),

            "contribution_percentage": _clean_value(
                insights["top_category_contribution"]
            ),

            "revenue_per_order": _clean_value(
                insights["top_category_revenue_per_order"]
            )
        },


        # ------------------------------------------
        # Category analysis
        # Used by Streamlit category chart
        # ------------------------------------------

        "category_analysis": _records(
            insights["category_analysis"]
        ),


        # ------------------------------------------
        # Monthly revenue data
        # Used by Streamlit chart
        # ------------------------------------------

        "monthly_revenue": _records(
            kpis["monthly_revenue"]
        ),


        # ------------------------------------------
        # Revenue anomalies
        # ------------------------------------------

        "anomalies": _records(
            kpis["anomalies"]
        ),


        # ------------------------------------------
        # Low-volume months
        # ------------------------------------------

        "low_volume_months": _records(
            kpis["low_volume_months"]
        ),


        # ------------------------------------------
        # Forecast
        # Used by Streamlit forecast chart
        # ------------------------------------------

        "forecast": {

            "values": _records(
                forecast["forecast"]
            ),

            "validation_mae": _clean_value(
                forecast["validation_mae"]
            ),

            "missing_months": [
                str(month.date())
                for month in forecast["missing_months"]
            ]
        },


        # ------------------------------------------
        # Business interpretation
        # ------------------------------------------

        "interpretation": insights["interpretation"]
    }

    return formatted_output


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    from analysis_agent import analysis_agent

    result = analysis_agent(
        "Analyze the overall business performance."
    )

    formatted = format_analysis_output(result)

    print("\nSTRUCTURED OUTPUT")
    print("=" * 50)

    print("\nSummary")
    print("-" * 30)
    print(formatted["summary"])

    print("\nKPIs")
    print("-" * 30)
    print(formatted["kpis"])

    print("\nTrend")
    print("-" * 30)
    print(formatted["trend"])

    print("\nTop Category")
    print("-" * 30)
    print(formatted["category"])

    print("\nCategory Analysis")
    print("-" * 30)

    for row in formatted["category_analysis"][:10]:
        print(row)

    print("\nMonthly Revenue Records:")
    print(len(formatted["monthly_revenue"]))

    print("\nAnomaly Records:")
    print(len(formatted["anomalies"]))

    print("\nLow-Volume Months:")
    print(formatted["low_volume_months"])

    print("\nForecast:")
    print("-" * 30)
    print(formatted["forecast"])

    print("\nInterpretation:")
    print("-" * 30)

    for item in formatted["interpretation"]:
        print("-", item)

