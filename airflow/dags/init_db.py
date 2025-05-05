from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
from clickhouse_driver import Client  # pip install clickhouse-driver

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def create_postgres_table_if_not_exists():
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432"
    )
    cursor = conn.cursor()
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
        print("✅ Table sentiment_social already exists.")

    cursor.close()
    conn.close()

def create_clickhouse_summary_table():
    client = Client(host='clickhouse', user='clickhouse', password='clickhouse', port=9000)
    client.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_summary (
            sentiment_score Int32,
            count UInt64
        ) ENGINE = MergeTree()
        ORDER BY sentiment_score;
    ''')
    print("✅ Created (or verified) ClickHouse table sentiment_summary.")

with DAG(
    dag_id='init_postgres_clickhouse_tables',
    default_args=default_args,
    description='Init PostgreSQL + ClickHouse tables',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once',
    catchup=False,
    tags=['postgres', 'clickhouse', 'init'],
) as dag:

    create_pg_task = PythonOperator(
        task_id='create_sentiment_social_pg',
        python_callable=create_postgres_table_if_not_exists
    )

    create_ch_task = PythonOperator(
        task_id='create_sentiment_summary_ch',
        python_callable=create_clickhouse_summary_table
    )

    create_pg_task >> create_ch_task
