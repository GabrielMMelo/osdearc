from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago


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
    volumes=['/opt/airflow/certs/CAs:/usr/src/app/mkcert'],
    network_mode="host",
    environment={
        'MINIO_BUCKET': 'lake',
        'MINIO_FOLDER_TARGET': 'dev/01_raw/awl_bg_prices/',
        'AWS_CA_BUNDLE': '/usr/src/app/mkcert/rootCA.pem',

    },
    dag=dag
)

t1
