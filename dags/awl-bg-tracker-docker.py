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

# TODO: this method must be in the utils/ subfolder (i.e. inside dags/)
def airbyte_create_connection():
    # TODO: create a conn with that
    airbyte_conf = {
        'airbyte_host': "localhost",
        'airbyte_port': 8888,
        'airbyte_ssl': False,
        'airbyte_email': "gabrielmelocomp@gmail.com"
    }
    airbyte_conf['airbyte_url'] = "".join(["https://" if airbyte_conf['airbyte_ssl'] else "http://", airbyte_conf["airbyte_host"], ":", str(airbyte_conf["airbyte_port"])]),

    def source_exists(conf):
        list_sources_endpoint = "/api/v1/sources/list"
        list_sources_url = conf["airbyte_url"] + list_sources_endpoint
        sources = requests.post(list_sources_url, headers={'Content-Type': "application/json"})
        response = sources.json()
        sourceId = list(filter(lambda x: x["name"] == dag.dag_id, response.get("sources")))[0].get("sourceId")
        return sourceId

    def get_workspace_id_by_email(conf):
        list_workspaces_endpoint = "/api/v1/workspaces/list"
        list_workspaces_url = conf["airbyte_url"] + list_workspaces_endpoint
        workspaces = requests.post(list_workspaces_url, headers={'Content-Type': "application/json"})
        response = workspaces.json()
        workspace_id = list(filter(lambda x: x["email"] == conf["airbyte_email"], response.get("workspaces")))[0].get("workspaceId")
        return workspace_id

    def get_source_definition_id_by_repository(conf):
        list_source_definitions_endpoint = "/api/v1/source_definitions/list"
        list_source_definitions_url = conf["airbyte_url"] + list_source_definitions_endpoint
        source_definitions = requests.post(list_source_definitions_url, headers={'Content-Type': "application/json"})
        response = source_definitions.json()
        source_definition_id = \
            list(
                filter(lambda x: x["dockerRepository"] == "airbyte/source-mongodb", response.get("sourceDefinitions")))[
                0].get(
                "sourceDefinitionId")
        return source_definition_id

    def createSourceMongo(conf, workspace_id, source_definition_id, database, user, password, source_name="Mongo DB",
                          ssl=False, host="localhost", port="27017", auth_source="admin", replica_set=""):
        connection_configuration = {
            "ssl": ssl,
            "host": host,
            "port": port,
            "user": user,
            "database": database,
            "password": password,
            "auth_source": auth_source,
            "replica_set": replica_set
        }

        body = {
            "sourceDefinitionId": source_definition_id,
            "workspaceId": workspace_id,
            "connectionConfiguration": connection_configuration,
            "name": dag.dag_id,
            "sourceName": source_name
        }

        create_sources_endpoint = "/api/v1/sources/create"
        create_sources_url = conf["airbyte_url"] + create_sources_endpoint

        source_creation = requests.post(create_sources_url, body=body, headers={'Content-Type': "application/json"})
        response = source_creation.json()
        print(response)

    if not source_exists(airbyte_conf):
        # get workspace id
        workspace_id = get_workspace_id_by_email(airbyte_conf)
        # get source_definition id
        source_definition_id = get_source_definition_id_by_repository(airbyte_conf)
        # create source
        createSourceMongo(
            airbyte_conf,
            workspace_id=workspace_id,
            source_definition_id=source_definition_id,
            database="ods",
            # TODO: credentials must be in "vault"
            user="root",
            password="********"
        )


t2 = PythonOperator(
    task_id="airbyte_create_connection",
    python_callable=airbyte_create_connection,
    dag=dag
)

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

t1 >> t2 >> t3 >> t4
