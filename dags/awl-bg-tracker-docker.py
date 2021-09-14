from datetime import datetime, timedelta
import json
import logging
import os

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago

from lib.Airbyte import AirbyteAPI

project_home = Variable.get("PROJECT_HOME")

default_args = {
    'owner': 'gabrielmelocomp',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'start_date': days_ago(2),
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'awl-bg-tracker-docker',
    default_args=default_args,
    schedule_interval='0 */4 * * *',
    description='Track prices from a given Amazon Wishlist (aka. AWL), via webcrawler, and store it in a postgresql '
                'database. '
)

t1 = DockerOperator(
    task_id='crawler_container',
    image='gabrielmmelo/awl-crawler:latest',
    # volumes=[''.join([project_home, 'certs/CAs:/usr/src/app/mkcert'])],
    network_mode="host",
    environment={
        # "MONGODB_HOST": "host.docker.internal",
        # "MONGODB_PORT": 27017,
        # "MONGODB_DB": "middleware",
        # "MONGODB_DOCUMENTS_TTL": 259200,  # in seconds
        # "MONGODB_TIMEZONE": "America/Sao_Paulo",
        "MONGODB_COLLECTION": str(dag.dag_id)
    },
    do_xcom_push=False,
    dag=dag
)

def airbyte_create_connection():
    ab = AirbyteAPI(
        host="host.docker.internal",
        port=8000,
        ssl=False
    )

    logging.info("Getting workspace id by email")
    workspace_id = ab.get_workspace_id_by_email("gabrielmelocomp@gmail.com")
    logging.info("Workspace ID: " + workspace_id)

    if not ab.source_exists(workspace_id=workspace_id, source_name=str(dag.dag_id)):
        source_definition_id = ab.get_source_definition_id_by_repository(repository="airbyte/source-mongodb")
        logging.info("Source Definition ID: " + source_definition_id)

        with open('dags/connections/sourceMongoDb.json', 'r') as f:
            connection_configuration = json.loads(f.read())["connectionConfiguration"]
            # TODO: update connection_configuration password field with env var
            logging.info(connection_configuration)

        ab.create_source(
            name=dag.dag_id,
            workspace_id=workspace_id,
            source_definition_id=source_definition_id,
            connection_configuration=connection_configuration
        )
    else:
        pass


t2 = PythonOperator(
    task_id="airbyte_create_connection",
    python_callable=airbyte_create_connection,
    dag=dag
)

"""
t3 = PythonOperator(
    task_id="airbyte_trigger_sync",
    python_callable=airbyte_trigger_sync,
    dag=dag
)

t4 = PythonOperator(
    task_id="mongodb_cleanup",
    python_callable=mongodb_cleanup,
    dag=dag
)
"""

t1 >> t2 #>> t3 >> t4
