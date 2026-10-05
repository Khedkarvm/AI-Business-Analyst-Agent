# data_loader.py
## fetch data from postgresql
import pandas as pd
from database import engine


def load_business_data():

    query = """
    SELECT
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        oi.seller_id,
        oi.price,
        oi.freight_value,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        p.product_category_name,
        ct.product_category_name_english
    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    LEFT JOIN products p
        ON oi.product_id = p.product_id

    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name;
    """

    df = pd.read_sql(query, engine)

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    return df


if __name__ == "__main__":

    df = load_business_data()

    print("Business data loaded successfully!")

    print("\nShape:")
    print(df.shape)

    print("\nFirst 5 rows:")
    print(df.head())