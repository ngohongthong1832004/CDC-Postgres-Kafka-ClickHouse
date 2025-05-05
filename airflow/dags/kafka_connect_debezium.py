from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def create_debezium_connector():
    # First check if the connector plugin is available
    response = requests.get("http://kafka-connect:8083/connector-plugins")
    
    if response.status_code == 200:
        plugins = response.json()
        debezium_installed = any(plugin["class"] == "io.debezium.connector.postgresql.PostgresConnector" for plugin in plugins)
        
        if not debezium_installed:
            print("⚠️ Debezium PostgreSQL connector not installed. Please install it first.")
            return
    
    connector_config = {
        "name": "debezium-postgres-connector",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": "postgres",
            "database.port": "5432",
            "database.user": "debezium",
            "database.password": "debezium",
            "database.dbname": "postgres",
            "database.server.name": "dbserver1",
            "topic.prefix": "dbserver1",  
            "plugin.name": "pgoutput",
            "table.include.list": "public.sentiment_social",
            "publication.name": "sentiment_pub",
            "slot.name": "debezium_slot",
            "tombstones.on.delete": "false",
            "include.schema.changes": "false"
        }
    }

    response = requests.post(
        "http://kafka-connect:8083/connectors",
        headers={"Content-Type": "application/json"},
        data=json.dumps(connector_config)
    )

    if response.status_code in (200, 201):
        print("✅ Debezium connector created successfully.")
    elif response.status_code == 409:
        print("ℹ️ Connector already exists.")
    else:
        raise Exception(f"❌ Failed to create connector: {response.text}")

with DAG(
    dag_id='create_debezium_connector',
    default_args=default_args,
    description='Create Debezium PostgreSQL CDC connector',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@once',
    catchup=False,
    tags=['cdc', 'debezium'],
) as dag:

    create_connector_task = PythonOperator(
        task_id='create_connector',
        python_callable=create_debezium_connector
    )
