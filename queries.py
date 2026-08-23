"""
Analytical SQL queries against the Turso (libSQL) orders database.
Each function returns (columns, rows) so callers (Streamlit, notebooks,
scripts) can turn results into a DataFrame however they like.
"""

import os
import libsql_client

DB_URL = os.environ.get("TURSO_DATABASE_URL", "file:local.db")
AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")


def get_client():
    if AUTH_TOKEN:
        return libsql_client.create_client_sync(url=DB_URL, auth_token=AUTH_TOKEN)
    return libsql_client.create_client_sync(url=DB_URL)


def run(client, sql, params=()):
    result = client.execute(sql, params)
    return result.columns, result.rows


# --- Revenue over time -------------------------------------------------

MONTHLY_REVENUE_SQL = """
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(total_amount)             AS revenue,
    COUNT(*)                      AS num_orders
FROM orders
GROUP BY month
ORDER BY month;
"""

# --- Top products --------------------------------------------------------

TOP_PRODUCTS_SQL = """
SELECT
    p.name,
    p.category,
    SUM(o.quantity)      AS units_sold,
    SUM(o.total_amount)  AS revenue
FROM orders o
JOIN products p ON p.product_id = o.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;
"""

# --- Revenue by region -----------------------------------------------------

REVENUE_BY_REGION_SQL = """
SELECT
    c.region,
    SUM(o.total_amount) AS revenue,
    COUNT(DISTINCT o.customer_id) AS active_customers
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.region
ORDER BY revenue DESC;
"""

# --- Customer order rank + retention (uses a window function) --------------

CUSTOMER_ORDER_RANK_SQL = """
SELECT
    customer_id,
    order_id,
    order_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id ORDER BY order_date
    ) AS order_sequence
FROM orders;
"""

REPEAT_PURCHASE_RATE_SQL = """
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    CAST(SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) AS REAL)
        / COUNT(*) AS repeat_purchase_rate,
    COUNT(*) AS total_customers_with_orders
FROM order_counts;
"""


def monthly_revenue(client):
    return run(client, MONTHLY_REVENUE_SQL)


def top_products(client):
    return run(client, TOP_PRODUCTS_SQL)


def revenue_by_region(client):
    return run(client, REVENUE_BY_REGION_SQL)


def repeat_purchase_rate(client):
    return run(client, REPEAT_PURCHASE_RATE_SQL)
