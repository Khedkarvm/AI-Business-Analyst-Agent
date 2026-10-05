# business_analysis.py
# Combine all business analysis results
## Business Analysis → calls → Analytics + Business Insights + Forecasting

from analytics import calculate_kpis
from business_insights import generate_business_insights
from forecasting import generate_forecast


def generate_business_analysis():

    # Run KPI analysis
    kpi_results = calculate_kpis()

    # Run business insights
    insight_results = generate_business_insights()

    # Run forecasting
    forecast_results = generate_forecast()

    # Combine all results
    results = {
        "kpis": kpi_results,
        "insights": insight_results,
        "forecast": forecast_results
    }

    return results


# --------------------------------------------------
# Run directly for testing
# --------------------------------------------------

if __name__ == "__main__":

    results = generate_business_analysis()

    print("BUSINESS ANALYSIS")
    print("=" * 50)

    print("\nKPIs")
    print("-" * 30)

    print(
        f"Total Revenue: "
        f"{results['kpis']['total_revenue']:.2f} BRL"
    )

    print(
        f"Total Orders: "
        f"{results['kpis']['total_orders']}"
    )

    print(
        f"AOV: "
        f"{results['kpis']['average_order_value']:.2f} BRL"
    )

    print("\nBusiness Insights")
    print("-" * 30)

    print(
        f"Revenue Trend: "
        f"{results['insights']['revenue_trend']}"
    )

    print(
        f"Revenue Growth: "
        f"{results['insights']['revenue_growth_percentage']:.2f}%"
    )

    print(
        f"Top Category: "
        f"{results['insights']['top_category']}"
    )

    print("\nForecast")
    print("-" * 30)

    print(
        f"Validation MAE: "
        f"{results['forecast']['validation_mae']:.2f} BRL"
    )

    print(
        results["forecast"]["forecast"]
    )