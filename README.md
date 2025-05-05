
# 📊 Real-time & Batch Data Platform with FastAPI, PostgreSQL, ClickHouse, Kafka, and Airflow

## 🧩 Mục tiêu dự án

Dự án mô phỏng một hệ thống backend thực tế, nơi:

- **PostgreSQL** đóng vai trò là cơ sở dữ liệu chính, lưu trữ dữ liệu transactional.
- **ClickHouse** là hệ cơ sở dữ liệu phân tích, được dùng để **tính toán trước** các thống kê phức tạp và tăng tốc độ truy vấn.
- **Kafka** đảm nhiệm **luồng dữ liệu realtime** giữa PostgreSQL và ClickHouse.
- **Airflow** mô phỏng **batch processing**, ví dụ như ETL theo lịch định kỳ.
- **FastAPI** là backend chính, cung cấp các API để truy vấn từ cả PostgreSQL và ClickHouse.

## 🛠️ Công nghệ sử dụng

| Thành phần                           | Vai trò chính                                            |
| ------------------------------------ | -------------------------------------------------------- |
| **FastAPI**                          | Xây dựng API layer kết nối với PostgreSQL và ClickHouse  |
| **PostgreSQL**                       | Lưu trữ dữ liệu chính (Transactional DB)                 |
| **ClickHouse**                       | Truy vấn phân tích hiệu suất cao (OLAP DB)               |
| **Kafka + Kafka Connect + Debezium**| Gửi CDC (Change Data Capture) từ PostgreSQL → ClickHouse |
| **Airflow**                          | Quản lý pipeline batch (giả lập dữ liệu hàng loạt)       |
| **Docker Compose**                   | Orchestration cho toàn bộ hệ thống                       |

## ⚙️ Kiến trúc hệ thống

```

+-------------+         +-------------+          +--------------+
\| PostgreSQL  | ─────►  |   Kafka     | ─────►   |  ClickHouse   |
\| (Main Data) |   CDC   | + Debezium  |          | (Analytics DB)|
+-------------+         +-------------+          +--------------+
▲                                               ▲
│                                               │
└─── FastAPI ───── Query & API ────────────────┘
│
▼
External User

````

## 🚀 Khởi chạy hệ thống

```bash
docker-compose up --build
````

Dịch vụ sẽ được khởi chạy trên các cổng:

* FastAPI: `http://localhost:8000`
* Airflow: `http://localhost:8080`
* Kafka Connect: `http://localhost:8083`
* PostgreSQL: `localhost:5432`
* ClickHouse: `http://localhost:8123`

## 📌 Ghi chú quan trọng

* FastAPI **phải truy cập được cả PostgreSQL và ClickHouse**, do đó driver `clickhouse-connect` và `psycopg2` đã được cài trong container.
* Debezium được cấu hình qua Kafka Connect, giúp tự động **lấy các thay đổi từ PostgreSQL** và đẩy qua Kafka.
* Airflow sử dụng SQLite cho đơn giản, mô phỏng chạy batch pipeline.

## 🛠️ Một số lệnh cần chạy tay
- CREATE USER debezium WITH PASSWORD 'debezium';
- GRANT CONNECT ON DATABASE postgres TO debezium;
- GRANT USAGE ON SCHEMA public TO debezium;
- GRANT SELECT ON TABLE sentiment_social TO debezium;
- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium;
      