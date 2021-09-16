from datetime import datetime, timedelta
import json
import logging
import os
import requests
import time

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from pymongo import MongoClient

from lib.Airbyte import AirbyteAPI
from lib.utils import (update_json)

minio_conn = BaseHook.get_connection("minio")
mongodb_conn = BaseHook.get_connection("mongodb")

default_args = {
    'owner': 'gabrielmelocomp',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'start_date': days_ago(1),
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    '01_mi-data',
    default_args=default_args,
    description='',
    schedule_interval='0 */4 * * *',
    catchup=False
)

dag_clean_name = dag.dag_id[3:]

t1 = DockerOperator(
    task_id='crawler_container',
    image='gabrielmmelo/extractor-sqlite:latest',
    network_mode="host",
    environment={
        # "MONGODB_HOST": "host.docker.internal",
        # "MONGODB_PORT": 27017,
        # "MONGODB_DOCUMENTS_TTL": 259200,  # in seconds
        # "MONGODB_TIMEZONE": "America/Sao_Paulo",
        "S3_ACCESS_KEY_ID": minio_conn.login,
        "S3_SECRET_ACCESS_KEY": minio_conn.password,
        "S3_SSL_ENABLED": "0",
        "S3_HOST": minio_conn.host,
        "S3_PORT": minio_conn.port,
        "S3_BUCKET_NAME": "landing",
        "S3_FILE_PATH": "midata/bkp.db",
        "SQLITE_QUERY": "SELECT * FROM MI_BAND_ACTIVITY_SAMPLE",
        "MONGODB_DB": dag_clean_name,
        "MONGODB_COLLECTION": dag_clean_name
    },
    do_xcom_push=False,
    dag=dag
)


def airbyte_create_connection(**kwargs):
    ab = AirbyteAPI(
        host="host.docker.internal",
        port=8000,
        ssl=False
    )

    workspace_id = ab.get_workspace_id_by_email("gabrielmelocomp@gmail.com")
    logging.debug("Workspace ID: " + workspace_id)

    logging.info("Checking if source already exists...")
    source_id = ab.get_source_by_name(workspace_id=workspace_id, source_name=str(dag_clean_name))
    if not source_id:
        logging.info("Creating new source...")
        source_definition_id = ab.get_source_definition_id_by_repository(repository="airbyte/source-mongodb")
        logging.debug("Source Definition ID: " + source_definition_id)

        with open('dags/connections/sourceMongoDb.json', 'r') as f:
            connection_configuration = json.loads(f.read())["connectionConfiguration"]
            logging.debug("Connection Configuration:")
            logging.debug(connection_configuration)

        connection_configuration = update_json(
            json=connection_configuration,
            database=dag_clean_name,
            user=mongodb_conn.login,
            password=mongodb_conn.password
        )

        source_id = ab.create_source(
            name=dag_clean_name,
            workspace_id=workspace_id,
            source_definition_id=source_definition_id,
            connection_configuration=connection_configuration
        )
    else:
        logging.info("Source already exists.")

    logging.info("Checking if destination already exists...")
    destination_id = ab.get_destination_by_name(workspace_id=workspace_id, destination_name=str(dag_clean_name))
    if not destination_id:
        logging.info("Creating new destination...")
        destination_definition_id = ab.get_destination_definition_id_by_repository(repository="airbyte/destination-s3")
        logging.debug("Destination Definition ID: " + destination_definition_id)

        with open('dags/connections/destinationMinIO.json', 'r') as f:
            connection_configuration = json.loads(f.read())["connectionConfiguration"]
            logging.debug("Connection Configuration:")
            logging.debug(connection_configuration)

        connection_configuration = update_json(
            json=connection_configuration,
            access_key_id=minio_conn.login,
            secret_access_key=minio_conn.password
        )

        destination_id = ab.create_destination(
            name=dag_clean_name,
            workspace_id=workspace_id,
            destination_definition_id=destination_definition_id,
            connection_configuration=connection_configuration
        )
    else:
        logging.info("Destination already exists.")

    logging.info("Checking if connection already exists...")
    connection_id = ab.get_connection_by_source_and_destination(workspace_id=workspace_id, source_id=source_id, destination_id=destination_id)
    if not connection_id:
        logging.info("Creating new connection...")
        with open('dags/connections/connectionTemplate.json', 'r') as f:
            configuration_template = json.loads(f.read())
            logging.debug("Connection template:")
            logging.debug(configuration_template)

        # TODO: create utils function to fill the template, instead of doing that in create_connection function
        # configuration_template = fill_json(configuration_template)

        source_stream = ab.get_source_stream(source_id=source_id)

        connection_id = ab.create_connection(
            source_stream=source_stream,
            source_id=source_id,
            destination_id=destination_id,
            configuration_template=configuration_template
        )
    else:
        logging.info("Connection already exists.")

    # kwargs['ti'].xcom_push(key='connection_id', value=connection_id)
    return connection_id


def airbyte_trigger_sync(**kwargs):
    ti = kwargs['ti']
    connection_id = ti.xcom_pull(task_ids='airbyte_create_connection')

    ab = AirbyteAPI(
        host="host.docker.internal",
        port=8000,
        ssl=False
    )

    job_id = ab.sync_connection(connection_id=connection_id)
    logging.info(job_id)

    job_status = ab.get_job_status(job_id)
    while job_status != "succeeded":
        logging.info("Job Status: " + job_status)
        time.sleep(5)
        job_status = ab.get_job_status(job_id)

    logging.info("Job Status: " + job_status)

def mongodb_cleanup():
    client = MongoClient(mongodb_conn.host, mongodb_conn.port)
    client.drop_database(dag_clean_name)


t2 = PythonOperator(
    task_id="airbyte_create_connection",
    python_callable=airbyte_create_connection,
    dag=dag
)

t3 = PythonOperator(
    task_id="airbyte_trigger_sync",
    python_callable=airbyte_trigger_sync,
    provide_context=True,
    dag=dag
)

t4 = PythonOperator(
    task_id="mongodb_cleanup",
    python_callable=mongodb_cleanup,
    dag=dag
)

t1 >> t2 >> t3 >> t4
