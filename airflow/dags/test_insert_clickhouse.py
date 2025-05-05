from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from clickhouse_driver import Client

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def insert_clickhouse_sample():
    client = Client(
        host='clickhouse',
        port=9000,
        user='clickhouse',
        password='clickhouse'
    )
    client.execute("""
        INSERT INTO sentiment_summary (sentiment_score, count)
        VALUES (10, 100)
    """)
    print("✅ Inserted test record into ClickHouse.")

with DAG(
    dag_id='test_insert_clickhouse_only',
    default_args=default_args,
    description='Test insert into ClickHouse only',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once',
    catchup=False,
    tags=['clickhouse', 'test'],
) as dag:

    insert_ch = PythonOperator(
        task_id='insert_into_clickhouse',
        python_callable=insert_clickhouse_sample
    )
