# analytics.py
## calculate basic buisness KPIs and trend analysis

import pandas as pd
from database import engine
from sqlalchemy import text
from data_loader import load_business_data


def calculate_kpis():

    # Load business data
    df = load_business_data()

    # -----------------------------
    # Basic KPIs
    # -----------------------------

    total_revenue = df["price"].sum()

    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT COUNT(DISTINCT oi.order_id)
                FROM order_items oi
                JOIN orders o
                    ON oi.order_id = o.order_id
            """)
        )
        total_orders = result.scalar()
        
    average_order_value = (
        total_revenue / total_orders
    )

    # -----------------------------
    # Monthly Revenue
    # -----------------------------

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly_revenue = (
        df.groupby("month")["price"]
        .sum()
        .reset_index()
    )

    monthly_revenue["revenue_growth_%"] = (
        monthly_revenue["price"].pct_change() * 100
    )

    # -----------------------------
    # Revenue Anomaly Detection
    # -----------------------------

    Q1 = monthly_revenue["price"].quantile(0.25)

    Q3 = monthly_revenue["price"].quantile(0.75)

    IQR = Q3 - Q1

    lower_limit = Q1 - 1.5 * IQR

    upper_limit = Q3 + 1.5 * IQR

    monthly_revenue["anomaly"] = (
        (monthly_revenue["price"] < lower_limit)
        |
        (monthly_revenue["price"] > upper_limit)
    )

    anomalies = monthly_revenue[
        monthly_revenue["anomaly"]
    ]

    # -----------------------------
    # Low-Volume Month Detection
    # -----------------------------

    monthly_orders = (
        df.groupby("month")["order_id"]
        .nunique()
        .reset_index(name="order_count")
    )

    LOW_VOLUME_THRESHOLD = 100

    monthly_orders["low_volume"] = (
        monthly_orders["order_count"]
        < LOW_VOLUME_THRESHOLD
    )

    low_volume_months = monthly_orders[
        monthly_orders["low_volume"]
    ]

    # -----------------------------
    # Return structured results
    # -----------------------------

    results = {

        "total_revenue": total_revenue,

        "total_orders": total_orders,

        "average_order_value": average_order_value,

        "monthly_revenue": monthly_revenue,

        "anomalies": anomalies,

        "low_volume_months": low_volume_months

    }

    return results


# -----------------------------------
# Run directly for testing
# -----------------------------------

if __name__ == "__main__":

    results = calculate_kpis()

    print("Business KPIs")
    print("-" * 30)

    print(
        f"Total Revenue: "
        f"{results['total_revenue']:.2f} BRL"
    )

    print(
        f"Total Orders: "
        f"{results['total_orders']}"
    )

    print(
        f"Average Order Value: "
        f"{results['average_order_value']:.2f} BRL"
    )

    print("\nRevenue Anomaly Detection")
    print("-" * 30)

    print(results["anomalies"])

    print("\nLow-Volume Months")
    print("-" * 30)

    print(results["low_volume_months"])