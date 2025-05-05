from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def setup_cdc_postgres():
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Tạo user nếu chưa có
    cur.execute("""
        DO $$
        BEGIN
           IF NOT EXISTS (
              SELECT FROM pg_catalog.pg_roles WHERE rolname = 'debezium'
           ) THEN
              CREATE ROLE debezium WITH LOGIN PASSWORD 'debezium';
              ALTER ROLE debezium WITH REPLICATION;
           END IF;
        END
        $$;
    """)

    # 2. Tạo publication nếu chưa có
    cur.execute("""
        DO $$
        BEGIN
           IF NOT EXISTS (
              SELECT FROM pg_publication WHERE pubname = 'sentiment_pub'
           ) THEN
              CREATE PUBLICATION sentiment_pub FOR TABLE sentiment_social;
           END IF;
        END
        $$;
    """)

    print("✅ CDC setup for PostgreSQL completed.")

    cur.close()
    conn.close()

with DAG(
    dag_id='init_postgres_cdc',
    default_args=default_args,
    description='Create user and publication for PostgreSQL CDC',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once',
    catchup=False,
    tags=['cdc', 'postgres'],
) as dag:

    cdc_task = PythonOperator(
        task_id='setup_postgres_cdc',
        python_callable=setup_cdc_postgres
    )
