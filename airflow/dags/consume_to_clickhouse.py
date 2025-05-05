from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import psycopg2
from clickhouse_driver import Client
from kafka import KafkaConsumer

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def consume_and_aggregate_to_clickhouse():
    # Kafka consumer với timeout để task không treo mãi
    consumer = KafkaConsumer(
        'dbserver1.public.sentiment_social',
        bootstrap_servers='kafka:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='clickhouse-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000  # ⏰ 5 giây không có msg sẽ kết thúc vòng lặp
    )

    pg_conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432"
    )
    pg_cursor = pg_conn.cursor()

    ch_client = Client(host='clickhouse', user='clickhouse', password='clickhouse', port=9000)

    found = False

    for msg in consumer:
        payload = msg.value

        if payload.get('op') in ['c', 'u', 'r'] and payload.get('after'):
            print("🔄 CDC event received → Aggregating from PostgreSQL...")

            pg_cursor.execute("""
                SELECT sentiment_score, COUNT(*) 
                FROM sentiment_social 
                GROUP BY sentiment_score
            """)
            result = pg_cursor.fetchall()

            ch_client.execute("TRUNCATE TABLE sentiment_summary")
            ch_client.execute(
                "INSERT INTO sentiment_summary (sentiment_score, count) VALUES",
                result
            )

            print("✅ Updated ClickHouse with:", result)
            found = True
            break

    if not found:
        print("⚠️ No new insert/update messages found during this execution.")

    pg_cursor.close()
    pg_conn.close()

with DAG(
    dag_id='consume_kafka_to_clickhouse',
    default_args=default_args,
    description='Consume Kafka CDC events and update ClickHouse aggregation',
    start_date=datetime(2024, 1, 1),
    schedule_interval='* * * * *',
    catchup=False,
    tags=['kafka', 'clickhouse', 'cdc'],
) as dag:

    consume_task = PythonOperator(
        task_id='consume_and_insert',
        python_callable=consume_and_aggregate_to_clickhouse
    )
