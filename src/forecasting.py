# forecasting.py
# Forecast historical monthly revenue using Prophet

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from data_loader import load_business_data
from prophet import Prophet


def generate_forecast():

    # --------------------------------------------------
    # Load business data
    # --------------------------------------------------

    df = load_business_data()

    # Convert timestamp to datetime
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    # --------------------------------------------------
    # Create monthly revenue
    # --------------------------------------------------

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_revenue = (
        df.groupby("month")["price"]
        .sum()
        .reset_index(name="revenue")
    )

    # --------------------------------------------------
    # Prepare data for Prophet
    # --------------------------------------------------

    forecast_df = monthly_revenue.rename(
        columns={
            "month": "ds",
            "revenue": "y"
        }
    )

    # --------------------------------------------------
    # Create continuous monthly date range
    # --------------------------------------------------

    full_months = pd.date_range(
        start=forecast_df["ds"].min(),
        end=forecast_df["ds"].max(),
        freq="MS"
    )

    # Find missing months
    missing_months = full_months.difference(
        forecast_df["ds"]
    )

    # Add missing months
    forecast_df = (
        forecast_df
        .set_index("ds")
        .reindex(full_months)
        .rename_axis("ds")
        .reset_index()
    )

    # Fill missing revenue
    forecast_df["y"] = forecast_df["y"].fillna(0)

    # --------------------------------------------------
    # Forecast Validation
    # --------------------------------------------------

    TEST_MONTHS = 3

    train_df = forecast_df[
        forecast_df["ds"] < "2018-01-01"
    ].copy()

    test_df = forecast_df[
        (forecast_df["ds"] >= "2018-01-01")
        &
        (forecast_df["ds"] <= "2018-03-01")
    ].copy()

    # Train validation model
    validation_model = Prophet()

    validation_model.fit(train_df)

    # Create future dates
    future_test = validation_model.make_future_dataframe(
        periods=TEST_MONTHS,
        freq="MS"
    )

    validation_forecast = validation_model.predict(
        future_test
    )

    # Get test predictions
    predictions = validation_forecast[
        validation_forecast["ds"].isin(test_df["ds"])
    ][["ds", "yhat"]]

    # Compare actual and predicted
    comparison = test_df.merge(
        predictions,
        on="ds"
    )

    comparison["error"] = (
        comparison["y"] - comparison["yhat"]
    )

    comparison["absolute_error"] = (
        comparison["error"].abs()
    )

    # Calculate MAE
    mae = comparison["absolute_error"].mean()

    # --------------------------------------------------
    # Train final Prophet model
    # --------------------------------------------------

    model = Prophet()

    model.fit(forecast_df)

    # --------------------------------------------------
    # Forecast next 6 months
    # --------------------------------------------------

    future = model.make_future_dataframe(
        periods=6,
        freq="MS"
    )

    forecast = model.predict(future)

    future_forecast = forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].tail(6)

    # --------------------------------------------------
    # Save forecast
    # --------------------------------------------------

    project_root = Path(__file__).resolve().parent.parent

    output_path = (
        project_root
        / "data"
        / "processed"
        / "revenue_forecast.csv"
    )

    future_forecast.to_csv(
        output_path,
        index=False
    )

    # --------------------------------------------------
    # Return structured results
    # --------------------------------------------------

    results = {

        "forecast": future_forecast,

        "validation_mae": mae,

        "missing_months": missing_months,

        "forecast_file": str(output_path)

    }

    return results


# --------------------------------------------------
# Run directly for testing
# --------------------------------------------------

if __name__ == "__main__":

    results = generate_forecast()

    print("FORECASTING RESULTS")
    print("=" * 50)

    print("\nMissing Months:")
    print(results["missing_months"])

    print("\nValidation MAE:")
    print(
        f"{results['validation_mae']:.2f} BRL"
    )

    print("\nRevenue Forecast:")
    print(
        results["forecast"]
    )

    print("\nForecast saved successfully!")

    print(
        f"File: {results['forecast_file']}"
    )

    # --------------------------------------------------
    # Plot forecast
    # --------------------------------------------------

    df = load_business_data()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_revenue = (
        df.groupby("month")["price"]
        .sum()
        .reset_index(name="revenue")
    )

    plot_df = monthly_revenue.rename(
        columns={
            "month": "ds",
            "revenue": "y"
        }
    )

    full_months = pd.date_range(
        start=plot_df["ds"].min(),
        end=plot_df["ds"].max(),
        freq="MS"
    )

    plot_df = (
        plot_df
        .set_index("ds")
        .reindex(full_months)
        .rename_axis("ds")
        .reset_index()
    )

    plot_df["y"] = plot_df["y"].fillna(0)

    plot_model = Prophet()

    plot_model.fit(plot_df)

    future = plot_model.make_future_dataframe(
        periods=6,
        freq="MS"
    )

    plot_forecast = plot_model.predict(
        future
    )

    fig = plot_model.plot(
        plot_forecast
    )

    plt.title("Monthly Revenue Forecast")
    plt.xlabel("Month")
    plt.ylabel("Revenue (BRL)")

    plt.tight_layout()
    plt.show()
