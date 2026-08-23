"""
Creates the schema and populates it with simulated e-commerce data
in a Turso (libSQL) database.

Uses TURSO_DATABASE_URL / TURSO_AUTH_TOKEN env vars if set, otherwise
falls back to a local file `local.db` so you can build/test without
a Turso account first.
"""

import os
import random
from datetime import datetime, timedelta

import libsql_client
from faker import Faker

fake = Faker()

DB_URL = os.environ.get("TURSO_DATABASE_URL", "file:local.db")
AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

CATEGORIES = ["Electronics", "Home & Kitchen", "Books", "Clothing", "Sports", "Beauty"]
REGIONS = ["North", "South", "East", "West", "Central"]

N_CUSTOMERS = 500
N_PRODUCTS = 40
N_ORDERS = 3000
DAYS_BACK = 365


def get_client():
    if AUTH_TOKEN:
        return libsql_client.create_client_sync(url=DB_URL, auth_token=AUTH_TOKEN)
    return libsql_client.create_client_sync(url=DB_URL)


def create_schema(client):
    with open("schema.sql") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    for stmt in statements:
        client.execute(stmt)
    print("Schema created.")


def seed_customers(client):
    rows = []
    for _ in range(N_CUSTOMERS):
        signup = fake.date_between(start_date=f"-{DAYS_BACK}d", end_date="today")
        rows.append((fake.name(), fake.email(), random.choice(REGIONS), signup.isoformat()))

    for batch_start in range(0, len(rows), 100):
        batch = rows[batch_start:batch_start + 100]
        stmts = [
            libsql_client.Statement(
                "INSERT INTO customers (name, email, region, signup_date) VALUES (?, ?, ?, ?)",
                r,
            )
            for r in batch
        ]
        client.batch(stmts)
    print(f"Inserted {len(rows)} customers.")


def seed_products(client):
    rows = []
    for _ in range(N_PRODUCTS):
        category = random.choice(CATEGORIES)
        name = f"{fake.word().capitalize()} {category[:-1] if category.endswith('s') else category}"
        price = round(random.uniform(9.99, 499.99), 2)
        rows.append((name, category, price))

    stmts = [
        libsql_client.Statement(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)", r
        )
        for r in rows
    ]
    client.batch(stmts)
    print(f"Inserted {len(rows)} products.")


def seed_orders(client, n_customers, n_products):
    today = datetime.today()
    rows = []
    for _ in range(N_ORDERS):
        customer_id = random.randint(1, n_customers)
        product_id = random.randint(1, n_products)
        order_date = today - timedelta(days=random.randint(0, DAYS_BACK))
        quantity = random.randint(1, 5)
        rows.append((customer_id, product_id, order_date.date().isoformat(), quantity))

    # look up product prices to compute total_amount realistically
    price_rows = client.execute("SELECT product_id, price FROM products").rows
    price_map = {r[0]: r[1] for r in price_rows}

    stmts = []
    for customer_id, product_id, order_date, quantity in rows:
        total = round(price_map[product_id] * quantity, 2)
        stmts.append(
            libsql_client.Statement(
                "INSERT INTO orders (customer_id, product_id, order_date, quantity, total_amount) "
                "VALUES (?, ?, ?, ?, ?)",
                (customer_id, product_id, order_date, quantity, total),
            )
        )

    for batch_start in range(0, len(stmts), 200):
        client.batch(stmts[batch_start:batch_start + 200])
    print(f"Inserted {len(stmts)} orders.")


def main():
    client = get_client()
    create_schema(client)
    seed_customers(client)
    seed_products(client)
    seed_orders(client, N_CUSTOMERS, N_PRODUCTS)
    client.close()
    print(f"Done. Data written to: {DB_URL}")


if __name__ == "__main__":
    main()
