import matplotlib.pyplot as plt
import pandas as pd


def plot_monthly_revenue(formatted_output):

    monthly_data = formatted_output["monthly_revenue"]

    df = pd.DataFrame(monthly_data)

    if df.empty:
        print("No monthly revenue data available.")
        return

    df["month"] = pd.to_datetime(df["month"])

    df = df.sort_values("month")

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["month"],
        df["price"],
        marker="o"
    )

    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (BRL)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    # Save chart
    output_path = "../data/processed/monthly_revenue_trend.png"

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    print(f"\nChart saved successfully:")
    print(output_path)

    plt.close()


def plot_revenue_forecast(formatted_output):

    monthly_data = formatted_output["monthly_revenue"]
    forecast_data = formatted_output["forecast"]["values"]

    actual_df = pd.DataFrame(monthly_data)
    forecast_df = pd.DataFrame(forecast_data)

    if actual_df.empty or forecast_df.empty:
        print("Forecast data is not available.")
        return

    actual_df["month"] = pd.to_datetime(actual_df["month"])
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    actual_df = actual_df.sort_values("month")
    forecast_df = forecast_df.sort_values("ds")

    plt.figure(figsize=(12, 6))

    # Historical revenue
    plt.plot(
        actual_df["month"],
        actual_df["price"],
        marker="o",
        label="Actual Revenue"
    )

    # Forecast revenue
    plt.plot(
        forecast_df["ds"],
        forecast_df["yhat"],
        marker="o",
        label="Forecast Revenue"
    )

    # Forecast uncertainty range
    plt.fill_between(
        forecast_df["ds"],
        forecast_df["yhat_lower"],
        forecast_df["yhat_upper"],
        alpha=0.2,
        label="Forecast Range"
    )

    plt.title("Revenue Forecast")
    plt.xlabel("Month")
    plt.ylabel("Revenue (BRL)")

    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()

    output_path = "../data/processed/revenue_forecast.png"

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    print("\nForecast chart saved successfully:")
    print(output_path)

    plt.close()


def plot_revenue_forecast(formatted_output):

    monthly_data = formatted_output["monthly_revenue"]
    forecast_data = formatted_output["forecast"]["values"]

    actual_df = pd.DataFrame(monthly_data)
    forecast_df = pd.DataFrame(forecast_data)

    if actual_df.empty or forecast_df.empty:
        print("Forecast data is not available.")
        return

    actual_df["month"] = pd.to_datetime(actual_df["month"])
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    actual_df = actual_df.sort_values("month")
    forecast_df = forecast_df.sort_values("ds")

    plt.figure(figsize=(12, 6))

    # Historical revenue
    plt.plot(
        actual_df["month"],
        actual_df["price"],
        marker="o",
        label="Actual Revenue"
    )

    # Forecast revenue
    plt.plot(
        forecast_df["ds"],
        forecast_df["yhat"],
        marker="o",
        label="Forecast Revenue"
    )

    # Forecast uncertainty range
    plt.fill_between(
        forecast_df["ds"],
        forecast_df["yhat_lower"],
        forecast_df["yhat_upper"],
        alpha=0.2,
        label="Forecast Range"
    )

    plt.title("Revenue Forecast")
    plt.xlabel("Month")
    plt.ylabel("Revenue (BRL)")

    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()

    output_path = "../data/processed/revenue_forecast.png"

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    print("\nForecast chart saved successfully:")
    print(output_path)

    plt.close()


if __name__ == "__main__":

    from analysis_agent import analysis_agent
    from output_formatter import format_analysis_output

    # Run Analysis Agent
    result = analysis_agent(
        "Analyze the overall business performance."
    )

    # Convert result into structured output
    formatted_output = format_analysis_output(result)

    # Create visualization
    plot_monthly_revenue(formatted_output)

    plot_revenue_forecast(formatted_output)