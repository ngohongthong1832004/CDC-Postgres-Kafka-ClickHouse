from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def create_postgres_table_if_not_exists():
    conn = psycopg2.connect(
        database="postgres",   # chú ý: database đúng
        user="postgres",       # chú ý: user đúng
        password="postgres",   # chú ý: password đúng
        host="postgres",
        port="5432"
    )
    cursor = conn.cursor()

    # Kiểm tra nếu bảng sentiment_social chưa tồn tại thì tạo
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'sentiment_social'
        );
    """)
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute("""
            CREATE TABLE sentiment_social (
                id BIGINT PRIMARY KEY,
                name TEXT,
                date TIMESTAMPTZ,
                title TEXT,
                content TEXT,
                sentiment_score INT
            );
        """)
        conn.commit()
        print("✅ Created table sentiment_social.")
    else:
        print("✅ Table sentiment_social already exists, no action needed.")

    cursor.close()
    conn.close()

with DAG(
    dag_id='init_postgres_table',
    default_args=default_args,
    description='Create sentiment_social table if not exists in PostgreSQL',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once',  # Chạy đúng 1 lần khi enable DAG
    catchup=False,
    tags=['postgres', 'init'],
) as dag:

    create_table_task = PythonOperator(
        task_id='create_sentiment_social_if_not_exists',
        python_callable=create_postgres_table_if_not_exists
    )
