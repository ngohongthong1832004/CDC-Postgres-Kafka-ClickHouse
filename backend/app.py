from fastapi import FastAPI, Query
from typing import Optional
import psycopg2
from clickhouse_driver import Client

app = FastAPI()

# Kết nối đến PostgreSQL
pg_conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="postgres",  # Hoặc "localhost" nếu chạy local
    port="5432"
)

# Kết nối đến ClickHouse
clickhouse_client = Client(
    host='clickhouse',
    user='clickhouse',
    password='clickhouse',
    port=9000
)

@app.get("/posts")
def get_posts(
    limit: int = Query(10, description="Số lượng tối đa record trả về"),
    name: Optional[str] = Query(None, description="Tên cần tìm kiếm (nếu có)")
):
    cur = pg_conn.cursor()

    if name:
        query = "SELECT * FROM sentiment_social WHERE name ILIKE %s LIMIT %s;"
        cur.execute(query, (f"%{name}%", limit))
    else:
        query = "SELECT * FROM sentiment_social LIMIT %s;"
        cur.execute(query, (limit,))

    rows = cur.fetchall()
    cur.close()

    # Chuyển về list[dict] để trả JSON dễ đọc
    return [
        {
            "id": r[0],
            "name": r[1],
            "date": r[2],
            "title": r[3],
            "content": r[4],
            "sentiment_score": r[5],
        }
        for r in rows
    ]

@app.get("/clickhouse/summary")
def get_summary():
    rows = clickhouse_client.execute("SELECT sentiment_score, count FROM sentiment_summary")
    return [
        {"sentiment_score": r[0], "count": r[1]}
        for r in rows
    ]
