from datetime import datetime, timedelta

import requests

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago

project_home = Variable.get("PROJECT_HOME")

default_args = {
    'owner': 'gabrielmelocomp',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'start_date': days_ago(2),
    'retries': 1,
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
        "MONGODB_HOST": "host.docker.internal",
        "MONGODB_PORT": 27017,
        "MONGODB_DB": "middleware",
        "MONGODB_DOCUMENTS_TTL": 259200,  # in seconds
        "MONGODB_TIMEZONE": "America/Sao_Paulo",
        "MONGODB_COLLECTION": dag.dag_id
    },
    dag=dag
)


def airbyte_api():
    # TODO: create a conn with that
    airbyte_conf = {
        'airbyte_host': "localhost",
        'airbyte_port': 8000,
        'airbyte_ssl': False,
        'airbyte_email': "gabrielmelocomp@gmail.com"
    }
    airbyte_conf['airbyte_url'] = "".join(["https://" if airbyte_conf['airbyte_ssl'] else "http://", airbyte_conf["airbyte_host"], ":", str(airbyte_conf["airbyte_port"])]),

    def get_workspace_id_by_email(conf):
        list_workspaces_endpoint = "/api/v1/workspaces/list"
        list_workspaces_url = conf["airbyte_url"] + list_workspaces_endpoint
        workspaces = requests.post(list_workspaces_url, headers={'Content-Type': "application/json"})
        response = workspaces.json()
        workspace_id = list(filter(lambda x: x["email"] == conf["airbyte_email"], response.get("workspaces")))[0].get("workspaceId")
        return workspace_id

    get_workspace_id_by_email(airbyte_conf)

    # get source definition id by repo
    list_source_definitions_endpoint = "/api/v1/source_definitions/list"
    list_source_definitions_url = airbyte_url + list_source_definitions_endpoint
    source_definitions = requests.post(list_source_definitions_url, headers={'Content-Type': "application/json"})
    response = source_definitions.json()
    source_definition_id = \
        list(filter(lambda x: x["dockerRepository"] == "airbyte/source-mongodb", response.get("sourceDefinitions")))[
            0].get(
            "sourceDefinitionId")

    # get create a new source
    """ pattern para mongodb: 
    {
  "sourceDefinitionId": "487b930d-7f6a-43ce-8bac-46e6b2de0a55",
  "sourceId": "90fd0a52-8440-401a-956f-83e5133cce7d",
  "workspaceId": "b17bdf4f-1e30-4574-990a-c0df68fe506c",
  "connectionConfiguration": {
    "ssl": false,
    "host": "localhost",
    "port": 27017,
    "user": "root",
    "database": "ods",
    "password": "**********",
    "auth_source": "admin",
    "replica_set": ""
  },
  "name": "test-source-mongodb",
  "sourceName": "Mongo DB"
}
    """
    pass


t3 = PythonOperator(
    task_id="aitbyte_api",
    python_callable=airbyte_api,
    dag=dag
)

t1 = PythonOperator(
)

t1
