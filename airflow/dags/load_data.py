from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import csv
import os

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

CSV_FILE_PATH = '/opt/airflow/dags/data/input_data.csv'
BATCH_SIZE = 100
TARGET_TABLE = 'sentiment_social'  # 👈 Chính thức dùng bảng sentiment_social

def load_batch_to_postgres():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432"
    )
    cursor = conn.cursor()

    # Track progress
    checkpoint_file = '/opt/airflow/dags/data/checkpoint.txt'
    last_position = 0

    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            last_position = int(f.read().strip())

    rows_to_insert = []
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

        # Determine batch
        batch_rows = all_rows[last_position:last_position + BATCH_SIZE]

        for row in batch_rows:
            rows_to_insert.append((
                row['id'],
                row['name'],
                row['date'],
                row['title'],
                row['content'],
                row['sentiment_score']
            ))

    # Insert batch into PostgreSQL
    if rows_to_insert:
        for record in rows_to_insert:
            cursor.execute(
                f"""
                INSERT INTO {TARGET_TABLE} (id, name, date, title, content, sentiment_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE 
                    SET name = EXCLUDED.name,
                        date = EXCLUDED.date,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        sentiment_score = EXCLUDED.sentiment_score;
                """,
                record
            )

        conn.commit()

        # Update checkpoint
        new_position = last_position + len(batch_rows)
        with open(checkpoint_file, 'w') as f:
            f.write(str(new_position))

    cursor.close()
    conn.close()

with DAG(
    dag_id='csv_to_postgres_batch_etl',
    default_args=default_args,
    description='Load CSV to sentiment_social table in batches of 100 rows every 5 minutes',
    start_date=datetime(2024, 1, 1),
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    catchup=False,
    tags=['csv', 'postgres', 'batch'],
) as dag:

    load_batch_task = PythonOperator(
        task_id='load_batch_to_postgres',
        python_callable=load_batch_to_postgres
    )
