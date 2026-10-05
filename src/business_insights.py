# business_insights.py
# This file takes business data from PostgreSQL, calculates important KPIs,
# analyzes revenue trends and product categories, detects low-volume months,
# and generates business-oriented insights.


import pandas as pd
from database import engine
from sqlalchemy import text
from data_loader import load_business_data


def format_category_name(category_name):
    """
    Convert database category names into
    user-friendly business names.
    """

    if not category_name:
        return category_name

    category_name = category_name.replace("_", " ").strip()

    category_mapping = {
        "health beauty": "Health & Beauty",
        "home appliances": "Home Appliances",
        "bed bath table": "Bed Bath & Table",
        "computers accessories": "Computers & Accessories",
        "furniture decor": "Furniture & Decor",
        "sports leisure": "Sports & Leisure",
        "watches gifts": "Watches & Gifts",
        "housewares": "Housewares",
        "auto": "Auto",
        "toys": "Toys",
        "cool stuff": "Cool Stuff"
    }

    return category_mapping.get(
        category_name.lower(),
        category_name.title()
    )


def generate_business_insights():

    # Load business data
    df = load_business_data()

    # --------------------------------------------------
    # Basic KPIs
    # --------------------------------------------------

    # Project definition:
    # Product revenue = SUM(order_items.price)
    total_revenue = df["price"].sum()

    # Count only orders that have order items.
    # This keeps Total Orders consistent with:
    # analytics.py, SQL Agent and Average Order Value.
    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT COUNT(DISTINCT oi.order_id)
                FROM order_items oi
                JOIN orders o
                    ON oi.order_id = o.order_id
                """
            )
        )

        total_orders = result.scalar()

    average_order_value = (
        total_revenue / total_orders
    )

    # --------------------------------------------------
    # Monthly Revenue
    # --------------------------------------------------

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly_revenue = (
        df.groupby("month")["price"]
        .sum()
        .reset_index()
    )

    # --------------------------------------------------
    # Monthly Orders
    # --------------------------------------------------

    monthly_orders = (
        df.groupby("month")["order_id"]
        .nunique()
        .reset_index(name="order_count")
    )

    monthly_analysis = monthly_revenue.merge(
        monthly_orders,
        on="month"
    )

    # --------------------------------------------------
    # Revenue Trend
    # --------------------------------------------------

    VALID_ORDER_THRESHOLD = 100

    valid_months = monthly_analysis[
        monthly_analysis["order_count"]
        >= VALID_ORDER_THRESHOLD
    ].copy()

    recent_3_months = valid_months.tail(3)

    previous_3_months = valid_months.iloc[-6:-3]

    recent_revenue = (
        recent_3_months["price"].sum()
    )

    previous_revenue = (
        previous_3_months["price"].sum()
    )

    # Prevent division by zero
    if previous_revenue != 0:

        revenue_growth_percentage = (
            (recent_revenue - previous_revenue)
            / previous_revenue
        ) * 100

    else:

        revenue_growth_percentage = 0.0

    if revenue_growth_percentage > 0:

        revenue_trend = "increasing"

    elif revenue_growth_percentage < 0:

        revenue_trend = "decreasing"

    else:

        revenue_trend = "stable"

    # --------------------------------------------------
    # Product Category Analysis
    # --------------------------------------------------

    category_analysis = (
        df.groupby(
            "product_category_name_english"
        )
        .agg(
            revenue=("price", "sum"),
            order_count=("order_id", "nunique")
        )
        .reset_index()
    )

    category_analysis["revenue_contribution_%"] = (
        category_analysis["revenue"]
        / total_revenue
    ) * 100

    category_analysis["revenue_per_order"] = (
        category_analysis["revenue"]
        / category_analysis["order_count"]
    )

    category_analysis = category_analysis.sort_values(
        "revenue",
        ascending=False
    )

    # --------------------------------------------------
    # Format Category Names
    # --------------------------------------------------

    category_analysis["category"] = (
        category_analysis[
            "product_category_name_english"
        ]
        .apply(format_category_name)
    )

    # --------------------------------------------------
    # Top Category
    # --------------------------------------------------

    top_category = category_analysis.iloc[0]

    top_category_name = top_category["category"]

    top_category_revenue = (
        top_category["revenue"]
    )

    top_category_orders = (
        top_category["order_count"]
    )

    top_category_contribution = (
        top_category["revenue_contribution_%"]
    )

    top_category_revenue_per_order = (
        top_category["revenue_per_order"]
    )

    # --------------------------------------------------
    # Low-Volume Months
    # --------------------------------------------------

    low_volume_months = monthly_orders[
        monthly_orders["order_count"]
        < VALID_ORDER_THRESHOLD
    ]

    # --------------------------------------------------
    # Business Interpretation
    # --------------------------------------------------

    interpretation = []

    interpretation.append(
        f"Revenue trend is {revenue_trend} over "
        f"the available period."
    )

    interpretation.append(
        f"Revenue changed by "
        f"{revenue_growth_percentage:,.2f}% "
        f"between the previous and recent "
        f"3-month periods."
    )

    interpretation.append(
        f"The top category was {top_category_name}. "
        f"It generated "
        f"{top_category_revenue:,.2f} BRL across "
        f"{top_category_orders:,} orders."
    )

    interpretation.append(
        f"Its revenue contribution is "
        f"{top_category_contribution:,.2f}% "
        f"of total product revenue."
    )

    interpretation.append(
        f"Revenue per order for this category "
        f"is {top_category_revenue_per_order:,.2f} BRL."
    )

    low_volume_count = len(low_volume_months)

    if low_volume_count == 1:
        month_text = "month"
    else:
        month_text = "months"

    interpretation.append(
        f"{low_volume_count} {month_text} have "
        f"fewer than {VALID_ORDER_THRESHOLD} orders "
        f"and should be reviewed before using them "
        f"for trend or forecasting decisions."
    )

    # --------------------------------------------------
    # Return Structured Results
    # --------------------------------------------------

    results = {

        "total_revenue": total_revenue,

        "total_orders": total_orders,

        "average_order_value": average_order_value,

        "revenue_trend": revenue_trend,

        "recent_3_month_revenue": recent_revenue,

        "previous_3_month_revenue": previous_revenue,

        "revenue_growth_percentage":
            revenue_growth_percentage,

        "top_category": top_category_name,

        "top_category_orders":
            top_category_orders,

        "top_category_revenue":
            top_category_revenue,

        "top_category_contribution":
            top_category_contribution,

        "top_category_revenue_per_order":
            top_category_revenue_per_order,

        # Complete category analysis
        "category_analysis":
            category_analysis,

        "low_volume_months":
            low_volume_months,

        "interpretation":
            interpretation
    }

    return results


# --------------------------------------------------
# Run Directly for Testing
# --------------------------------------------------

if __name__ == "__main__":

    results = generate_business_insights()

    print("BUSINESS INSIGHTS")
    print("=" * 50)

    print(
        f"\n1. Total Revenue: "
        f"{results['total_revenue']:,.2f} BRL"
    )

    print(
        f"2. Total Orders: "
        f"{results['total_orders']:,}"
    )

    print(
        f"3. Average Order Value: "
        f"{results['average_order_value']:,.2f} BRL"
    )

    print(
        f"4. Revenue Trend: "
        f"{results['revenue_trend']}"
    )

    print(
        f"5. Recent 3-Month Revenue: "
        f"{results['recent_3_month_revenue']:,.2f} BRL"
    )

    print(
        f"6. Previous 3-Month Revenue: "
        f"{results['previous_3_month_revenue']:,.2f} BRL"
    )

    print(
        f"7. 3-Month Revenue Growth: "
        f"{results['revenue_growth_percentage']:,.2f}%"
    )

    print(
        f"8. Top Product Category: "
        f"{results['top_category']}"
    )

    print(
        f"9. Top Category Orders: "
        f"{results['top_category_orders']:,}"
    )

    print(
        f"10. Top Category Revenue: "
        f"{results['top_category_revenue']:,.2f} BRL"
    )

    print(
        f"11. Top Category Contribution: "
        f"{results['top_category_contribution']:,.2f}%"
    )

    print(
        f"12. Top Category Revenue per Order: "
        f"{results['top_category_revenue_per_order']:,.2f} BRL"
    )

    print("\n13. Category Analysis:")

    print(
        results["category_analysis"][
            [
                "category",
                "revenue",
                "order_count",
                "revenue_contribution_%",
                "revenue_per_order"
            ]
        ].head(10)
    )

    print("\n14. Low-Volume Months:")

    print(
        results["low_volume_months"]
    )

    print("\nBUSINESS INTERPRETATION")
    print("=" * 50)

    for point in results["interpretation"]:

        print(f"- {point}")