"""
SQL queries for the Turso analytics dashboard.
"""

import os

from libsql_client import Client, create_client


def get_client() -> Client:
    """Create and return a Turso client."""
    url = os.environ.get("TURSO_DB_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")
    
    if not url:
        raise ValueError("TURSO_DB_URL environment variable is required")
    
    return create_client(url, auth_token=auth_token)


def monthly_revenue(client: Client):
    """Get monthly revenue and order counts."""
    sql = """
        SELECT 
            strftime('%Y-%m', order_date) as month,
            SUM(total_amount) as revenue,
            COUNT(DISTINCT order_id) as num_orders
        FROM orders
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month
    """
    result = client.execute(sql)
    return result.columns, result.rows


def top_products(client: Client, limit: int = 10):
    """Get top products by revenue."""
    sql = f"""
        SELECT 
            p.name,
            p.category,
            SUM(oi.quantity * oi.price) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY oi.product_id
        ORDER BY revenue DESC
        LIMIT {limit}
    """
    result = client.execute(sql)
    return result.columns, result.rows


def revenue_by_region(client: Client):
    """Get revenue breakdown by region."""
    sql = """
        SELECT 
            c.region,
            SUM(o.total_amount) as revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY revenue DESC
    """
    result = client.execute(sql)
    return result.columns, result.rows


def repeat_purchase_rate(client: Client):
    """Calculate the repeat purchase rate."""
    sql = """
        WITH customer_orders AS (
            SELECT 
                customer_id,
                COUNT(*) as order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT 
            CAST(
                COUNT(CASE WHEN order_count > 1 THEN 1 END) AS FLOAT
            ) / COUNT(*) as repeat_rate
        FROM customer_orders
    """
    result = client.execute(sql)
    return result.columns, result.rows
