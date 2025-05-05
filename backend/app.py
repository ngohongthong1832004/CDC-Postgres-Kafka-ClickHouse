from fastapi import FastAPI, Query
import psycopg2
from clickhouse_driver import Client

app = FastAPI()

pg_conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="postgres", port="5432")
clickhouse_client = Client('clickhouse')

@app.get("/posts")
def get_posts(limit: int = Query(10, description="Số lượng tối đa record trả về"),
              name: str = Query(None, description="Tên cần tìm kiếm (nếu có)")):
    cur = pg_conn.cursor()

    if name:
        # Nếu có name: search by name và giới hạn limit
        query = "SELECT * FROM sentiment_social WHERE name ILIKE %s LIMIT %s;"
        cur.execute(query, (f"%{name}%", limit))
    else:
        # Nếu không có name: lấy tất cả limit bản ghi
        query = "SELECT * FROM sentiment_social LIMIT %s;"
        cur.execute(query, (limit,))

    rows = cur.fetchall()
    cur.close()
    return rows
    
@app.get("/clickhouse/metrics")
def get_metrics():
    result = clickhouse_client.execute("SELECT * FROM metrics_summary")
    return result
