# data.quality.py 
## used for data quality check

import pandas as pd
from database import engine

# Load order dates
query = """
SELECT
    order_id,
    order_purchase_timestamp
FROM orders;
"""

df = pd.read_sql(query, engine)

# Convert date column to datetime
df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)

# Get months present in the dataset
months = (
    df["order_purchase_timestamp"]
    .dt.to_period("M")
    .sort_values()
    .unique()
)

# Create the complete expected monthly range
expected_months = pd.period_range(
    start=months.min(),
    end=months.max(),
    freq="M"
)

# check 1: Find missing months
missing_months = expected_months.difference(months)

print("Data Quality Check")
print("-" * 30)

print(f"Data starts: {months.min()}")
print(f"Data ends:   {months.max()}")

print("\nMissing months:")

if len(missing_months) == 0:
    print("No missing months found.")
else:
    for month in missing_months:
        print(month)


# Check 2: Monthly Order Volume

df["month"] = df["order_purchase_timestamp"].dt.to_period("M")

monthly_orders = (
    df.groupby("month")["order_id"]
    .nunique()
    .reset_index(name="order_count")
)

print("\nMonthly Order Volume")
print("-" * 30)

print(monthly_orders)



# Check 3: Missing Values

print("\nMissing Values")
print("-" * 30)

missing_values = df.isnull().sum()

print(missing_values)



# Check 4: Duplicate Orders

print("\nDuplicate Orders")
print("-" * 30)

duplicate_orders = df["order_id"].duplicated().sum()

print(f"Duplicate order IDs: {duplicate_orders}")



# Check 5: Duplicate Order Items

items_query = """
SELECT
    order_id,
    order_item_id
FROM order_items;
"""

items_df = pd.read_sql(items_query, engine)

print("\nDuplicate Order Items")
print("-" * 30)

duplicate_items = items_df.duplicated(
    subset=["order_id", "order_item_id"]
).sum()

print(f"Duplicate order-item records: {duplicate_items}")




# Check 6: Invalid Price Values

print("\nInvalid Price Values")
print("-" * 30)

invalid_price_query = """
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE price IS NULL) AS null_prices,
    COUNT(*) FILTER (WHERE price <= 0) AS non_positive_prices
FROM order_items;
"""

price_check = pd.read_sql(invalid_price_query, engine)

print(price_check)



# Check 7: Orphan Order Items
## order item that refers to an order that does not exist in the orders table. (not exact mapping of order id in order_item id)

orphan_query = """
SELECT COUNT(*) AS orphan_order_items
FROM order_items oi
LEFT JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;      
"""
# order_id is null means no matching then we count(*) as orphan_order_items

orphan_check = pd.read_sql(orphan_query, engine)

print("\nOrphan Order Items")
print("-" * 30)

print(orphan_check)




# Check 8: Order Status by Period

status_query = """
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY month, order_status
ORDER BY month, order_status;
"""

status_df = pd.read_sql(status_query, engine)

print("\nOrder Status by Month")
print("-" * 30)

print(status_df)



# -----------------------------
# Check 9: Orders vs Revenue
# -----------------------------

revenue_query = """
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    COUNT(DISTINCT o.order_id) AS order_count,
    COALESCE(SUM(oi.price), 0) AS revenue
FROM orders o
LEFT JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
"""

revenue_check = pd.read_sql(revenue_query, engine)

print("\nMonthly Orders vs Revenue")
print("-" * 30)

print(revenue_check)