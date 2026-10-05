METRIC_DEFINITIONS = {

    "product_revenue": {
        "description": "Total value of products sold.",
        "formula": "SUM(order_items.price)",
        "table": "order_items",
        "column": "price",
        "unit": "BRL"
    },

    "total_payment_value": {
        "description": "Total payment value recorded for orders.",
        "formula": "SUM(payments.payment_value)",
        "table": "payments",
        "column": "payment_value",
        "unit": "BRL"
    },

    "total_orders": {
        "description": "Total number of unique orders.",
        "formula": "COUNT(DISTINCT orders.order_id)",
        "table": "orders",
        "column": "order_id",
        "unit": "count"
    },

    "total_customers": {
        "description": "Total number of unique customers.",
        "formula": "COUNT(DISTINCT customers.customer_unique_id)",
        "table": "customers",
        "column": "customer_unique_id",
        "unit": "count"
    },

    "average_order_value": {
        "description": "Average product revenue generated per order.",
        "formula": "product_revenue / total_orders",
        "unit": "BRL"
    },

    "average_review_score": {
        "description": "Average customer review score.",
        "formula": "AVG(order_reviews.review_score)",
        "table": "order_reviews",
        "column": "review_score",
        "unit": "score"
    }
}