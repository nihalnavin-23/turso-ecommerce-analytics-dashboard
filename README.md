# 📊 E-Commerce Analytics Dashboard (Turso + Streamlit)

An end-to-end analytics project: simulated e-commerce order data is generated with Python, stored in **Turso** (a distributed, SQLite-compatible edge database), queried with analytical SQL (including window functions), and visualized in a live **Streamlit** dashboard — with a built-in natural-language "Ask a question" feature.

Built to demonstrate the full data analyst workflow: schema design → data pipeline → SQL analysis → visualization → insight delivery, using a modern cloud database instead of a static CSV.

## 🔗 Live Demo

*(add your Streamlit Community Cloud link here once deployed)*

## ✨ Features

- **Live dashboard** — monthly revenue trend (with best month auto-highlighted), top 10 products, revenue by region
- **Natural-language Q&A tab** — ask things like *"Which month had the highest sales?"* or *"Who are the top customers?"* and get an instant answer computed live from the database
- **Real analytical SQL** — aggregations, joins, CTEs, and a `ROW_NUMBER() OVER (PARTITION BY ...)` window function for customer order sequencing and repeat-purchase rate
- **Cloud-hosted data** — all data lives in Turso (libSQL), not a local file, queried live over the network

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Database | Turso (libSQL / SQLite-compatible) |
| Data generation | Python + Faker |
| Analytics | SQL (aggregations, joins, CTEs, window functions) |
| Dashboard | Streamlit + Plotly |
| Secrets management | python-dotenv |

## 📁 Project Structure

...
